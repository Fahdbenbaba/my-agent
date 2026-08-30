import os
import importlib
import inspect
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from models.ollama_client import OllamaClient
from skills.base_skill import BaseSkill
from agent.evidence_guard import EvidenceGuard


class AgentCore:
    """Core agent with skills, verified workflows, evidence controls, and persistent learning context."""

    MAX_TOOL_STEPS = 8
    MAX_HISTORY_MESSAGES = 12
    MAX_JOURNAL_ENTRIES = 12
    MAX_JOURNAL_CHARS = 32000

    SYSTEM_PROMPT = (
        "You are a helpful, friendly, conversational autonomous AI agent. "
        "Respond naturally and warmly to greetings and casual questions. "
        "Maintain continuity with recent conversation. Use tools when useful and call multiple tools in sequence. "
        "NEVER claim a tool action happened unless its actual result confirms success. "
        "For side effects, verify them with a follow-up tool when possible. "
        "If a tool fails, report the failure. Reply in the user's language or dialect. "
        "You have a skill_learning tool for continuous learning. After meaningful debugging discoveries, non-obvious workarounds, "
        "project-specific patterns, or verified tool integrations, consider extracting a reusable skill. "
        "Before creating a skill, search existing learned skills for duplicates. "
        "Never invent a fix, command, configuration, or verification result. "
        "Use the provided verified learning context as the source of truth. "
        "Never store credentials, tokens, passwords, private keys, or other secrets in learned skills. "
        "A learned skill must contain a precise trigger, reusable solution, and verification evidence."
    )

    def __init__(self, model_name="qwen3:1.7b"):
        self.model_name = model_name
        self.client = OllamaClient(model_name=model_name)
        self.skills = {}
        self.history = []
        self.execution_journal = []
        self._journal_path = Path(__file__).resolve().parent.parent / "agent_memory" / "learning_journal.jsonl"
        self._journal_path.parent.mkdir(parents=True, exist_ok=True)
        self._load_learning_journal()
        self._load_skills()

    @staticmethod
    def _redact(text: str, limit=6000) -> str:
        value = str(text or "")
        patterns = [
            r"(?i)(api[_ -]?key|client[_ -]?secret|access[_ -]?token|refresh[_ -]?token|password|authorization)\s*[:=]\s*[^\s]+",
            r"(?i)bearer\s+[A-Za-z0-9._~+/=-]+",
            r"-----BEGIN [A-Z ]+PRIVATE KEY-----.*?-----END [A-Z ]+PRIVATE KEY-----",
            r"(?i)ghp_[A-Za-z0-9]+",
            r"(?i)github_pat_[A-Za-z0-9_]+",
        ]
        for pattern in patterns:
            value = re.sub(pattern, "[REDACTED_SECRET]", value, flags=re.S)
        return value[:limit]

    def _load_learning_journal(self):
        if not self._journal_path.exists():
            return
        try:
            lines = self._journal_path.read_text(encoding="utf-8", errors="replace").splitlines()
            for line in lines[-self.MAX_JOURNAL_ENTRIES:]:
                try:
                    entry = json.loads(line)
                    text = str(entry.get("text", "")).strip()
                    if text:
                        self.execution_journal.append(text)
                except json.JSONDecodeError:
                    continue
        except OSError:
            pass

    def _persist_journal(self):
        try:
            records = [
                {"timestamp": datetime.now(timezone.utc).isoformat(), "text": self._redact(entry, 7000)}
                for entry in self.execution_journal[-self.MAX_JOURNAL_ENTRIES:]
            ]
            self._journal_path.write_text("\n".join(json.dumps(item, ensure_ascii=False) for item in records) + ("\n" if records else ""), encoding="utf-8")
        except OSError:
            pass

    def _load_skills(self):
        skills_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "skills")
        for filename in os.listdir(skills_dir):
            if not filename.endswith(".py") or filename in {"__init__.py", "base_skill.py"}:
                continue
            try:
                module = importlib.import_module(f"skills.{filename[:-3]}")
                for _, obj in inspect.getmembers(module, inspect.isclass):
                    if not issubclass(obj, BaseSkill) or obj is BaseSkill:
                        continue
                    skill = obj()
                    name = getattr(skill, "name", "")
                    if not name or not isinstance(getattr(skill, "description", None), str) or not isinstance(getattr(skill, "schema", None), dict):
                        raise ValueError(f"Invalid skill metadata: {filename}")
                    if name in self.skills:
                        raise ValueError(f"Duplicate skill name: {name}")
                    self.skills[name] = skill
            except Exception as e:
                print(f"Error loading skill {filename}: {e}")

    def clear_history(self):
        self.history.clear()
        self.execution_journal.clear()
        self._persist_journal()

    def _remember(self, role, content):
        if content:
            self.history.append({"role": role, "content": str(content)})
            self.history = self.history[-self.MAX_HISTORY_MESSAGES:]

    def _record_learning_context(self, kind, text):
        safe = self._redact(text)
        if not safe.strip():
            return
        self.execution_journal.append(f"{kind}:\n{safe}")
        self.execution_journal = self.execution_journal[-self.MAX_JOURNAL_ENTRIES:]
        self._persist_journal()

    def _record_execution(self, name, arguments, result):
        entry = (
            f"TOOL: {name}\n"
            f"ARGUMENTS: {json.dumps(arguments, ensure_ascii=False, default=str)}\n"
            f"RESULT:\n{str(result)[:6000]}"
        )
        self._record_learning_context("EXECUTION", entry)

    def _learning_evidence(self):
        if not self.execution_journal:
            return ""
        return "\n\n---\n\n".join(self.execution_journal)[-self.MAX_JOURNAL_CHARS:]

    def _tool_definitions(self):
        tools = []
        for skill in self.skills.values():
            schema = skill.schema
            tools.append(schema if "function" in schema else {"type": "function", "function": {"name": skill.name, "description": skill.description, "parameters": schema}})
        return tools

    @staticmethod
    def _normalize_arguments(arguments):
        if isinstance(arguments, dict):
            return arguments
        if isinstance(arguments, str):
            try:
                value = json.loads(arguments)
                return value if isinstance(value, dict) else {"query": arguments}
            except json.JSONDecodeError:
                return {"query": arguments}
        return {"query": str(arguments)}

    @staticmethod
    def _deterministic_web_answer(query, evidence):
        q = query.lower()
        if "python" not in q or not any(k in q for k in ("latest", "current", "release", "version")):
            return None
        match = re.search(r"VERIFIED_FACT:\s*Latest Python(?:\s+3)? release[^\n:]*:\s*Python\s+(3\.\d+\.\d+)", evidence, re.I)
        if not match:
            return None
        urls = re.findall(r"URL:\s*(https?://\S+)", evidence)
        source = next((u for u in urls if "python.org" in u.lower()), "https://www.python.org/")
        return f"The latest stable Python release is Python {match.group(1)}. Source: {source}"

    def _extract_url(self, text):
        match = re.search(r"https?://[^\s,)>]+", text)
        return match.group(0).rstrip(".,)") if match else None

    def _extract_txt_filename(self, text):
        match = re.search(r"\b([A-Za-z0-9_.-]+\.txt)\b", text, re.I)
        return match.group(1) if match else None

    def _execute_skill(self, name, arguments):
        if name not in self.skills:
            return f"Tool Error: Unknown tool '{name}'."
        try:
            if name == "skill_learning" and isinstance(arguments, dict) and str(arguments.get("action", "")).lower() == "save":
                arguments = dict(arguments)
                if not str(arguments.get("evidence", "")).strip():
                    evidence = self._learning_evidence()
                    if evidence:
                        arguments["evidence"] = evidence
                        arguments.setdefault("source", "verified execution journal")
            result = self.skills[name].execute(arguments)
            if name == "web_search":
                result = EvidenceGuard.filter_web_evidence(str(arguments.get("query", "")), str(result))
            self._record_execution(name, arguments, result)
            return str(result)
        except Exception as e:
            result = f"Tool Error in '{name}': {e}"
            self._record_execution(name, arguments, result)
            return result

    def _execute_tool_call(self, tool_call):
        function = tool_call.get("function", {}) if isinstance(tool_call, dict) else {}
        return self._execute_skill(function.get("name"), self._normalize_arguments(function.get("arguments", {})))

    def _run_verified_browser_file_workflow(self, query):
        q = query.lower()
        if "http" not in q or not any(x in q for x in ("go to", "open", "visit")):
            return None
        if not any(x in q for x in ("create a file", "create file", "save it to", "write it to")):
            return None
        url = self._extract_url(query)
        filename = self._extract_txt_filename(query)
        browser_name = "browser_automation" if "browser_automation" in self.skills else "browser"
        if not url or not filename or browser_name not in self.skills or "file_manager" not in self.skills:
            return None
        browser_result = self._execute_skill(browser_name, {"url": url, "action": "get_info"})
        if not browser_result.startswith("BROWSER_SUCCESS"):
            return f"Workflow failed: browser step did not succeed.\n{browser_result}"
        title_match = re.search(r"^TITLE:\s*(.+)$", browser_result, re.M)
        title = title_match.group(1).strip() if title_match else "Unknown"
        version_match = re.search(r"\bPython\s+(3\.\d+\.\d+)\b", browser_result, re.I)
        version = version_match.group(1) if version_match else None
        if "latest python release" in q and not version:
            return "Workflow failed verification: no Python release version was found on the loaded page."
        content = ((f"Python Version: {version}\n") if version else "") + f"Page Title: {title}"
        create_result = self._execute_skill("file_manager", {"action": "create", "filepath": filename, "content": content})
        if not create_result.startswith("File created successfully:"):
            return f"Workflow failed: file creation was not confirmed.\n{create_result}"
        read_result = self._execute_skill("file_manager", {"action": "read", "filepath": filename})
        if read_result != content:
            return f"Workflow failed verification: '{filename}' was not read back with the expected content."
        return f"Task completed and verified.\nPython version: {version or 'not found'}\nPage title: {title}\nFile created and verified: {filename}"

    def run(self, user_query: str) -> str:
        self._record_learning_context("USER_REQUEST", user_query)
        workflow = self._run_verified_browser_file_workflow(user_query)
        if workflow:
            self._remember("user", user_query)
            self._remember("assistant", workflow)
            return workflow

        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}, *self.history, {"role": "user", "content": user_query}]
        tools = self._tool_definitions()
        web_evidence_seen = False
        last_result = ""

        try:
            for _ in range(self.MAX_TOOL_STEPS):
                assistant_message = self.client.chat(messages, tools=tools)
                messages.append(assistant_message)
                tool_calls = assistant_message.get("tool_calls") or []
                if not tool_calls:
                    response = assistant_message.get("content", "").strip()
                    self._remember("user", user_query)
                    self._remember("assistant", response)
                    return response
                for tool_call in tool_calls:
                    result = self._execute_tool_call(tool_call)
                    last_result = result
                    function = tool_call.get("function", {})
                    name = function.get("name", "unknown")
                    if name == "skill_learning" and str(self._normalize_arguments(function.get("arguments", {})).get("action", "")).lower() == "save":
                        if result.startswith("SKILL_REJECTED") or result.startswith("SKILL_LEARNING_ERROR"):
                            self._remember("user", user_query)
                            self._remember("assistant", result)
                            return result
                    if name == "web_search":
                        web_evidence_seen = True
                        direct = self._deterministic_web_answer(user_query, result)
                        if direct:
                            self._remember("user", user_query)
                            self._remember("assistant", direct)
                            return direct
                    messages.append({"role": "tool", "content": result, "name": name})
                if web_evidence_seen:
                    messages.append({"role": "system", "content": EvidenceGuard.final_instruction(user_query, last_result)})

            final_message = self.client.chat(messages + [{"role": "system", "content": "Give the final answer naturally. Do not claim any unverified action succeeded."}])
            response = final_message.get("content", "").strip()
            self._remember("user", user_query)
            self._remember("assistant", response)
            return response
        except Exception as e:
            return f"Error: {e}"
