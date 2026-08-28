import os
import importlib
import inspect
import json
from models.ollama_client import OllamaClient
from skills.base_skill import BaseSkill


class AgentCore:
    """Core agent loop with dynamic skill discovery and native Ollama tool calling."""

    MAX_TOOL_STEPS = 6

    def __init__(self, model_name="qwen3:1.7b"):
        self.model_name = model_name
        self.client = OllamaClient(model_name=model_name)
        self.skills = {}
        self._load_skills()

    def _load_skills(self):
        """Discover every concrete BaseSkill implementation in skills/."""
        skills_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "skills"
        )

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
        """Return OpenAI/Ollama-compatible tool definitions from all skills."""
        tools = []
        for skill in self.skills.values():
            schema = skill.schema
            if "function" in schema:
                tools.append(schema)
            else:
                tools.append(
                    {
                        "type": "function",
                        "function": {
                            "name": skill.name,
                            "description": skill.description,
                            "parameters": schema,
                        },
                    }
                )
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

    def _execute_tool_call(self, tool_call):
        function = tool_call.get("function", {}) if isinstance(tool_call, dict) else {}
        name = function.get("name")
        arguments = self._normalize_arguments(function.get("arguments", {}))

        if name not in self.skills:
            return f"Tool Error: Unknown tool '{name}'."

        try:
            return self.skills[name].execute(arguments)
        except Exception as e:
            return f"Tool Error in '{name}': {e}"

    def run(self, user_query: str) -> str:
        """Run the agent until it reaches a final answer or the step limit."""
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an autonomous local AI agent. Use tools when they are useful. "
                    "You may call multiple tools in sequence. After observing tool results, "
                    "continue reasoning until the user's task is complete. "
                    "Do not claim a tool was used unless you actually called it. "
                    "Reply in the same language or dialect as the user."
                ),
            },
            {"role": "user", "content": user_query},
        ]

        tools = self._tool_definitions()

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
                    messages.append(
                        {
                            "role": "tool",
                            "content": result,
                            "name": tool_name,
                        }
                    )

            # Ask for a concise final response if the safety step limit is reached.
            final_message = self.client.chat(
                messages + [
                    {
                        "role": "system",
                        "content": "Give the best final answer now. Do not call any more tools.",
                    }
                ]
            )
            return final_message.get("content", "").strip()

        except Exception as e:
            return f"Error: {e}"
