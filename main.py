import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.core import AgentCore
from agent.router import Router


def main():
    agent = AgentCore(model_name="qwen3:1.7b")
    router = Router()

    print("🚀 Full Master Agent (All Skills Integrated) is Online! (Type 'exit' to quit)\n" + "-" * 60)

    while True:
        try:
            user_query = input("You: ").strip()

            if user_query.lower() == "exit":
                print("Goodbye!")
                break

            if user_query.lower() in {"clear", "clear memory", "clear conversation"}:
                agent.clear_history()
                print("\nAgent:\nConversation memory cleared.\n" + "-" * 60)
                continue

            if not user_query:
                continue

            print("\n[Agent analyzing & routing...]")
            route_decision = router.route(user_query)

            if route_decision and route_decision.get("use_tool"):
                tool_name = route_decision.get("tool")
                if tool_name in agent.skills:
                    print(f"🔧 Executing skill: {tool_name}")

            response = agent.run(user_query)
            print(f"\nAgent:\n{response}\n" + "-" * 60)

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {e}\n" + "-" * 60)


if __name__ == "__main__":
    main()
