import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.core import AgentCore
from agent.router import Router
from skills.calculator import CalculatorSkill
from skills.file_manager import FileManagerSkill
from skills.memory_skill import MemorySkill
from skills.web_search_skill import WebSearchSkill
from skills.git_skill import GitSkill
from skills.database_skill import DatabaseSkill
from skills.browser_skill import BrowserSkill
from skills.python_sandbox import PythonSandboxSkill


def main():
    agent = AgentCore(model_name="qwen3:1.7b")
    router = Router()

    tools = {
        "calculator": CalculatorSkill(),
        "file_manager": FileManagerSkill(),
        "memory": MemorySkill(),
        "web_search": WebSearchSkill(),
        "git": GitSkill(),
        "database": DatabaseSkill(),
        "browser": BrowserSkill(),
        "python_sandbox": PythonSandboxSkill(),
    }

    print("🚀 Full Master Agent (All Skills Integrated) is Online! (Type 'exit' to quit)\n" + "-" * 60)

    while True:
        try:
            user_query = input("You: ")
            if user_query.strip().lower() == "exit":
                print("Goodbye!")
                break

            if not user_query.strip():
                continue

            print("\n[Agent analyzing & routing...]")
            route_decision = router.route(user_query)

            if route_decision and route_decision.get("use_tool"):
                tool_name = route_decision.get("tool")
                arguments = route_decision.get("arguments", {})
                print(f"🔧 Executing skill: {tool_name}")

                if tool_name in tools:
                    tool_result = tools[tool_name].execute(arguments)

                    synthesis_prompt = f"""
The user asked: "{user_query}"
The tool "{tool_name}" returned this result: "{tool_result}"
Task: Write a natural, direct, and helpful response to the user based on this tool result. Do not mention technical tool names, just answer naturally.
"""
                    response = agent.run(synthesis_prompt)
                else:
                    response = f"Error: Tool '{tool_name}' not found."
            else:
                response = agent.run(user_query)

            print(f"\nAgent:\n{response}\n" + "-" * 60)

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {e}\n" + "-" * 60)


if __name__ == "__main__":
    main()
