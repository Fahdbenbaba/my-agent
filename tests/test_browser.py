from unittest.mock import MagicMock, patch

from skills.browser_skill import BrowserSkill


def test_browser_url_validation():
    assert BrowserSkill._validate_url("https://www.python.org") == "https://www.python.org"


def test_browser_rejects_invalid_url():
    result = BrowserSkill().execute({"url": "not-a-url"})
    assert result.startswith("Browser Automation Error:")


def test_browser_rejects_unsupported_action():
    result = BrowserSkill().execute({"url": "https://example.com", "action": "delete"})
    assert "Unsupported action" in result
