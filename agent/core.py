import os
import importlib
import inspect
import json
import re
from models.ollama_client import OllamaClient
from skills.base_skill import BaseSkill
from agent.evidence_guard import EvidenceGuard


class AgentCore:
    """Core agent loop with dynamic skill discovery, tool calling, and evidence controls."""

    MAX_TOOL_STEPS = 6

    def __init__(self, model_name="qwen3:1.7b"):
        self.model_name = model_name
        self.client = OllamaClient(model_name=model_name)
        self.skills = {}
        self._load_skills()

    def _load_skills(self):
        skills_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "skills")
        for filename in os.listdir(skills_dir):
            if not filename.endswith(".py") or filename in {"__init__.py", "base_skill.py"}:
                continue
            module_name = f"skills.{filename[:-3]}"
            try:
                module = importlib.import_module(module_name)
                for _, obj in inspect.getmembers(module, inspect.isclass):
                    if not issubclass(obj, BaseSkill) or obj is BaseSkill:
                        continue
                    skill_instance = obj()
                    skill_name = getattr(skill_instance, "name", "")
                    if not skill_name:
                        raise ValueError("Skill is missing required 'name' attribute")
                    if not isinstance(getattr(skill_instance, "description", None), str):
                        raise ValueError(f"Skill '{skill_name}' has invalid description")
                    if not isinstance(getattr(skill_instance, "schema", None), dict):
                        raise ValueError(f"Skill '{skill_name}' has invalid schema")
                    if skill_name in self.skills:
                        raise ValueError(f"Duplicate skill name: {skill_name}")
                    self.skills[skill_name] = skill_instance
            except Exception as e:
                print(f"Error loading skill {filename}: {e}")

    def _tool_definitions(self):
        tools = []
        for skill in self.skills.values():
            schema = skill.schema
            if "function" in schema:
                tools.append(schema)
            else:
                tools.append({"type": "function", "function": {"name": skill.name, "description": skill.description, "parameters": schema}})
        return tools

    @staticmethod
    def _normalize_arguments(arguments):
        if isinstance(arguments, dict):
            return arguments
        if isinstance(arguments, str):
            try:
                parsed = json.loads(arguments)
                return parsed if isinstance(parsed, dict) else {"query": arguments}
            except json.JSONDecodeError:
                return {"query": arguments}
        return {"query": str(arguments)}

    @staticmethod
    def _deterministic_web_answer(query: str, evidence: str):
        """Return a direct answer for verified current Python release facts."""
        q = query.lower()
        if not ("python" in q and any(k in q for k in ("latest", "current", "release", "version"))):
            return None
        match = re.search(r"VERIFIED_FACT:\s*Latest Python(?:\s+3)? release[^\n:]*:\s*Python\s+(3\.\d+\.\d+)", evidence, flags=re.IGNORECASE)
        if not match:
            return None
        version = match.group(1)
        urls = re.findall(r"URL:\s*(https?://\S+)", evidence)
        official_url = next((u for u in urls if "python.org" in u.lower()), "https://www.python.org/")
        return f"The latest stable Python release is Python {version}. Source: {official_url}"

    def _execute_tool_call(self, tool_call):
        function = tool_call.get("function", {}) if isinstance(tool_call, dict) else {}
        name = function.get("name")
        arguments = self._normalize_arguments(function.get("arguments", {}))
        if name not in self.skills:
            return f"Tool Error: Unknown tool '{name}'."
        try:
            result = self.skills[name].execute(arguments)
            if name == "web_search":
                query = arguments.get("query", "")
                result = EvidenceGuard.filter_web_evidence(str(query), result)
            return result
        except Exception as e:
            return f"Tool Error in '{name}': {e}"

    def run(self, user_query: str) -> str:
        messages = [
            {"role": "system", "content": (
                "You are an autonomous local AI agent. Use tools when useful. You may call "
                "multiple tools in sequence. After observing tool results, continue until the "
                "task is complete. Do not claim a tool was used unless you actually called it. "
                "Reply in the same language or dialect as the user."
            )},
            {"role": "user", "content": user_query},
        ]
        tools = self._tool_definitions()
        web_evidence_seen = False

        try:
            for _ in range(self.MAX_TOOL_STEPS):
                assistant_message = self.client.chat(messages, tools=tools)
                messages.append(assistant_message)
                tool_calls = assistant_message.get("tool_calls") or []
                if not tool_calls:
                    return assistant_message.get("content", "").strip()

                for tool_call in tool_calls:
                    result = self._execute_tool_call(tool_call)
                    function = tool_call.get("function", {})
                    tool_name = function.get("name", "unknown")
                    if tool_name == "web_search":
                        web_evidence_seen = True
                        direct_answer = self._deterministic_web_answer(user_query, result)
                        if direct_answer:
                            return direct_answer
                    messages.append({"role": "tool", "content": result, "name": tool_name})

                if web_evidence_seen:
                    messages.append({
                        "role": "system",
                        "content": EvidenceGuard.final_instruction(user_query, result),
                    })

            final_message = self.client.chat(
                messages + [{"role": "system", "content": "Give the best final answer now. Do not call any more tools."}]
            )
            return final_message.get("content", "").strip()
        except Exception as e:
            return f"Error: {e}"
