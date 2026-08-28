class Router:
    def route(self, query: str) -> dict:
        query_lower = query.lower().strip()

        # 1. Calculator
        if any(w in query_lower for w in ["calculate", "math", "حساب", "+", "-", "*", "/"]):
            return {
                "use_tool": True,
                "tool": "calculator",
                "arguments": {"expression": query.strip()},
            }

        # 2. File Manager
        elif any(w in query_lower for w in ["file", "files", "dir", "show", "list", "ملف", "ملفات"]):
            return {"use_tool": True, "tool": "file_manager", "arguments": {"query": query}}

        # 3. Memory
        elif any(w in query_lower for w in ["remember", "recall", "memory", "what", "who", "whats", "شكون", "شنو", "حفظ", "ذاكرة"]):
            return {"use_tool": True, "tool": "memory", "arguments": {"query": query}}

        # 4. Web Search
        elif any(w in query_lower for w in ["search", "google", "web", "بحث", "ابحث"]):
            return {"use_tool": True, "tool": "web_search", "arguments": {"query": query}}

        # 5. Git Skill
        elif any(w in query_lower for w in ["git", "commit", "repo", "github"]):
            return {"use_tool": True, "tool": "git", "arguments": {"query": query}}

        # 6. Database Skill
        elif any(w in query_lower for w in ["db", "database", "sql", "sqlite", "قاعدة"]):
            return {"use_tool": True, "tool": "database", "arguments": {"query": query}}

        # 7. Browser Skill
        elif any(w in query_lower for w in ["browser", "open url", "site", "موقع", "متصفح"]):
            return {"use_tool": True, "tool": "browser", "arguments": {"query": query}}

        # 8. Python Sandbox Skill
        elif any(w in query_lower for w in ["python", "code", "run script", "sandbox", "سكربت"]):
            return {"use_tool": True, "tool": "python_sandbox", "arguments": {"query": query}}

        return {"use_tool": False}
