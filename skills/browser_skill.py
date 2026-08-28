from playwright.sync_api import sync_playwright
from skills.base_skill import BaseSkill


class BrowserSkill(BaseSkill):
    name = "browser_automation"
    description = "Automate a browser to navigate websites and extract text or screenshots."
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
                        "enum": ["get_text", "screenshot"],
                        "description": "The action to perform on the page. Defaults to get_text.",
                    },
                },
                "required": ["url"],
            },
        },
    }

    def execute(self, arguments: dict) -> str:
        url = arguments.get("url") if isinstance(arguments, dict) else None
        action = arguments.get("action", "get_text") if isinstance(arguments, dict) else "get_text"
        if not url:
            return "Error: No URL provided."

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, wait_until="domcontentloaded", timeout=60000)

                if action == "screenshot":
                    path = "screenshot.png"
                    page.screenshot(path=path)
                    browser.close()
                    return f"Screenshot successfully saved to {path}."

                content = page.inner_text("body")
                browser.close()
                return content[:5000] + ("..." if len(content) > 5000 else "")
        except Exception as e:
            return f"Browser Automation Error: {str(e)}"
