import re


class Router:
    def route(self, query: str) -> dict:
        text = query.strip()
        query_lower = text.lower()

        # 1. Python execution
        python_patterns = [
            "run python", "python code", "python script", "run script",
            "python sandbox", "execute python", "execute code", "run code",
            "with python", "using python", "سكربت بايثون", "كود بايثون"
        ]
        if any(w in query_lower for w in python_patterns):
            code = text
            match = re.search(r"(?:python\s*(?:code|script)?\s*[:\-]?\s*)(.*)$", text, re.I | re.S)
            if match and match.group(1).strip():
                code = match.group(1).strip()
            else:
                match = re.search(r"(?:run|execute)\s+(?:python\s+)?(?:code|script)?\s*[:\-]?\s*(.*)$", text, re.I | re.S)
                if match and match.group(1).strip():
                    code = match.group(1).strip()
            return {"use_tool": True, "tool": "python_sandbox", "arguments": {"code": code}}

        # 2. Browser/navigation
        url_match = re.search(r"https?://\S+", text, re.I)
        browser_patterns = ["open url", "open website", "open site", "open http", "open https", "browse to", "visit", "go to", "browser", "موقع", "متصفح"]
        if url_match or any(w in query_lower for w in browser_patterns):
            url = url_match.group(0).rstrip(".,)") if url_match else text
            return {"use_tool": True, "tool": "browser", "arguments": {"url": url}}

        # 3. Database: use explicit DB/SQL intent before generic file/list words.
        database_patterns = ["create sqlite database", "create a sqlite database", "create database", "create a database", "database", "sqlite", "sql query", "run sql", "execute sql", "db", "قاعدة بيانات"]
        if any(w in query_lower for w in database_patterns):
            sql = text
            create_db = re.search(r"create\s+(?:a\s+)?(?:sqlite\s+)?database\s+(?:called|named)?\s*['\"]?([^'\"\s]+)['\"]?", text, re.I)
            if create_db:
                db_name = create_db.group(1).strip()
                sql = "CREATE TABLE IF NOT EXISTS _agent_metadata (name TEXT PRIMARY KEY)"
                return {"use_tool": True, "tool": "database", "arguments": {"query": sql, "db_path": db_name}}
            return {"use_tool": True, "tool": "database", "arguments": {"query": sql}}

        # 4. Git: explicit Git intent before generic file/list words.
        git_patterns = ["git status", "git diff", "git log", "git branch", "git commit", "git add", "git restore", "git checkout", "git repo", "git repository", "repository status", "repo status", "github", "git"]
        if any(w in query_lower for w in git_patterns):
            if "status" in query_lower:
                command = "status"
            elif "diff" in query_lower:
                command = "diff"
            elif "log" in query_lower:
                command = "log"
            elif "branch" in query_lower:
                command = "branch"
            else:
                command = "status"
            return {"use_tool": True, "tool": "git_manager", "arguments": {"command": command}}

        # 5. Calculator
        if any(w in query_lower for w in ["calculate", "math", "حساب", "+", "-", "*", "/"]):
            return {"use_tool": True, "tool": "calculator", "arguments": {"expression": text}}

        # 6. Memory
        memory_words = ["remember", "recall", "memory", "what do you remember", "what do you know about me", "what did you remember", "retrieve", "remember about me", "what is my", "what's my", "tell me about me", "my favorite", "شنو كتفكر", "شنو كتعرف عليا", "شكون أنا", "حفظ", "ذاكرة"]
        if any(w in query_lower for w in memory_words):
            retrieval_patterns = ["what do you remember", "what do you know about me", "what did you remember", "recall", "retrieve", "remember about me", "what is my", "what's my", "tell me about me", "my favorite", "شنو كتفكر", "شنو كتعرف عليا", "شكون أنا"]
            action = "retrieve" if any(w in query_lower for w in retrieval_patterns) else "store"
            memory_text = text
            if action == "store":
                for prefix in ["remember that ", "remember ", "please remember that ", "please remember "]:
                    if memory_text.lower().startswith(prefix):
                        memory_text = memory_text[len(prefix):].strip()
                        break
            return {"use_tool": True, "tool": "memory", "arguments": {"action": action, "text": memory_text}}

        # 7. File Manager
        file_words = ["file", "files", "dir", "directory", "folder", "show", "list", "create file", "make a file", "write to", "read file", "ملف", "ملفات"]
        if any(w in query_lower for w in file_words):
            create_match = re.search(r"(?:create|make|write)\s+(?:a\s+)?file\s+(?:called|named)?\s*['\"]?([^'\"\s]+)['\"]?\s+(?:with|containing)\s+(?:the\s+)?(?:text|content)?\s*[:=]?\s*['\"]?(.*?)['\"]?$", text, re.I)
            if create_match:
                return {"use_tool": True, "tool": "file_manager", "arguments": {"action": "create", "filepath": create_match.group(1).strip(), "content": create_match.group(2).strip().strip("'\"")}}
            if any(w in query_lower for w in ["list", "show", "files", "directory", "folder", "dir"]):
                return {"use_tool": True, "tool": "file_manager", "arguments": {"action": "list", "filepath": "."}}
            read_match = re.search(r"(?:read|open|show)\s+(?:the\s+)?file\s+['\"]?([^'\"\s]+)", text, re.I)
            if read_match:
                return {"use_tool": True, "tool": "file_manager", "arguments": {"action": "read", "filepath": read_match.group(1).strip()}}
            return {"use_tool": True, "tool": "file_manager", "arguments": {"action": "list", "filepath": "."}}

        # 8. Web Search
        if any(w in query_lower for w in ["search", "google", "web", "بحث", "ابحث"]):
            return {"use_tool": True, "tool": "web_search", "arguments": {"query": text}}

        return {"use_tool": False}
