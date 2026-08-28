from unittest.mock import Mock, patch

from skills.search_providers.brave_provider import BraveSearchProvider
from skills.search_providers.duckduckgo_provider import DuckDuckGoProvider


def test_brave_unavailable_without_key(monkeypatch):
    monkeypatch.delenv("BRAVE_SEARCH_API_KEY", raising=False)
    assert BraveSearchProvider().available() is False


def test_brave_parses_results():
    response = Mock()
    response.json.return_value = {"web": {"results": [{"title": "Python", "description": "Official", "url": "https://python.org"}]}}
    response.raise_for_status.return_value = None
    with patch("skills.search_providers.brave_provider.requests.get", return_value=response) as get:
        result = BraveSearchProvider(api_key="test").search("python", 1)
    assert result[0]["title"] == "Python"
    assert result[0]["href"] == "https://python.org"
    get.assert_called_once()


def test_duckduckgo_unavailable_without_package():
    with patch.dict("sys.modules", {"ddgs": None}):
        assert DuckDuckGoProvider().available() is False
