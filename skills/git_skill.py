# skills/git_skill.py
import subprocess
from skills.base_skill import BaseSkill

class GitSkill(BaseSkill):
    def get_name(self) -> str:
        return "git_manager"

    def get_description(self) -> str:
        return "Execute Git commands (like status, add, commit, log, diff) in the current workspace repository."

    def get_schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.get_name(),
                "description": self.get_description(),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The specific git subcommand and arguments to run, e.g., 'status', 'add .', 'commit -m \"msg\"'."
                        }
                    },
                    "required": ["command"]
                }
            }
        }

    def execute(self, args: dict) -> str:
        cmd_arg = args.get("command")
        if not cmd_arg:
            return "Error: No git command provided."

        # Security check to ensure it's a git command
        full_cmd = f"git {cmd_arg}"
        
        try:
            result = subprocess.run(
                full_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            output = result.stdout.strip()
            error = result.stderr.strip()
            
            if result.returncode == 0:
                return output if output else "Git command executed successfully with no output."
            else:
                return f"Git Error:\n{error if error else output}"
                
        except Exception as e:
            return f"Execution Exception: {str(e)}"