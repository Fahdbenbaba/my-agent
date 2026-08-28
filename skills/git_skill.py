import subprocess
from skills.base_skill import BaseSkill


class GitSkill(BaseSkill):
    name = "git_manager"
    description = "Execute approved Git commands in the current workspace repository."
    schema = {
        "type": "function",
        "function": {
            "name": "git_manager",
            "description": description,
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Git subcommand and arguments, e.g. 'status' or 'diff'.",
                    }
                },
                "required": ["command"],
            },
        },
    }

    ALLOWED_COMMANDS = {
        "status", "diff", "log", "show", "branch", "remote", "rev-parse",
        "add", "commit", "restore", "switch", "checkout",
    }

    def execute(self, arguments: dict) -> str:
        command = arguments.get("command", "").strip()
        if not command:
            return "Error: No git command provided."

        parts = command.split()
        if not parts or parts[0] not in self.ALLOWED_COMMANDS:
            return f"Error: Git command '{parts[0] if parts else ''}' is not allowed."

        try:
            result = subprocess.run(
                ["git", *parts],
                shell=False,
                capture_output=True,
                text=True,
                timeout=15,
            )
            output = result.stdout.strip()
            error = result.stderr.strip()
            if result.returncode == 0:
                return output or "Git command executed successfully with no output."
            return f"Git Error:\n{error or output}"
        except Exception as e:
            return f"Execution Exception: {str(e)}"
