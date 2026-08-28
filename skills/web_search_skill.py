import re
from datetime import datetime, timezone

from skills.base_skill import BaseSkill
from skills.search_providers.brave_provider import BraveSearchProvider
from skills.search_providers.duckduckgo_provider import DuckDuckGoProvider


class WebSearchSkill(BaseSkill):
    name = "web_search"
    description = "Search the web with Brave primary and DuckDuckGo fallback, with strict primary-source verification for current factual queries."
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
                    "verify": {"type": "boolean", "description": "Verify relevant pages before returning evidence"},
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
        markers = ("latest", "current", "today", "now", "recent", "newest", "release", "version", "price", "news", "this week", "this month", "آخر", "حاليا", "اليوم", "جديد", "أحدث", "نسخة", "إصدار")
        return any(marker in q for marker in markers)

    @staticmethod
    def _is_python_release_query(query: str) -> bool:
        q = query.lower()
        return "python" in q and any(k in q for k in ("latest", "current", "release", "version"))

    @staticmethod
    def _keywords(query: str) -> set[str]:
        return {w for w in re.findall(r"[a-z0-9][a-z0-9._+-]*", query.lower()) if len(w) > 1 and w not in {"the", "for", "and", "with", "from", "what", "is", "are"}}

    @classmethod
    def _score_result(cls, query: str, result: dict) -> float:
        title = str(result.get("title", "")).lower()
        body = str(result.get("body", "")).lower()
        url = str(result.get("href", "")).lower()
        haystack = f"{title} {body} {url}"
        keywords = cls._keywords(query)
        score = sum(2 for word in keywords if word in title) + sum(1 for word in keywords if word in body)
        for domain in ("python.org", "docs.python.org", "pypi.org"):
            if domain in url:
                score += 10
                break
        if any(x in query.lower() for x in ("release", "version", "latest")) and any(x in title for x in ("release", "download", "python")):
            score += 5
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
                text = " ".join(page.inner_text("body").split())
                browser.close()
                return text[:8000]
        except Exception as exc:
            return f"Verification failed: {exc}"

    @staticmethod
    def _normalize_query(query: str) -> str:
        if WebSearchSkill._is_python_release_query(query):
            return "site:python.org/downloads/ latest Python release"
        return query.strip()

    @staticmethod
    def _extract_python_release_facts(text: str) -> str:
        """Extract likely release/version facts from verified Python pages only."""
        version_patterns = [
            r"Python\s+(3\.\d+\.\d+)\s+is\s+the\s+latest",
            r"latest\s+(?:stable\s+)?(?:release|version)\s+(?:of\s+)?Python\s+(3\.\d+\.\d+)",
            r"Python\s+(3\.\d+\.\d+)\s+\([^)]*\)\s+is\s+the\s+latest",
            r"Python\s+(3\.\d+\.\d+)\s+released",
        ]
        matches = []
        for pattern in version_patterns:
            matches.extend(re.findall(pattern, text, flags=re.IGNORECASE))
        versions = sorted(set(matches), key=lambda v: tuple(map(int, v.split('.'))), reverse=True)
        if versions:
            return f"VERIFIED_FACT: Latest Python release candidate explicitly stated on official page: Python {versions[0]}"
        return "VERIFIED_FACT: No exact latest Python release version was explicitly extracted from the verified official page."

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
        time_sensitive = self._looks_time_sensitive(query)
        verify = verify or time_sensitive
        python_release = self._is_python_release_query(query)
        search_query = self._normalize_query(query)
        errors = []

        for provider in self.providers:
            if not provider.available():
                continue
            try:
                results = provider.search(search_query, max_results=max_results)
                if not results:
                    continue
                ranked = sorted(results, key=lambda item: self._score_result(query, item), reverse=True)
                if python_release:
                    ranked = [r for r in ranked if "python.org" in str(r.get("href", "")).lower() or "python" in str(r.get("title", "")).lower()]
                    ranked.sort(key=lambda r: ("python.org" not in str(r.get("href", "")).lower(), -self._score_result(query, r)))
                output = [
                    f"RESEARCH QUERY: {query}",
                    f"RETRIEVED_AT_UTC: {datetime.now(timezone.utc).isoformat()}",
                    "EVIDENCE_POLICY: Final answers must use only supported evidence below; do not supplement with model memory.",
                ]
                verified_count = 0
                for index, result in enumerate(ranked[:max_results], start=1):
                    title = result.get("title", "")
                    href = result.get("href", "")
                    body = result.get("body", "")
                    score = self._score_result(query, result)
                    output.append(f"SOURCE {index} | relevance_score={score:.1f} | provider={result.get('provider', '')}\nTITLE: {title}\nURL: {href}\nSNIPPET: {body}")
                    if verify and href and verified_count < 3:
                        page_text = self._verify_url(href)
                        if not page_text.startswith("Verification failed:"):
                            output.append(f"VERIFIED_PAGE_TEXT: {page_text}")
                            if python_release and "python.org" in href.lower():
                                output.append(self._extract_python_release_facts(page_text))
                            verified_count += 1
                return "\n\n".join(output)
            except Exception as exc:
                errors.append(f"{provider.name}: {exc}")
        if errors:
            return "Web search error: " + " | ".join(errors)
        return "No web search provider is available. Configure BRAVE_SEARCH_API_KEY or install the ddgs package."
