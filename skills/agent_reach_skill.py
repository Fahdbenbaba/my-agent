import json
import shutil
import subprocess
from skills.base_skill import BaseSkill


class AgentReachSkill(BaseSkill):
    """Bridge to the locally installed Agent Reach CLI."""

    name = "agent_reach"
    description = "Check and use locally installed Agent Reach internet capabilities. Run diagnostics first; installation is explicit and never automatic."
    schema = {
        "type": "function",
        "function": {
            "name": "agent_reach",
            "description": description,
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["status", "doctor", "capabilities"],
                        "description": "status checks the CLI, doctor runs Agent Reach diagnostics, capabilities returns the supported capability map.",
                    }
                },
                "required": ["action"],
            },
        },
    }

    CAPABILITIES = {
        "web": "Read public web pages through Agent Reach's configured web backend.",
        "youtube": "Search videos and extract available metadata/transcripts.",
        "rss": "Read RSS and Atom feeds.",
        "github": "Read public repositories; additional actions require explicit GitHub authorization.",
        "search": "Use the configured semantic web-search backend.",
        "social": "Optional channels such as X, Reddit, LinkedIn, Facebook, and Instagram may require explicit local login/configuration.",
    }

    @staticmethod
    def _cli():
        return shutil.which("agent-reach") or shutil.which("agent-reach.exe")

    def execute(self, arguments: dict) -> str:
        if not isinstance(arguments, dict):
            return "Agent Reach Error: arguments must be a dictionary."

        action = str(arguments.get("action", "status")).strip().lower()
        if action not in {"status", "doctor", "capabilities"}:
            return f"Agent Reach Error: Unsupported action '{action}'."

        if action == "capabilities":
            return json.dumps({"installed": bool(self._cli()), "capabilities": self.CAPABILITIES}, ensure_ascii=False, indent=2)

        cli = self._cli()
        if not cli:
            return (
                "AGENT_REACH_NOT_INSTALLED\n"
                "Agent Reach CLI was not found on PATH. Install it explicitly first, then run this action again. "
                "The agent will not modify your system or install software automatically."
            )

        if action == "status":
            return f"AGENT_REACH_AVAILABLE\nCLI: {cli}\nRun the 'doctor' action for full diagnostics."

        try:
            completed = subprocess.run(
                [cli, "doctor"],
                capture_output=True,
                text=True,
                timeout=120,
                shell=False,
            )
            output = (completed.stdout or completed.stderr or "").strip()
            return (
                f"AGENT_REACH_DOCTOR\nEXIT_CODE: {completed.returncode}\n"
                f"{output[:12000]}"
            )
        except subprocess.TimeoutExpired:
            return "Agent Reach Error: doctor timed out after 120 seconds."
        except OSError as exc:
            return f"Agent Reach Error: {exc}"
