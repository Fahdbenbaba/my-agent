from skills.base_skill import BaseSkill


class WebSearchSkill(BaseSkill):
    name = "web_search"
    description = "Search the web for current information, news, and facts."
    schema = {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": description,
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search keywords"}
                },
                "required": ["query"],
            },
        },
    }

    def execute(self, arguments: dict) -> str:
        query = arguments.get("query", "") if isinstance(arguments, dict) else str(arguments)
        if not query:
            return "Error: No search query provided."

        try:
            from ddgs import DDGS
            results = []
            with DDGS() as ddgs:
                for result in ddgs.text(str(query), max_results=3):
                    if result:
                        results.append(result)

            if not results:
                return "No web results found."

            return "".join(
                f"- **{result.get('title', '')}**: {result.get('body', '')}\n"
                f"  URL: {result.get('href', '')}\n"
                for result in results
            )
        except Exception as e:
            return f"Web search error: {str(e)}"
