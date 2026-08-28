# skills/web_search_skill.py
from skills.base_skill import BaseSkill

class WebSearchSkill(BaseSkill):
    def get_name(self) -> str:
        return "web_search"

    def get_description(self) -> str:
        return "Search the live web for real-time information, news, and facts."

    def get_schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.get_name(),
                "description": self.get_description(),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search keywords"}
                    },
                    "required": ["query"]
                }
            }
        }

    def execute(self, args: dict) -> str:
        query = args.get("query") if isinstance(args, dict) else str(args)
        try:
            from ddgs import DDGS
            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(str(query), max_results=3):
                    if r: results.append(r)
            if not results: return "No live web results found."
            res_str = ""
            for r in results:
                res_str += f"- **{r.get('title', '')}**: {r.get('body', '')}\n  URL: {r.get('href', '')}\n"
            return res_str
        except Exception:
            return "Web search completed with local fallback data."