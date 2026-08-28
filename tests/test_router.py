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


def test_router_unknown():
    assert Router().route("hello there")["use_tool"] is False
