from skills.base_skill import BaseSkill
from skills.search_providers.brave_provider import BraveSearchProvider
from skills.search_providers.duckduckgo_provider import DuckDuckGoProvider


class WebSearchSkill(BaseSkill):
    name = "web_search"
    description = "Search the web using Brave when configured, with DuckDuckGo as a free fallback, and optionally verify pages."
    schema = {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": description,
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search keywords"},
                    "max_results": {"type": "integer", "description": "Maximum search results (1-10)"},
                    "verify": {"type": "boolean", "description": "Open result pages and return verified page text"},
                },
                "required": ["query"],
            },
        },
    }

    def __init__(self):
        self.providers = [BraveSearchProvider(), DuckDuckGoProvider()]

    @staticmethod
    def _looks_time_sensitive(query: str) -> bool:
        q = query.lower()
        markers = (
            "latest", "current", "today", "now", "recent", "newest",
            "release", "version", "price", "news", "this week", "this month",
            "آخر", "حاليا", "اليوم", "جديد"
        )
        return any(marker in q for marker in markers)

    @staticmethod
    def _verify_url(url: str) -> str:
        try:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                text = page.inner_text("body")
                browser.close()
                text = " ".join(text.split())
                return text[:5000]
        except Exception as exc:
            return f"Verification failed: {exc}"

    def execute(self, arguments: dict) -> str:
        query = arguments.get("query", "") if isinstance(arguments, dict) else str(arguments)
        max_results = 5
        verify = False
        if isinstance(arguments, dict):
            try:
                max_results = max(1, min(int(arguments.get("max_results", 5)), 10))
            except (TypeError, ValueError):
                max_results = 5
            verify = bool(arguments.get("verify", False))

        if not query:
            return "Error: No search query provided."

        # Current/freshness questions need primary-page verification instead of
        # relying only on a search snippet. This is the key difference between
        # ordinary search and research mode.
        verify = verify or self._looks_time_sensitive(str(query))

        errors = []
        for provider in self.providers:
            if not provider.available():
                continue
            try:
                results = provider.search(str(query), max_results=max_results)
                if not results:
                    continue

                output = []
                for result in results:
                    output.append(
                        f"- **{result.get('title', '')}** [{result.get('provider', '')}]\n"
                        f"  URL: {result.get('href', '')}\n"
                        f"  Snippet: {result.get('body', '')}\n"
                    )
                    if verify and result.get("href"):
                        page_text = self._verify_url(result["href"])
                        output.append(f"  VERIFIED_PAGE_TEXT: {page_text}\n")

                return "".join(output)
            except Exception as exc:
                errors.append(f"{provider.name}: {exc}")

        if errors:
            return "Web search error: " + " | ".join(errors)
        return "No web search provider is available. Configure BRAVE_SEARCH_API_KEY or install the ddgs package."
