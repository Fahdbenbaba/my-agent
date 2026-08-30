import json
import re
import shutil
import subprocess
import urllib.parse
import urllib.request

from skills.base_skill import BaseSkill


class AgentReachSkill(BaseSkill):
    """Bridge the agent to Agent Reach diagnostics and its available backends."""

    name = "agent_reach"
    description = (
        "Use the locally installed Agent Reach stack for web pages, GitHub, YouTube, "
        "RSS, search, diagnostics, and capability discovery."
    )
    schema = {
        "type": "function",
        "function": {
            "name": "agent_reach",
            "description": description,
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["status", "doctor", "capabilities", "read", "search", "github", "youtube", "rss"],
                    },
                    "url": {"type": "string"},
                    "query": {"type": "string"},
                    "max_results": {"type": "integer", "description": "Maximum number of results (1-10)."},
                },
                "required": ["action"],
            },
        },
    }

    CAPABILITIES = {
        "web": "Read public web pages through Jina Reader.",
        "youtube": "Search YouTube with yt-dlp and inspect public video metadata.",
        "rss": "Read RSS and Atom feeds with feedparser.",
        "github": "Search public GitHub repositories and read public GitHub pages.",
        "search": "Use the agent web-search provider abstraction.",
        "social": "Optional social channels depend on local configuration and login state.",
    }

    @staticmethod
    def _cli():
        return shutil.which("agent-reach") or shutil.which("agent-reach.exe")

    @staticmethod
    def _decode_output(value):
        if value is None:
            return ""
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="replace").strip()
        return str(value).strip()

    @classmethod
    def _run_command(cls, command, timeout=120):
        """Run in binary mode and decode explicitly; also supports mocked text output in tests."""
        try:
            completed = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=False,
                timeout=timeout,
                shell=False,
            )
            stdout = cls._decode_output(completed.stdout)
            stderr = cls._decode_output(completed.stderr)
            return completed.returncode, stdout or stderr
        except subprocess.TimeoutExpired:
            return 124, "Command timed out."
        except OSError as exc:
            return 1, f"OS error: {exc}"

    @staticmethod
    def _http_get(url, timeout=30, headers=None):
        request = urllib.request.Request(url, headers=headers or {"User-Agent": "my-agent/1.0"})
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read().decode("utf-8", errors="replace")

    def _read_web(self, url):
        url = str(url).strip()
        if not re.match(r"^https?://", url, re.I):
            return "Agent Reach Error: read requires an http(s) URL."
        try:
            text = self._http_get(
                "https://r.jina.ai/" + url,
                timeout=45,
                headers={"User-Agent": "Mozilla/5.0 my-agent/1.0"},
            )
            return f"AGENT_REACH_WEB_SUCCESS\nURL: {url}\nCONTENT:\n{text[:20000]}"
        except Exception as exc:
            return f"AGENT_REACH_WEB_ERROR\nURL: {url}\nERROR: {exc}"

    def _search_web(self, query, max_results):
        try:
            from skills.web_search_skill import WebSearchSkill
            result = WebSearchSkill().execute({"query": query, "max_results": max_results, "verify": False})
            return f"AGENT_REACH_SEARCH\n{result}"
        except Exception as exc:
            return f"AGENT_REACH_SEARCH_ERROR\nQUERY: {query}\nERROR: {exc}"

    def _github(self, query, url=None, max_results=5):
        target_url = str(url or "").strip()
        if target_url and "github.com" in target_url.lower():
            return self._read_web(target_url)
        query = str(query or "").strip()
        if not query:
            return "Agent Reach Error: github requires a query or GitHub URL."
        encoded = urllib.parse.quote(query)
        api_url = f"https://api.github.com/search/repositories?q={encoded}&per_page={max_results}"
        try:
            payload = json.loads(
                self._http_get(
                    api_url,
                    timeout=30,
                    headers={"Accept": "application/vnd.github+json", "User-Agent": "my-agent/1.0"},
                )
            )
            items = payload.get("items", [])
            if not items:
                return f"AGENT_REACH_GITHUB\nQUERY: {query}\nNo public repositories found."
            lines = ["AGENT_REACH_GITHUB", f"QUERY: {query}"]
            for index, item in enumerate(items[:max_results], 1):
                lines.append(
                    f"REPO {index} | {item.get('full_name', '')}\n"
                    f"URL: {item.get('html_url', '')}\n"
                    f"DESCRIPTION: {item.get('description') or 'No description'}\n"
                    f"STARS: {item.get('stargazers_count', 0)} | LANGUAGE: {item.get('language') or 'unknown'}"
                )
            return "\n\n".join(lines)
        except Exception as exc:
            return f"AGENT_REACH_GITHUB_ERROR\nQUERY: {query}\nERROR: {exc}"

    def _youtube(self, query, url=None, max_results=5):
        executable = shutil.which("yt-dlp") or shutil.which("yt-dlp.exe")
        if not executable:
            return "AGENT_REACH_YOUTUBE_ERROR\nyt-dlp is not available on PATH."
        target = str(url or "").strip()
        if not target:
            query = str(query or "").strip()
            if not query:
                return "Agent Reach Error: youtube requires a query or URL."
            target = f"ytsearch{max_results}:{query}"
        code, output = self._run_command(
            [executable, "--dump-single-json", "--flat-playlist", "--skip-download", target],
            timeout=120,
        )
        if code != 0:
            return f"AGENT_REACH_YOUTUBE_ERROR\n{output[:12000]}"
        try:
            data = json.loads(output)
        except json.JSONDecodeError:
            return f"AGENT_REACH_YOUTUBE\n{output[:12000]}"
        entries = data.get("entries") or [data]
        lines = ["AGENT_REACH_YOUTUBE"]
        for index, item in enumerate(entries[:max_results], 1):
            lines.append(
                f"VIDEO {index} | {item.get('title', 'Unknown title')}\n"
                f"URL: {item.get('webpage_url') or item.get('url', '')}\n"
                f"CHANNEL: {item.get('channel') or item.get('uploader') or 'Unknown'}\n"
                f"DURATION: {item.get('duration') or 'unknown'}"
            )
        return "\n\n".join(lines)

    def _rss(self, url):
        url = str(url or "").strip()
        if not url:
            return "Agent Reach Error: rss requires a feed URL."
        try:
            import feedparser
            feed = feedparser.parse(url)
            if getattr(feed, "bozo", 0) and not getattr(feed, "entries", None):
                return f"AGENT_REACH_RSS_ERROR\nURL: {url}\nERROR: {getattr(feed, 'bozo_exception', 'Invalid feed')}"
            lines = ["AGENT_REACH_RSS", f"URL: {url}", f"TITLE: {feed.feed.get('title', 'Unknown feed')}"]
            for index, entry in enumerate(feed.entries[:10], 1):
                lines.append(
                    f"ITEM {index} | {entry.get('title', 'Untitled')}\n"
                    f"URL: {entry.get('link', '')}\n"
                    f"SUMMARY: {re.sub(r'<[^>]+>', ' ', entry.get('summary', ''))[:1000]}"
                )
            return "\n\n".join(lines)
        except Exception as exc:
            return f"AGENT_REACH_RSS_ERROR\nURL: {url}\nERROR: {exc}"

    def execute(self, arguments: dict) -> str:
        if not isinstance(arguments, dict):
            return "Agent Reach Error: arguments must be a dictionary."
        action = str(arguments.get("action", "status")).strip().lower()
        allowed = {"status", "doctor", "capabilities", "read", "search", "github", "youtube", "rss"}
        if action not in allowed:
            return f"Agent Reach Error: Unsupported action '{action}'."
        if action == "capabilities":
            return json.dumps({"installed": bool(self._cli()), "capabilities": self.CAPABILITIES}, ensure_ascii=False, indent=2)
        cli = self._cli()
        if action in {"status", "doctor"}:
            if not cli:
                return "AGENT_REACH_NOT_INSTALLED\nAgent Reach CLI was not found on PATH."
            if action == "status":
                return f"AGENT_REACH_AVAILABLE\nCLI: {cli}"
            code, output = self._run_command([cli, "doctor", "--json"], timeout=120)
            return f"AGENT_REACH_DOCTOR\nEXIT_CODE: {code}\n{output[:20000]}"
        max_results = 5
        try:
            max_results = max(1, min(int(arguments.get("max_results", 5)), 10))
        except (TypeError, ValueError):
            pass
        url = str(arguments.get("url", "")).strip()
        query = str(arguments.get("query", "")).strip()
        if action == "read":
            return self._read_web(url)
        if action == "search":
            return self._search_web(query, max_results)
        if action == "github":
            return self._github(query, url, max_results)
        if action == "youtube":
            return self._youtube(query, url, max_results)
        return self._rss(url)
