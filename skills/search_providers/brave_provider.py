import os
import requests


class BraveSearchProvider:
    """Brave Search provider. Enabled only when BRAVE_SEARCH_API_KEY is set."""

    name = "brave"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("BRAVE_SEARCH_API_KEY")

    def available(self) -> bool:
        return bool(self.api_key)

    def search(self, query: str, max_results: int = 5) -> list[dict]:
        if not self.api_key:
            raise RuntimeError("BRAVE_SEARCH_API_KEY is not configured")

        response = requests.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers={
                "Accept": "application/json",
                "X-Subscription-Token": self.api_key,
            },
            params={
                "q": query,
                "count": min(max_results, 20),
                "search_lang": "en",
            },
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()

        results = []
        for item in (data.get("web", {}).get("results", []) or []):
            results.append({
                "title": item.get("title", ""),
                "body": item.get("description", "") or item.get("snippet", ""),
                "href": item.get("url", ""),
                "provider": self.name,
            })
        return results
