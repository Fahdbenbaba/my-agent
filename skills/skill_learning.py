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
        "Continuously learn reusable knowledge from verified debugging, workarounds, "
        "project patterns, and tool discoveries. Use after non-obvious tasks or when "
        "the user asks what was learned, save this as a skill, or extract a skill."
    )
    schema = {
        "type": "function",
        "function": {
            "name": "skill_learning",
            "description": description,
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["list", "search", "save", "get"],
                    },
                    "name": {
                        "type": "string",
                        "description": "Skill slug for save/get (kebab-case).",
                    },
                    "query": {
                        "type": "string",
                        "description": "Search terms for existing learned skills.",
                    },
                    "title": {"type": "string"},
                    "description_text": {
                        "type": "string",
                        "description": "Precise reusable trigger-oriented description.",
                    },
                    "problem": {"type": "string"},
                    "triggers": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "solution": {"type": "string"},
                    "verification": {"type": "string"},
                    "notes": {"type": "string"},
                    "source": {"type": "string"},
                },
                "required": ["action"],
            },
        },
    }

    def __init__(self, root=None):
        project_root = Path(root or os.path.dirname(os.path.dirname(__file__)))
        self.root = project_root / "agent_skills"
        self.root.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _slug(value: str) -> str:
        value = re.sub(r"[^a-zA-Z0-9]+", "-", str(value).strip().lower()).strip("-")
        return value[:80]

    @staticmethod
    def _clean(value: str, limit=12000) -> str:
        text = str(value or "").strip()
        # Never persist credentials, bearer tokens, private keys, or obvious secrets.
        secret_patterns = [
            r"(?i)(api[_ -]?key|client[_ -]?secret|access[_ -]?token|refresh[_ -]?token|password|authorization)\s*[:=]\s*[^\s]+",
            r"(?i)bearer\s+[A-Za-z0-9._~+/=-]+",
            r"-----BEGIN [A-Z ]+PRIVATE KEY-----.*?-----END [A-Z ]+PRIVATE KEY-----",
            r"(?i)ghp_[A-Za-z0-9]+",
            r"(?i)github_pat_[A-Za-z0-9_]+",
        ]
        for pattern in secret_patterns:
            text = re.sub(pattern, "[REDACTED_SECRET]", text, flags=re.S)
        return text[:limit]

    def _paths(self) -> list[Path]:
        return sorted(self.root.glob("*/SKILL.md"))

    def _read(self, path: Path) -> str:
        return path.read_text(encoding="utf-8", errors="replace")

    def _matches(self, text: str, query: str) -> int:
        terms = [t for t in re.findall(r"[a-z0-9][a-z0-9._-]+", query.lower()) if len(t) > 2]
        haystack = text.lower()
        return sum(1 for term in terms if term in haystack)

    def _render(self, slug: str, title: str, description: str, problem: str, triggers: Iterable[str], solution: str, verification: str, notes: str, source: str, version: str, date: str) -> str:
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
            "## Notes\n\n"
            f"{self._clean(notes) or 'Use only when the trigger conditions match. Do not treat this skill as authoritative without verification.'}"
            f"{references}\n"
        )

    def _save(self, arguments: dict) -> str:
        required = ["name", "title", "description_text", "problem", "solution", "verification"]
        missing = [key for key in required if not str(arguments.get(key, "")).strip()]
        if missing:
            return "SKILL_LEARNING_ERROR: Missing required fields: " + ", ".join(missing)

        slug = self._slug(arguments["name"])
        if not slug:
            return "SKILL_LEARNING_ERROR: Invalid skill name."

        description = self._clean(arguments["description_text"], 1500)
        content = "\n".join([description, self._clean(arguments["problem"]), self._clean(arguments["solution"])])
        if len(content.strip()) < 80:
            return "SKILL_REJECTED: Knowledge is too thin to be reusable."

        suspicious = ("[REDACTED_SECRET]" in content and any(token in content.lower() for token in ("token", "secret", "password", "api key")))
        if suspicious:
            return "SKILL_REJECTED: Sensitive credential-like content was detected."

        target = self.root / slug / "SKILL.md"
        existing = self._read(target) if target.exists() else ""
        if existing:
            old_version = re.search(r"(?m)^version:\s*([0-9]+)\.([0-9]+)\.([0-9]+)\s*$", existing)
            if old_version:
                major, minor, patch = map(int, old_version.groups())
                version = f"{major}.{minor}.{patch + 1}"
            else:
                version = "1.1.0"
        else:
            version = "1.0.0"

        rendered = self._render(
            slug=slug,
            title=arguments["title"],
            description=description,
            problem=arguments["problem"],
            triggers=arguments.get("triggers", []),
            solution=arguments["solution"],
            verification=arguments["verification"],
            notes=arguments.get("notes", ""),
            source=arguments.get("source", ""),
            version=version,
            date=datetime.now(timezone.utc).date().isoformat(),
        )
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
            scored = [(self._matches(self._read(path), query), path) for path in self._paths()]
            scored = [item for item in scored if item[0] > 0]
            scored.sort(key=lambda item: item[0], reverse=True)
            if not scored:
                return "No matching learned skills found."
            lines = ["LEARNED_SKILL_SEARCH"]
            for score, path in scored[:10]:
                lines.append(f"- score={score} name={path.parent.name} path={path.as_posix()}")
            return "\n".join(lines)

        slug = self._slug(arguments.get("name", ""))
        if not slug:
            return "Skill Learning Error: No skill name provided."
        target = self.root / slug / "SKILL.md"
        if action == "get":
            if not target.exists():
                return f"Learned skill not found: {slug}"
            return self._read(target)[:20000]

        return self._save(arguments)
