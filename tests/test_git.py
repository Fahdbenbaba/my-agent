from skills.git_skill import GitSkill


def test_git_status():
    result = GitSkill().execute({"command": "status --short"})
    assert not result.startswith("Error: Git command")


def test_git_rejects_disallowed_command():
    result = GitSkill().execute({"command": "push origin main"})
    assert "not allowed" in result


def test_git_empty_command():
    assert GitSkill().execute({"command": ""}) == "Error: No git command provided."
