# main.py
import json
from models.ollama_client import OllamaClient
from skills.calculator import CalculatorSkill
from skills.file_manager import FileManagerSkill
from skills.memory_skill import MemorySkill
from skills.web_search import WebSearchSkill
from skills.python_sandbox import PythonSandboxSkill
from skills.browser_skill import BrowserSkill
from skills.database_skill import DatabaseSkill
from skills.git_skill import GitSkill

def main():
    client = OllamaClient(model_name="qwen3:1.7b")
    calc_skill = CalculatorSkill()
    file_skill = FileManagerSkill()
    memory_skill = MemorySkill()
    web_search_skill = WebSearchSkill()
    python_skill = PythonSandboxSkill()
    browser_skill = BrowserSkill()
    db_skill = DatabaseSkill()
    git_skill = GitSkill()

    available_tools = [
        calc_skill.get_schema(),
        file_skill.get_schema(),
        memory_skill.get_schema(),
        web_search_skill.get_schema(),
        python_skill.get_schema(),
        browser_skill.get_schema(),
        db_skill.get_schema(),
        git_skill.get_schema()
    ]

    print("==========================================")
    print("   AI Agent Core - Phase 8 (Git/GitHub)")
    print("==========================================")
    print("Type 'exit' to stop.\n")

    conversation_history = [
        {"role": "system", "content": "You are a helpful AI assistant with access to a calculator, file manager, long-term memory, web search, python sandbox, browser automation, database manager, and git integration. Use the git_manager tool when asked to check repository status, commit changes, or view git history."}
    ]

    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() == 'exit':
                break
            if not user_input.strip():
                continue

            conversation_history.append({"role": "user", "content": user_input})

            print("\n[Agent thinking...]")
            response = client.chat(messages=conversation_history, tools=available_tools)

            if response.get("tool_calls"):
                tool_call = response["tool_calls"][0]
                tool_name = tool_call["function"]["name"]
                args = tool_call["function"]["arguments"]

                tool_result = ""
                if tool_name == "calculator":
                    print(f" > [Executing Tool: Calculator] args: {args}")
                    tool_result = calc_skill.execute(args)
                elif tool_name == "file_manager":
                    print(f" > [Executing Tool: File Manager] args: {args}")
                    tool_result = file_skill.execute(args)
                elif tool_name == "memory_tool":
                    print(f" > [Executing Tool: Memory] args: {args}")
                    tool_result = memory_skill.execute(args)
                elif tool_name == "web_search":
                    print(f" > [Executing Tool: Web Search] args: {args}")
                    tool_result = web_search_skill.execute(args)
                elif tool_name == "python_sandbox":
                    print(f" > [Executing Tool: Python Sandbox] args: {args}")
                    tool_result = python_skill.execute(args)
                elif tool_name == "browser_automation":
                    print(f" > [Executing Tool: Browser Automation] args: {args}")
                    tool_result = browser_skill.execute(args)
                elif tool_name == "database_manager":
                    print(f" > [Executing Tool: Database Manager] args: {args}")
                    tool_result = db_skill.execute(args)
                elif tool_name == "git_manager":
                    print(f" > [Executing Tool: Git Manager] args: {args}")
                    tool_result = git_skill.execute(args)

                print(f" > [Tool Result]: {tool_result}")

                conversation_history.append({
                    "role": "assistant",
                    "tool_calls": [tool_call]
                })
                conversation_history.append({
                    "role": "tool",
                    "content": str(tool_result),
                    "name": tool_name
                })

                print("[Agent summarizing result...]\n")
                final_response = client.chat(messages=conversation_history)
                assistant_reply = final_response.get("content", "Done.")
                print(f"Agent: {assistant_reply}\n")
                
                conversation_history.append({"role": "assistant", "content": assistant_reply})
            else:
                assistant_reply = response.get("content", "")
                print(f"Agent: {assistant_reply}\n")
                conversation_history.append({"role": "assistant", "content": assistant_reply})

        except Exception as e:
            print(f"\n[LLM ERROR] {e}\n")

if __name__ == "__main__":
    main()