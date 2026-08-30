import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from skills.base_skill import BaseSkill


class SkillLearningSkill(BaseSkill):
    """Persist verified, reusable lessons as searchable Markdown skills."""

    name = "skill_learning"
    description = (
        "Learn reusable knowledge from verified debugging, workarounds, project patterns, "
        "and tool discoveries. Learned content must be grounded in concrete evidence, not "
        "model-only speculation."
    )
    schema = {
        "type": "function",
        "function": {
            "name": "skill_learning",
            "description": description,
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["list", "search", "save", "get"]},
                    "name": {"type": "string"},
                    "query": {"type": "string"},
                    "title": {"type": "string"},
                    "description_text": {"type": "string"},
                    "problem": {"type": "string"},
                    "triggers": {"type": "array", "items": {"type": "string"}},
                    "solution": {"type": "string"},
                    "verification": {"type": "string"},
                    "evidence": {"type": "string"},
                    "context": {"type": "string", "description": "Verified execution context supplied by the agent core. Prefer this over assumptions."},
                    "notes": {"type": "string"},
                    "source": {"type": "string"},
                },
                "required": ["action"],
            },
        },
    }

    def __init__(self, root=None):
        # Tests and callers may provide an explicit skill-library root.
        # The default runtime location remains project_root/agent_skills.
        if root is None:
            project_root = Path(os.path.dirname(os.path.dirname(__file__)))
            self.root = project_root / "agent_skills"
        else:
            self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _slug(value: str) -> str:
        return re.sub(r"[^a-zA-Z0-9]+", "-", str(value).strip().lower()).strip("-")[:80]

    @staticmethod
    def _clean(value: str, limit=12000) -> str:
        text = str(value or "").strip()
        patterns = [
            r"(?i)(api[_ -]?key|client[_ -]?secret|access[_ -]?token|refresh[_ -]?token|password|authorization)\s*[:=]\s*[^\s]+",
            r"(?i)bearer\s+[A-Za-z0-9._~+/=-]+",
            r"-----BEGIN [A-Z ]+PRIVATE KEY-----.*?-----END [A-Z ]+PRIVATE KEY-----",
            r"(?i)ghp_[A-Za-z0-9]+",
            r"(?i)github_pat_[A-Za-z0-9_]+",
        ]
        for pattern in patterns:
            text = re.sub(pattern, "[REDACTED_SECRET]", text, flags=re.S)
        return text[:limit]

    def _paths(self):
        return sorted(self.root.glob("*/SKILL.md"))

    def _read(self, path: Path) -> str:
        return path.read_text(encoding="utf-8", errors="replace")

    def _matches(self, text: str, query: str) -> int:
        terms = [t for t in re.findall(r"[a-z0-9][a-z0-9._-]+", query.lower()) if len(t) > 2]
        haystack = text.lower()
        return sum(term in haystack for term in terms)

    @staticmethod
    def _quality_check(problem: str, solution: str, verification: str, evidence: str, context: str) -> str | None:
        if not evidence.strip() and not context.strip():
            return "SKILL_REJECTED: No concrete evidence/context was supplied. Do not learn from model-only speculation."
        combined = f"{evidence}\n{context}\n{verification}".lower()
        markers = ("exit_code: 0", "success", "successfully", "listening on", "passed", "verified", "working", "completed")
        if not any(marker in combined for marker in markers):
            return "SKILL_REJECTED: Evidence lacks a recognizable successful/verified execution marker."
        if "unicodedecodeerror" in problem.lower() and "cp1252" in problem.lower():
            solution_lower = solution.lower()
            if "utf-8" not in solution_lower or ("errors=\"replace\"" not in solution_lower and "errors='replace'" not in solution_lower):
                return "SKILL_REJECTED: Proposed encoding fix is not supported by the verified UTF-8 replacement-decoding evidence."
        return None

    def _render(self, slug, title, description, problem, triggers: Iterable[str], solution, verification, evidence, notes, source, version, date):
        trigger_lines = "\n".join(f"- {self._clean(t, 1000)}" for t in triggers if str(t).strip())
        references = f"\n\n## References\n{self._clean(source, 4000)}" if str(source).strip() else ""
        return (
            "---\n"
            f"name: {slug}\n"
            "description: |\n"
            f"  {self._clean(description, 1500).replace(chr(10), chr(10) + '  ')}\n"
            "author: My Agent\n"
            f"version: {version}\n"
            f"date: {date}\n"
            "---\n\n"
            f"# {self._clean(title, 300)}\n\n"
            "## Problem\n\n"
            f"{self._clean(problem)}\n\n"
            "## Context / Trigger Conditions\n\n"
            f"{trigger_lines or '- No specific triggers supplied.'}\n\n"
            "## Solution\n\n"
            f"{self._clean(solution)}\n\n"
            "## Verification\n\n"
            f"{self._clean(verification)}\n\n"
            "## Evidence\n\n"
            f"{self._clean(evidence)}\n\n"
            "## Notes\n\n"
            f"{self._clean(notes) or 'Use only when the trigger conditions match. Re-verify before applying to a different environment.'}"
            f"{references}\n"
        )

    def _save(self, arguments: dict) -> str:
        required = ["name", "title", "description_text", "problem", "solution", "verification"]
        missing = [key for key in required if not str(arguments.get(key, "")).strip()]
        if missing:
            return "SKILL_LEARNING_ERROR: Missing required fields: " + ", ".join(missing)

        evidence = str(arguments.get("evidence", "")).strip()
        context = str(arguments.get("context", "")).strip()
        rejection = self._quality_check(str(arguments["problem"]), str(arguments["solution"]), str(arguments["verification"]), evidence, context)
        if rejection:
            return rejection

        slug = self._slug(arguments["name"])
        if not slug:
            return "SKILL_LEARNING_ERROR: Invalid skill name."

        safe_context = self._clean(context)
        safe_evidence = self._clean(evidence)
        safe_solution = self._clean(arguments["solution"])
        combined = "\n".join([self._clean(arguments["description_text"]), self._clean(arguments["problem"]), safe_solution, self._clean(arguments["verification"]), safe_evidence, safe_context])
        if len(combined.strip()) < 120:
            return "SKILL_REJECTED: Knowledge is too thin to be reusable."

        target = self.root / slug / "SKILL.md"
        existing = self._read(target) if target.exists() else ""
        if existing:
            old_version = re.search(r"(?m)^version:\s*([0-9]+)\.([0-9]+)\.([0-9]+)\s*$", existing)
            version = f"{int(old_version.group(1))}.{int(old_version.group(2))}.{int(old_version.group(3)) + 1}" if old_version else "1.1.0"
        else:
            version = "1.0.0"

        rendered = self._render(slug, arguments["title"], arguments["description_text"], arguments["problem"], arguments.get("triggers", []), safe_solution, arguments["verification"], safe_evidence or safe_context, arguments.get("notes", ""), arguments.get("source", ""), version, datetime.now(timezone.utc).date().isoformat())
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")
        return f"SKILL_SAVED: {slug}\nPATH: {target.as_posix()}\nVERSION: {version}"

    def execute(self, arguments: dict) -> str:
        if not isinstance(arguments, dict):
            return "Skill Learning Error: arguments must be a dictionary."
        action = str(arguments.get("action", "")).strip().lower()
        if action not in {"list", "search", "save", "get"}:
            return f"Skill Learning Error: Unsupported action '{action}'."
        if action == "list":
            paths = self._paths()
            if not paths:
                return "No learned skills yet."
            lines = ["LEARNED_SKILLS"]
            for path in paths:
                content = self._read(path)
                match = re.search(r"(?m)^name:\s*(.+)$", content)
                description = re.search(r"(?ms)^description:\s*\|\n((?:\s{2}.+\n?)+)", content)
                desc = " ".join(line.strip() for line in (description.group(1).splitlines() if description else []))[:180]
                lines.append(f"- {match.group(1).strip() if match else path.parent.name}: {desc}")
            return "\n".join(lines)
        if action == "search":
            query = str(arguments.get("query", "")).strip()
            if not query:
                return "Skill Learning Error: No search query provided."
            scored = sorted([(self._matches(self._read(path), query), path) for path in self._paths()], key=lambda item: item[0], reverse=True)
            scored = [item for item in scored if item[0] > 0]
            if not scored:
                return "No matching learned skills found."
            return "\n".join(["LEARNED_SKILL_SEARCH", *[f"- score={score} name={path.parent.name} path={path.as_posix()}" for score, path in scored[:10]]])
        slug = self._slug(arguments.get("name", ""))
        if not slug:
            return "Skill Learning Error: No skill name provided."
        target = self.root / slug / "SKILL.md"
        if action == "get":
            return self._read(target)[:20000] if target.exists() else f"Learned skill not found: {slug}"
        return self._save(arguments)
