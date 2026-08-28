# skills/browser_skill.py
from playwright.sync_api import sync_playwright
from skills.base_skill import BaseSkill

class BrowserSkill(BaseSkill):
    def get_name(self) -> str:
        return "browser_automation"

    def get_description(self) -> str:
        return "Automate a browser to navigate websites, click elements, fill forms, or extract text content."

    def get_schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.get_name(),
                "description": self.get_description(),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "The URL to navigate to."
                        },
                        "action": {
                            "type": "string",
                            "enum": ["get_text", "screenshot"],
                            "description": "The action to perform on the page."
                        }
                    },
                    "required": ["url", "action"]
                }
            }
        }

    def execute(self, args: dict) -> str:
        url = args.get("url")
        action = args.get("action")
        
        if not url:
            return "Error: No URL provided."

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, timeout=60000)
                
                if action == "screenshot":
                    path = "screenshot.png"
                    page.screenshot(path=path)
                    browser.close()
                    return f"Screenshot successfully saved to {path}."
                
                elif action == "get_text" or not action:
                    content = page.inner_text("body")
                    browser.close()
                    # Limit output length to prevent token overflow
                    return content[:3000] + ("..." if len(content) > 3000 else "")
                
                browser.close()
                return "Action executed successfully."
        except Exception as e:
            return f"Browser Automation Error: {str(e)}"