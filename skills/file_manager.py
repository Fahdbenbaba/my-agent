import os
from skills.base_skill import BaseSkill


class FileManagerSkill(BaseSkill):
    name = "file_manager"
    description = "Use this tool to read the contents of a text file on the local machine."
    schema = {
        "type": "function",
        "function": {
            "name": "file_manager",
            "description": description,
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "The path of the file to read (relative or absolute)",
                    }
                },
                "required": ["filepath"],
            },
        },
    }

    def execute(self, arguments: dict) -> str:
        filepath = arguments.get("filepath", "")
        try:
            if not os.path.exists(filepath):
                return f"Error: File '{filepath}' not found."

            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"
