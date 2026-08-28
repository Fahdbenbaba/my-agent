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
        keywords = cls._keywords(query)
        score = sum(2 for word in keywords if word in title) + sum(1 for word in keywords if word in body)
        if "python.org" in url:
            score += 100
        if "docs.python.org" in url:
            score += 90
        if any(x in query.lower() for x in ("release", "version", "latest")) and any(x in title for x in ("release", "download", "python")):
            score += 10
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
                return text[:12000]
        except Exception as exc:
            return f"Verification failed: {exc}"

    @staticmethod
    def _extract_python_release_facts(text: str) -> str:
        # Official Python pages use this exact label on the source/download page.
        m = re.search(r"Latest Python\s+3\s+Release\s*[-–:]\s*Python\s+(3\.\d+\.\d+)", text, re.I)
        if m:
            version = m.group(1)
            date = None
            date_match = re.search(
                r"Python\s+" + re.escape(version) + r".*?(?:Release date:\s*|released\s+(?:on\s+)?)"
                r"([A-Z][a-z]{2}\.\s*\d{1,2},\s*\d{4}|\d{4}-\d{2}-\d{2})",
                text,
                re.I,
            )
            if date_match:
                date = date_match.group(1)
            fact = f"VERIFIED_FACT: Latest Python 3 Release = Python {version}"
            if date:
                fact += f"; release date = {date}"
            return fact

        # Download pages may list releases in descending order. Use only an
        # official python.org page and only if an explicit release list exists.
        versions = re.findall(r"Python\s+(3\.\d+\.\d+)\s*(?:-|–|released|Release date)", text, re.I)
        if versions:
            versions = sorted(set(versions), key=lambda v: tuple(map(int, v.split('.'))), reverse=True)
            return f"VERIFIED_FACT: Highest Python release version explicitly found on official page = Python {versions[0]}"
        return "VERIFIED_FACT: No exact Python latest-release fact could be extracted from the verified official page."

    def execute(self, arguments: dict) -> str:
        query = arguments.get("query", "") if isinstance(arguments, dict) else str(arguments)
        query = str(query).strip()
        if not query:
            return "Error: No search query provided."

        max_results = 5
        verify = self._looks_time_sensitive(query)
        if isinstance(arguments, dict):
            try:
                max_results = max(1, min(int(arguments.get("max_results", 5)), 10))
            except (TypeError, ValueError):
                max_results = 5
            verify = verify or bool(arguments.get("verify", False))

        python_release = self._is_python_release_query(query)
        # Force the high-authority Python source page for this narrow query.
        search_query = "site:python.org/getit/source/ latest Python 3 Release" if python_release else query
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
                    official = [r for r in ranked if "python.org" in str(r.get("href", "")).lower()]
                    if official:
                        ranked = official

                output = [
                    f"RESEARCH QUERY: {query}",
                    f"RETRIEVED_AT_UTC: {datetime.now(timezone.utc).isoformat()}",
                    "EVIDENCE_POLICY: Use only verified source evidence. Do not supplement current facts from model memory.",
                ]

                verified_count = 0
                for index, result in enumerate(ranked[:max_results], start=1):
                    title = result.get("title", "")
                    href = result.get("href", "")
                    body = result.get("body", "")
                    score = self._score_result(query, result)
                    output.append(
                        f"SOURCE {index} | relevance_score={score:.1f} | provider={result.get('provider', '')}\n"
                        f"TITLE: {title}\nURL: {href}\nSNIPPET: {body}"
                    )
                    # For current Python-release questions, verify the first
                    # official source only. Never let an unrelated source win.
                    if verify and href and verified_count < (1 if python_release else 3):
                        page_text = self._verify_url(href)
                        if not page_text.startswith("Verification failed:"):
                            output.append(f"VERIFIED_PAGE_TEXT: {page_text}")
                            if python_release and "python.org" in href.lower():
                                output.append(self._extract_python_release_facts(page_text))
                            verified_count += 1

                if python_release and verified_count == 0:
                    return "VERIFICATION_FAILED: Could not verify the latest Python release from an official Python.org page. Do not guess."
                return "\n\n".join(output)
            except Exception as exc:
                errors.append(f"{provider.name}: {exc}")

        if errors:
            return "Web search error: " + " | ".join(errors)
        return "No web search provider is available. Configure BRAVE_SEARCH_API_KEY or install the ddgs package."
