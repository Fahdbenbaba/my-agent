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

        # 2. Explicit Agent Reach requests.
        if any(w in query_lower for w in [
            "agent reach", "agent-reach", "reach doctor", "reach status",
            "internet capabilities", "internet reach"
        ]):
            action = "doctor" if "doctor" in query_lower else (
                "capabilities" if "capabilit" in query_lower else "status"
            )
            return {"use_tool": True, "tool": "agent_reach", "arguments": {"action": action}}

        # 3. Native continuous skill learning.
        learning_list_intent = any(w in query_lower for w in [
            "list learned skills", "show learned skills", "list skills", "/skills"
        ])
        learning_search_intent = any(w in query_lower for w in [
            "search learned skills", "search a learned skill", "find learned skill",
            "find a learned skill", "search skills for", "find skills for"
        ])
        learning_save_intent = any(w in query_lower for w in [
            "save this as a skill", "save what we learned as a skill",
            "extract a skill from this", "extract this as a skill",
            "create a skill from this", "save what we learned"
        ])
        learning_recall_intent = any(w in query_lower for w in [
            "what did we learn", "what have we learned"
        ])

        if learning_list_intent or learning_search_intent or learning_save_intent or learning_recall_intent:
            if learning_search_intent or learning_recall_intent:
                search_query = text
                search_query = re.sub(
                    r"(?i)^.*?\b(?:search|find)\s+(?:a\s+)?learned\s+skill(?:s)?\s*(?:for|about|matching)?\s*",
                    "",
                    search_query,
                ).strip()
                search_query = search_query or text
                return {"use_tool": True, "tool": "skill_learning", "arguments": {"action": "search", "query": search_query}}
            if learning_list_intent:
                return {"use_tool": True, "tool": "skill_learning", "arguments": {"action": "list", "query": text}}
            return {"use_tool": True, "tool": "skill_learning", "arguments": {"action": "save", "query": text}}

        # 4. Agent Reach web/GitHub/YouTube/RSS intent.
        url_match = re.search(r"https?://\S+", text, re.I)
        clean_url = url_match.group(0).rstrip(".,)") if url_match else ""

        read_intent = any(w in query_lower for w in [
            "read this", "read url", "read the page", "read this page", "read the url",
            "fetch this", "fetch url", "fetch the page", "fetch the url",
            "scrape this", "extract from", "get content from", "analyze this page",
        ])
        if clean_url and re.match(r"^(read|fetch|scrape)\b", query_lower):
            read_intent = True

        github_intent = "github" in query_lower or "git hub" in query_lower
        youtube_intent = any(w in query_lower for w in ["youtube", "youtube video", "youtube videos"])
        rss_intent = any(w in query_lower for w in ["rss feed", "atom feed", "rss", "atom"])
        search_github = github_intent and any(w in query_lower for w in ["search", "find", "look for", "look up", "repositories", "repo", "repos"])
        search_youtube = youtube_intent and any(w in query_lower for w in ["search", "find", "look for", "videos", "video"])

        if search_github:
            search_query = re.sub(r"(?i)\b(?:search|find|look for|look up)\s+(?:on\s+)?github\s*(?:for|:)?\s*", "", text).strip() or text
            return {"use_tool": True, "tool": "agent_reach", "arguments": {"action": "github", "query": search_query}}
        if github_intent and clean_url:
            return {"use_tool": True, "tool": "agent_reach", "arguments": {"action": "github", "url": clean_url}}
        if search_youtube:
            search_query = re.sub(r"(?i)\b(?:search|find|look for)\s+(?:on\s+)?youtube\s*(?:for|:)?\s*", "", text).strip() or text
            return {"use_tool": True, "tool": "agent_reach", "arguments": {"action": "youtube", "query": search_query}}
        if youtube_intent and clean_url:
            return {"use_tool": True, "tool": "agent_reach", "arguments": {"action": "youtube", "url": clean_url}}
        if rss_intent and clean_url:
            return {"use_tool": True, "tool": "agent_reach", "arguments": {"action": "rss", "url": clean_url}}
        if read_intent and clean_url:
            return {"use_tool": True, "tool": "agent_reach", "arguments": {"action": "read", "url": clean_url}}

        # 5. OpenConnector runtime.
        if any(w in query_lower for w in ["openconnector", "open connector", "connector health", "connector providers", "connector actions", "connector test", "oauth", "connect github"]):
            if "self test" in query_lower or "self-test" in query_lower or "smoke test" in query_lower or "connector test" in query_lower:
                action = "self_test"
            elif "health" in query_lower:
                action = "health"
            elif "provider" in query_lower:
                action = "providers"
            elif "oauth" in query_lower:
                action = "oauth_configs"
            elif "connect" in query_lower and "github" in query_lower:
                action = "connections"
            elif "search" in query_lower:
                action = "search_actions"
            else:
                action = "list_actions"
            return {"use_tool": True, "tool": "open_connector", "arguments": {"action": action, "query": text}}

        # 6. Browser/navigation.
        browser_patterns = ["open url", "open website", "open site", "open http", "open https", "browse to", "visit", "go to", "browser", "موقع", "متصفح"]
        if url_match or any(w in query_lower for w in browser_patterns):
            url = clean_url if url_match else text
            return {"use_tool": True, "tool": "browser", "arguments": {"url": url}}

        # 7. Database.
        database_patterns = ["create sqlite database", "create a sqlite database", "create database", "create a database", "database", "sqlite", "sql query", "run sql", "execute sql", "db", "قاعدة بيانات"]
        if any(w in query_lower for w in database_patterns):
            sql = text
            create_db = re.search(r"create\s+(?:a\s+)?(?:sqlite\s+)?database\s+(?:called|named)?\s*['\"]?([^'\"\s]+)['\"]?", text, re.I)
            if create_db:
                db_name = create_db.group(1).strip()
                sql = "CREATE TABLE IF NOT EXISTS _agent_metadata (name TEXT PRIMARY KEY)"
                return {"use_tool": True, "tool": "database", "arguments": {"query": sql, "db_path": db_name}}
            return {"use_tool": True, "tool": "database", "arguments": {"query": sql}}

        # 8. Git. Only local git commands here; GitHub research is routed above.
        git_patterns = ["git status", "git diff", "git log", "git branch", "git commit", "git add", "git restore", "git checkout", "git repo", "git repository", "repository status", "repo status", "git"]
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

        # 9. Calculator
        if any(w in query_lower for w in ["calculate", "math", "حساب", "+", "-", "*", "/"]):
            return {"use_tool": True, "tool": "calculator", "arguments": {"expression": text}}

        # 10. Memory
        memory_words = ["remember", "recall", "memory", "what do you remember", "what do you know about me", "what did you remember", "retrieve", "remember about me", "what is my", "what's my", "tell me about me", "my favorite", "شنو كتفكر", "شنو كتعرف عليا", "شكون أنا", "حفظ", "ذاكرة"]
        if any(w in query_lower for w in memory_words):
            store_prefixes = ["remember that ", "remember ", "please remember that ", "please remember "]
            explicit_store = any(query_lower.startswith(prefix) for prefix in store_prefixes)
            retrieval_patterns = ["what do you remember", "what do you know about me", "what did you remember", "recall", "retrieve", "remember about me", "what is my", "what's my", "tell me about me", "my favorite", "شنو كتفكر", "شنو كتعرف عليا", "شكون أنا"]
            action = "store" if explicit_store else ("retrieve" if any(w in query_lower for w in retrieval_patterns) else "store")
            memory_text = text
            if action == "store":
                for prefix in store_prefixes:
                    if memory_text.lower().startswith(prefix):
                        memory_text = memory_text[len(prefix):].strip()
                        break
            return {"use_tool": True, "tool": "memory", "arguments": {"action": action, "text": memory_text}}

        # 11. File Manager
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

        # 12. Web Search
        if any(w in query_lower for w in ["search", "google", "web", "بحث", "ابحث"]):
            return {"use_tool": True, "tool": "web_search", "arguments": {"query": text}}

        return {"use_tool": False}
