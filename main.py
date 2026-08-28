import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.core import AgentCore
from agent.router import Router


def main():
    agent = AgentCore(model_name="qwen3:1.7b")
    router = Router()

    # AgentCore is the single source of truth for registered skills.
    # Backward-compatible aliases keep older router names working too.
    tools = dict(agent.skills)
    aliases = {
        "git": "git_manager",
        "database": "database_manager",
        "browser": "browser_automation",
    }
    for alias, real_name in aliases.items():
        if real_name in tools:
            tools[alias] = tools[real_name]

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
The tool returned this result: "{tool_result}"
Task: Write a natural, direct, and helpful response based ONLY on this tool result.
Do not invent facts, actions, errors, or results that are not present in the tool result.
Do not mention technical tool names unless the user asked about them.
"""
                    response = agent.run(synthesis_prompt)
                else:
                    response = f"Error: Tool '{tool_name}' is not registered. Available tools: {', '.join(sorted(agent.skills))}"
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
