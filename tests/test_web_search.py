from unittest.mock import MagicMock, patch

from skills.web_search_skill import WebSearchSkill


def test_python_release_query_is_time_sensitive():
    assert WebSearchSkill._looks_time_sensitive("latest Python release")
    assert WebSearchSkill._is_python_release_query("latest Python release")


def test_score_prefers_python_org():
    query = "latest Python release"
    official = {"title": "Python Releases", "body": "Latest Python release", "href": "https://www.python.org/downloads/", "provider": "duckduckgo"}
    unrelated = {"title": "Latest Python news", "body": "news", "href": "https://example.com/python", "provider": "duckduckgo"}
    assert WebSearchSkill._score_result(query, official) > WebSearchSkill._score_result(query, unrelated)


def test_extract_python_release_fact():
    text = "Latest Python 3 Release - Python 3.14.7"
    result = WebSearchSkill._extract_python_release_facts(text)
    assert "Python 3.14.7" in result


def test_empty_query():
    assert WebSearchSkill().execute({"query": ""}) == "Error: No search query provided."
