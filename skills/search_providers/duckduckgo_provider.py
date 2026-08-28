class DuckDuckGoProvider:
    """Free fallback provider using the ddgs package."""

    name = "duckduckgo"

    def available(self) -> bool:
        try:
            from ddgs import DDGS  # noqa: F401
            return True
        except ImportError:
            return False

    def search(self, query: str, max_results: int = 5) -> list[dict]:
        from ddgs import DDGS

        results = []
        with DDGS() as ddgs:
            for result in ddgs.text(str(query), max_results=max_results):
                if result:
                    results.append({
                        "title": result.get("title", ""),
                        "body": result.get("body", ""),
                        "href": result.get("href", ""),
                        "provider": self.name,
                    })
        return results
