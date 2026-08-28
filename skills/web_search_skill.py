import re
from datetime import datetime, timezone

from skills.base_skill import BaseSkill
from skills.search_providers.brave_provider import BraveSearchProvider
from skills.search_providers.duckduckgo_provider import DuckDuckGoProvider


class WebSearchSkill(BaseSkill):
    name = "web_search"
    description = "Search the web with Brave primary and DuckDuckGo fallback, rank relevant sources, and verify primary pages for current factual questions."
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
                    "verify": {"type": "boolean", "description": "Open relevant result pages and return verified page text"},
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
            "latest", "current", "today", "now", "recent", "newest", "release",
            "version", "price", "news", "this week", "this month", "آخر", "حاليا",
            "اليوم", "جديد", "أحدث", "نسخة", "إصدار"
        )
        return any(marker in q for marker in markers)

    @staticmethod
    def _keywords(query: str) -> set[str]:
        return {
            w for w in re.findall(r"[a-z0-9][a-z0-9._+-]*", query.lower())
            if len(w) > 1 and w not in {"the", "for", "and", "with", "from", "what", "is", "are"}
        }

    @classmethod
    def _score_result(cls, query: str, result: dict) -> float:
        title = str(result.get("title", "")).lower()
        body = str(result.get("body", "")).lower()
        url = str(result.get("href", "")).lower()
        haystack = f"{title} {body} {url}"
        keywords = cls._keywords(query)
        score = sum(2 for word in keywords if word in title)
        score += sum(1 for word in keywords if word in body)

        # Prefer primary/official sources for factual and release/version questions.
        official_domains = {
            "python.org": ("python",),
            "docs.python.org": ("python",),
            "pypi.org": ("python",),
            "github.com": (),
        }
        for domain, hints in official_domains.items():
            if domain in url:
                score += 8
                if hints and any(h in haystack for h in hints):
                    score += 3
                break

        if "release" in query.lower() or "version" in query.lower() or "latest" in query.lower():
            if any(token in title for token in ("release", "download", "python")):
                score += 4

        if result.get("provider") == "brave":
            score += 0.5
        return score

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
                return text[:6000]
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

        query = str(query).strip()
        if not query:
            return "Error: No search query provided."

        verify = verify or self._looks_time_sensitive(query)
        errors = []

        for provider in self.providers:
            if not provider.available():
                continue
            try:
                results = provider.search(query, max_results=max_results)
                if not results:
                    continue

                ranked = sorted(results, key=lambda item: self._score_result(query, item), reverse=True)
                # Verify only the strongest few sources. This reduces noise and avoids
                # flooding the local model with unrelated pages.
                verify_limit = 3 if verify else 0
                output = [
                    f"RESEARCH QUERY: {query}\n",
                    f"RETRIEVED_AT_UTC: {datetime.now(timezone.utc).isoformat()}\n",
                    "Use the evidence below as the source of truth. Do not invent facts that are not supported by it.\n",
                ]

                for index, result in enumerate(ranked[:max_results], start=1):
                    title = result.get("title", "")
                    href = result.get("href", "")
                    body = result.get("body", "")
                    score = self._score_result(query, result)
                    output.append(
                        f"SOURCE {index} | relevance_score={score:.1f} | provider={result.get('provider', '')}\n"
                        f"TITLE: {title}\nURL: {href}\nSNIPPET: {body}\n"
                    )
                    if verify and index <= verify_limit and href:
                        page_text = self._verify_url(href)
                        output.append(f"VERIFIED_PAGE_TEXT: {page_text}\n")

                return "\n".join(output)
            except Exception as exc:
                errors.append(f"{provider.name}: {exc}")

        if errors:
            return "Web search error: " + " | ".join(errors)
        return "No web search provider is available. Configure BRAVE_SEARCH_API_KEY or install the ddgs package."
