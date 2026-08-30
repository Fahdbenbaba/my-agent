from unittest.mock import patch

from skills.agent_reach_skill import AgentReachSkill


def test_capabilities_work_without_cli():
    result = AgentReachSkill().execute({"action": "capabilities"})
    assert "capabilities" in result
    assert "github" in result
    assert "read" in result or "web" in result


@patch("skills.agent_reach_skill.shutil.which")
def test_status_reports_missing_cli(mock_which):
    mock_which.return_value = None
    result = AgentReachSkill().execute({"action": "status"})
    assert result.startswith("AGENT_REACH_NOT_INSTALLED")


@patch("skills.agent_reach_skill.subprocess.run")
@patch("skills.agent_reach_skill.shutil.which")
def test_doctor_uses_utf8_and_replacement(mock_which, mock_run):
    mock_which.side_effect = lambda name: "C:/agent-reach.exe" if name == "agent-reach" else None

    class Completed:
        returncode = 0
        stdout = '{"web": {"status": "ok"}}'
        stderr = ""

    mock_run.return_value = Completed()
    result = AgentReachSkill().execute({"action": "doctor"})

    assert result.startswith("AGENT_REACH_DOCTOR\nEXIT_CODE: 0")
    kwargs = mock_run.call_args.kwargs
    assert kwargs["encoding"] == "utf-8"
    assert kwargs["errors"] == "replace"


def test_rejects_unknown_action():
    assert "Unsupported action" in AgentReachSkill().execute({"action": "install"})
