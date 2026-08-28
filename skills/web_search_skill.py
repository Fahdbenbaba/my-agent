from skills.base_skill import BaseSkill
from skills.search_providers.brave_provider import BraveSearchProvider
from skills.search_providers.duckduckgo_provider import DuckDuckGoProvider


class WebSearchSkill(BaseSkill):
    name = "web_search"
    description = "Search the web using Brave when configured, with DuckDuckGo as a free fallback."
    schema = {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": description,
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search keywords"},
                    "max_results": {"type": "integer", "description": "Maximum results (1-10)"},
                },
                "required": ["query"],
            },
        },
    }

    def __init__(self):
        self.providers = [BraveSearchProvider(), DuckDuckGoProvider()]

    def execute(self, arguments: dict) -> str:
        query = arguments.get("query", "") if isinstance(arguments, dict) else str(arguments)
        if not query:
            return "Error: No search query provided."

        try:
            max_results = max(1, min(int(arguments.get("max_results", 5)), 10))
        except (TypeError, ValueError):
            max_results = 5

        errors = []
        for provider in self.providers:
            if not provider.available():
                continue
            try:
                results = provider.search(str(query), max_results=max_results)
                if results:
                    return "".join(
                        f"- **{result.get('title', '')}**: {result.get('body', '')}\n"
                        f"  URL: {result.get('href', '')}\n"
                        for result in results
                    )
            except Exception as exc:
                errors.append(f"{provider.name}: {exc}")

        if errors:
            return "Web search error: " + " | ".join(errors)
        return "No web search provider is available. Configure BRAVE_SEARCH_API_KEY or install the ddgs package."
