# skills/web_search.py
from ddgs import DDGS
from skills.base_skill import BaseSkill

class WebSearchSkill(BaseSkill):
    def get_name(self) -> str:
        return "web_search"

    def get_description(self) -> str:
        return "Search the web for real-time information, news, or facts using DDGS."

    def get_schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.get_name(),
                "description": self.get_description(),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query to look up on the web."
                        }
                    },
                    "required": ["query"]
                }
            }
        }

    def execute(self, args: dict) -> str:
        query = args.get("query")
        if not query:
            return "Error: No query provided."

        try:
            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=4):
                    title = r.get("title", "")
                    body = r.get("body", "")
                    results.append(f"- {title}: {body}")

            if not results:
                return f"No results found for '{query}'."

            return "\n".join(results)
        except Exception as e:
            return f"Error executing web search: {str(e)}"