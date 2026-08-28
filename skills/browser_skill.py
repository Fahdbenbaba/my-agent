from urllib.parse import urlparse

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from skills.base_skill import BaseSkill


class BrowserSkill(BaseSkill):
    name = "browser_automation"
    description = "Control a real Chromium browser to navigate websites, inspect pages, extract text/links, and capture screenshots."
    schema = {
        "type": "function",
        "function": {
            "name": "browser_automation",
            "description": description,
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The URL to navigate to."},
                    "action": {
                        "type": "string",
                        "enum": ["get_text", "get_info", "get_links", "screenshot"],
                        "description": "What to do after navigation. Defaults to get_text.",
                    },
                    "wait_ms": {
                        "type": "integer",
                        "description": "Extra time to wait after navigation, in milliseconds (0-10000).",
                    },
                },
                "required": ["url"],
            },
        },
    }

    @staticmethod
    def _validate_url(url: str) -> str:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ValueError("URL must start with http:// or https:// and include a hostname.")
        return url

    def execute(self, arguments: dict) -> str:
        if not isinstance(arguments, dict):
            return "Browser Automation Error: arguments must be a dictionary."

        url = str(arguments.get("url", "")).strip()
        action = str(arguments.get("action", "get_text")).strip().lower()
        try:
            wait_ms = max(0, min(int(arguments.get("wait_ms", 0)), 10000))
        except (TypeError, ValueError):
            wait_ms = 0

        if not url:
            return "Browser Automation Error: No URL provided."
        if action not in {"get_text", "get_info", "get_links", "screenshot"}:
            return f"Browser Automation Error: Unsupported action '{action}'."

        try:
            url = self._validate_url(url)
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(viewport={"width": 1440, "height": 900})
                try:
                    response = page.goto(url, wait_until="domcontentloaded", timeout=60000)
                    if wait_ms:
                        page.wait_for_timeout(wait_ms)

                    status = response.status if response else None
                    final_url = page.url
                    title = page.title()

                    if action == "screenshot":
                        path = "browser_screenshot.png"
                        page.screenshot(path=path, full_page=True)
                        return f"BROWSER_SUCCESS\nURL: {final_url}\nTITLE: {title}\nHTTP_STATUS: {status}\nSCREENSHOT: {path}"

                    if action == "get_info":
                        text = " ".join(page.locator("body").inner_text().split())
                        return (
                            f"BROWSER_SUCCESS\nURL: {final_url}\nTITLE: {title}\n"
                            f"HTTP_STATUS: {status}\nTEXT: {text[:5000]}"
                        )

                    if action == "get_links":
                        links = page.locator("a").evaluate_all(
                            "els => els.slice(0, 100).map(a => ({text: (a.innerText || '').trim(), href: a.href}))"
                        )
                        lines = [f"- {item.get('text') or '[no text]'} -> {item.get('href')}" for item in links]
                        return (
                            f"BROWSER_SUCCESS\nURL: {final_url}\nTITLE: {title}\nHTTP_STATUS: {status}\n"
                            "LINKS:\n" + "\n".join(lines)
                        )

                    text = " ".join(page.locator("body").inner_text().split())
                    return (
                        f"BROWSER_SUCCESS\nURL: {final_url}\nTITLE: {title}\nHTTP_STATUS: {status}\n"
                        f"TEXT: {text[:10000]}"
                    )
                finally:
                    browser.close()

        except PlaywrightTimeoutError as exc:
            return f"Browser Automation Error: Navigation timed out after 60 seconds. Details: {exc}"
        except Exception as exc:
            message = str(exc)
            if "Executable doesn't exist" in message or "executable doesn't exist" in message:
                return (
                    "Browser Automation Error: Chromium is not installed for Playwright. "
                    "Run `python -m playwright install chromium` once, then retry."
                )
            return f"Browser Automation Error: {message}"
