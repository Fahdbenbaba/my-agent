import re


class Router:
    def route(self, query: str) -> dict:
        text = query.strip()
        query_lower = text.lower()

        # 1. Python execution must take priority over calculator keywords.
        # Example: "Run Python code: print(10 * 20)" contains "*" and
        # "calculate"-like language, but the requested operation is execution.
        python_patterns = [
            "run python", "python code", "python script", "run script",
            "python sandbox", "execute python", "execute code", "run code",
            "with python", "using python", "سكربت بايثون", "كود بايثون"
        ]
        if any(w in query_lower for w in python_patterns):
            code = text
            match = re.search(r"(?:python\s*(?:code|script)?\s*[:\-]?\s*)(.*)$", text, re.IGNORECASE | re.DOTALL)
            if match and match.group(1).strip():
                code = match.group(1).strip()
            else:
                match = re.search(r"(?:run|execute)\s+(?:python\s+)?(?:code|script)?\s*[:\-]?\s*(.*)$", text, re.IGNORECASE | re.DOTALL)
                if match and match.group(1).strip():
                    code = match.group(1).strip()

            return {
                "use_tool": True,
                "tool": "python_sandbox",
                "arguments": {"code": code},
            }

        # 2. Calculator
        if any(w in query_lower for w in ["calculate", "math", "حساب", "+", "-", "*", "/"]):
            return {
                "use_tool": True,
                "tool": "calculator",
                "arguments": {"expression": text},
            }

        # 3. Memory
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
            memory_text = text
            if action == "store":
                for prefix in ["remember that ", "remember ", "please remember that ", "please remember "]:
                    if memory_text.lower().startswith(prefix):
                        memory_text = memory_text[len(prefix):].strip()
                        break
            return {
                "use_tool": True,
                "tool": "memory",
                "arguments": {"action": action, "text": memory_text},
            }

        # 4. File Manager — structured routing for create/read/list.
        file_words = ["file", "files", "dir", "directory", "folder", "show", "list", "create file", "make a file", "write to", "read file", "ملف", "ملفات"]
        if any(w in query_lower for w in file_words):
            create_match = re.search(
                r"(?:create|make|write)\s+(?:a\s+)?file\s+(?:called|named)?\s*['\"]?([^'\"\s]+)['\"]?\s+(?:with|containing)\s+(?:the\s+)?(?:text|content)?\s*[:=]?\s*['\"]?(.*?)['\"]?$",
                text,
                re.IGNORECASE,
            )
            if create_match:
                return {
                    "use_tool": True,
                    "tool": "file_manager",
                    "arguments": {
                        "action": "create",
                        "filepath": create_match.group(1).strip(),
                        "content": create_match.group(2).strip().strip("'\""),
                    },
                }
            if any(w in query_lower for w in ["list", "show", "files", "directory", "folder", "dir"]):
                return {"use_tool": True, "tool": "file_manager", "arguments": {"action": "list", "filepath": "."}}
            read_match = re.search(r"(?:read|open|show)\s+(?:the\s+)?file\s+['\"]?([^'\"\s]+)", text, re.IGNORECASE)
            if read_match:
                return {"use_tool": True, "tool": "file_manager", "arguments": {"action": "read", "filepath": read_match.group(1).strip()}}
            return {"use_tool": True, "tool": "file_manager", "arguments": {"action": "list", "filepath": "."}}

        # 5. Web Search
        if any(w in query_lower for w in ["search", "google", "web", "بحث", "ابحث"]):
            return {"use_tool": True, "tool": "web_search", "arguments": {"query": text}}

        # 6. Git Skill
        if any(w in query_lower for w in ["git", "commit", "repo", "github"]):
            return {"use_tool": True, "tool": "git", "arguments": {"query": text}}

        # 7. Database Skill
        if any(w in query_lower for w in ["db", "database", "sql", "sqlite", "قاعدة"]):
            return {"use_tool": True, "tool": "database", "arguments": {"query": text}}

        # 8. Browser Skill
        if any(w in query_lower for w in ["browser", "open url", "site", "موقع", "متصفح"]):
            return {"use_tool": True, "tool": "browser", "arguments": {"query": text}}

        return {"use_tool": False}
