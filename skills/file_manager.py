import os
from pathlib import Path

from skills.base_skill import BaseSkill


class FileManagerSkill(BaseSkill):
    name = "file_manager"
    description = "Safely list, read, and create text files in the agent workspace."
    schema = {
        "type": "function",
        "function": {
            "name": "file_manager",
            "description": description,
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["list", "read", "create"],
                        "description": "File operation to perform.",
                    },
                    "filepath": {
                        "type": "string",
                        "description": "Path relative to the agent workspace.",
                    },
                    "content": {
                        "type": "string",
                        "description": "Text content used when action is create.",
                    },
                },
                "required": ["action"],
            },
        },
    }

    def __init__(self):
        self.workspace = Path.cwd().resolve()

    def _safe_path(self, filepath: str) -> Path:
        path = (self.workspace / filepath).resolve()
        if path != self.workspace and self.workspace not in path.parents:
            raise ValueError("Path must stay inside the agent workspace.")
        return path

    def execute(self, arguments: dict) -> str:
        if not isinstance(arguments, dict):
            return "File Manager Error: arguments must be a dictionary."

        action = str(arguments.get("action", "")).strip().lower()

        try:
            if action == "list":
                items = sorted(p.name for p in self.workspace.iterdir())
                return "Files and folders:\n" + ("\n".join(items) if items else "(empty)")

            filepath = str(arguments.get("filepath", "")).strip()
            if not filepath:
                return "File Manager Error: filepath is required."

            path = self._safe_path(filepath)

            if action == "read":
                if not path.is_file():
                    return f"Error: File '{filepath}' not found."
                return path.read_text(encoding="utf-8")

            if action == "create":
                content = str(arguments.get("content", ""))
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
                return f"File created successfully: {path.relative_to(self.workspace)}"

            return "File Manager Error: action must be 'list', 'read', or 'create'."

        except Exception as e:
            return f"File Manager Error: {str(e)}"
