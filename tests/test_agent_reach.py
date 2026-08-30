from unittest.mock import patch
from skills.agent_reach_skill import AgentReachSkill


def test_capabilities_work_without_cli():
    result = AgentReachSkill().execute({"action": "capabilities"})
    assert "capabilities" in result
    assert "github" in result


@patch("skills.agent_reach_skill.shutil.which")
def test_status_reports_missing_cli(mock_which):
    mock_which.return_value = None
    result = AgentReachSkill().execute({"action": "status"})
    assert result.startswith("AGENT_REACH_NOT_INSTALLED")


def test_rejects_unknown_action():
    assert "Unsupported action" in AgentReachSkill().execute({"action": "install"})
