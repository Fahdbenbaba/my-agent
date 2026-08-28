from unittest.mock import MagicMock, patch

from agent.core import AgentCore


def test_normalize_arguments_dict():
    assert AgentCore._normalize_arguments({"query": "x"}) == {"query": "x"}


def test_normalize_arguments_json():
    assert AgentCore._normalize_arguments('{"query":"x"}') == {"query": "x"}


def test_extract_url():
    assert AgentCore._extract_url("Open https://www.python.org.") == "https://www.python.org"


def test_extract_txt_filename():
    assert AgentCore._extract_txt_filename("create python_latest.txt") == "python_latest.txt"


def test_unknown_skill_is_reported():
    core = object.__new__(AgentCore)
    core.skills = {}
    assert "Unknown tool" in core._execute_skill("missing", {})
