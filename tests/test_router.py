from agent.router import Router


def test_router_python():
    result = Router().route("Run Python code: print(10 * 20)")
    assert result["tool"] == "python_sandbox"
    assert result["arguments"]["code"] == "print(10 * 20)"


def test_router_browser():
    result = Router().route("Open https://www.python.org")
    assert result["tool"] == "browser"
    assert result["arguments"]["url"] == "https://www.python.org"


def test_router_database():
    result = Router().route("Create a SQLite database called test.db")
    assert result["tool"] == "database"
    assert result["arguments"]["db_path"] == "test.db"


def test_router_git():
    result = Router().route("Show me the git status of this repository")
    assert result["tool"] == "git_manager"
    assert result["arguments"]["command"] == "status"


def test_router_memory():
    result = Router().route("remember that my favorite language is Python")
    assert result["tool"] == "memory"
    assert result["arguments"]["action"] == "store"


def test_router_search():
    result = Router().route("Search the web for the latest Python release")
    assert result["tool"] == "web_search"


def test_router_agent_reach_read():
    result = Router().route("Read https://example.com")
    assert result["tool"] == "agent_reach"
    assert result["arguments"] == {"action": "read", "url": "https://example.com"}


def test_router_agent_reach_github():
    result = Router().route("Search GitHub for qwen")
    assert result["tool"] == "agent_reach"
    assert result["arguments"]["action"] == "github"
    assert result["arguments"]["query"] == "qwen"


def test_router_agent_reach_youtube():
    result = Router().route("Search YouTube for Python tutorials")
    assert result["tool"] == "agent_reach"
    assert result["arguments"]["action"] == "youtube"
    assert result["arguments"]["query"] == "Python tutorials"


def test_router_agent_reach_rss():
    result = Router().route("Read this RSS feed https://example.com/feed.xml")
    assert result["tool"] == "agent_reach"
    assert result["arguments"]["action"] == "rss"
    assert result["arguments"]["url"] == "https://example.com/feed.xml"


def test_router_unknown():
    assert Router().route("hello there")["use_tool"] is False
