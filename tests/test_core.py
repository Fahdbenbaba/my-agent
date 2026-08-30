import json

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


def test_generic_learning_extracts_verified_recovery(tmp_path):
    core = object.__new__(AgentCore)
    core.skills = {}

    from skills.skill_learning import SkillLearningSkill
    core.skills["skill_learning"] = SkillLearningSkill(root=tmp_path)
    evidence = (
        "EXECUTION:\nTOOL: launcher\nARGUMENTS: {}\nRESULT:\nError: spawn EINVAL\n\n---\n\n"
        "EXECUTION:\nTOOL: api\nARGUMENTS: {\"command\": \"dev:api\"}\nRESULT:\nServer started successfully and listening on 127.0.0.1:3000"
    )
    result = core._generic_learning_save(evidence)
    assert result.startswith("SKILL_SAVED:")
    files = list((tmp_path).glob("*/SKILL.md"))
    assert files
    saved = files[0].read_text(encoding="utf-8")
    assert "spawn EINVAL" in saved
    assert "started successfully" in saved


def test_generic_learning_does_not_learn_without_recovery(tmp_path):
    core = object.__new__(AgentCore)
    from skills.skill_learning import SkillLearningSkill
    core.skills = {"skill_learning": SkillLearningSkill(root=tmp_path)}
    evidence = "EXECUTION:\nTOOL: launcher\nARGUMENTS: {}\nRESULT:\nError: spawn EINVAL"
    assert core._generic_learning_save(evidence) is None
