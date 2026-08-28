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

        # 2. Memory — check before generic words such as "what" or "show".
        memory_words = [
            "remember", "recall", "memory", "what do you remember",
            "what do you know about me", "what did you remember",
            "retrieve", "remember about me", "what is my", "what's my",
            "tell me about me", "my favorite", "شنو كتفكر", "شنو كتعرف عليا",
            "شكون أنا", "حفظ", "ذاكرة"
        ]
        if any(w in query_lower for w in memory_words):
            retrieval_patterns = [
                "what do you remember", "what do you know about me",
                "what did you remember", "recall", "retrieve", "remember about me",
                "what is my", "what's my", "tell me about me", "my favorite",
                "شنو كتفكر", "شنو كتعرف عليا", "شكون أنا"
            ]
            is_retrieval = any(w in query_lower for w in retrieval_patterns)
            action = "retrieve" if is_retrieval else "store"

            text = query.strip()
            if action == "store":
                for prefix in ["remember that ", "remember ", "please remember that ", "please remember "]:
                    if text.lower().startswith(prefix):
                        text = text[len(prefix):].strip()
                        break

            return {
                "use_tool": True,
                "tool": "memory",
                "arguments": {"action": action, "text": text},
            }

        # 3. File Manager
        elif any(w in query_lower for w in ["file", "files", "dir", "show", "list", "ملف", "ملفات"]):
            return {"use_tool": True, "tool": "file_manager", "arguments": {"query": query}}

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
