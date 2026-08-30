from pathlib import Path

from skills.skill_learning import SkillLearningSkill


def test_save_and_get_skill(tmp_path: Path):
    skill = SkillLearningSkill(root=tmp_path)
    result = skill.execute({
        "action": "save",
        "name": "windows-npm-spawn-einval",
        "title": "Windows npm child-process spawn EINVAL",
        "description_text": "Fix Windows Node child-process spawn EINVAL in a local development launcher. Use when npm.cmd is spawned as a child process on Windows and Node returns EINVAL.",
        "problem": "A development launcher fails with spawn EINVAL while starting an npm workspace process on Windows.",
        "triggers": ["Node.js on Windows", "spawn EINVAL", "npm.cmd child process"],
        "solution": "Run the API entrypoint directly instead of the wrapper that spawns npm.cmd, or use a Windows shell-compatible process launch strategy.",
        "verification": "The API runtime starts and listens successfully on localhost:3000.",
        "evidence": "EXIT_CODE: 0\nconnect server listening\nurl: http://127.0.0.1:3000",
        "notes": "Keep the workaround specific to Windows process spawning and verify against the installed Node version.",
    })
    assert result.startswith("SKILL_SAVED:")
    saved = skill.execute({"action": "get", "name": "windows-npm-spawn-einval"})
    assert "spawn EINVAL" in saved
    assert "127.0.0.1:3000" in saved


def test_secret_content_is_redacted(tmp_path: Path):
    skill = SkillLearningSkill(root=tmp_path)
    result = skill.execute({
        "action": "save",
        "name": "secret-test",
        "title": "Secret handling",
        "description_text": "A reusable secret-handling lesson for API clients.",
        "problem": "Do not persist client secret values.",
        "solution": "Never store client_secret: supersecret-value in a learned skill.",
        "verification": "The stored document contains no raw credential value.",
        "evidence": "Verification passed successfully; credential value was redacted.",
    })
    assert "supersecret-value" not in result
    saved = skill.execute({"action": "get", "name": "secret-test"})
    assert "supersecret-value" not in saved
    assert "[REDACTED_SECRET]" in saved


def test_auto_capture_uses_verified_evidence(tmp_path: Path):
    skill = SkillLearningSkill(root=tmp_path)
    result = skill.execute({
        "action": "auto_capture",
        "name": "verified-runtime-recovery",
        "title": "Verified runtime recovery",
        "description_text": "Reusable recovery after a verified runtime failure.",
        "problem": "The first runtime launch failed with a process error.",
        "triggers": ["runtime failure", "process error"],
        "solution": "Use the verified direct API entrypoint instead of the failing wrapper.",
        "verification": "The direct API runtime started successfully and is listening on 127.0.0.1:3000.",
        "evidence": "First attempt failed with process error. Recovery completed successfully with exit_code: 0.",
        "source": "verified execution journal",
    })
    assert result.startswith("SKILL_SAVED:")
    saved = skill.execute({"action": "get", "name": "verified-runtime-recovery"})
    assert "Recovery completed successfully" in saved


def test_auto_capture_still_rejects_unverified_evidence(tmp_path: Path):
    skill = SkillLearningSkill(root=tmp_path)
    result = skill.execute({
        "action": "auto_capture",
        "name": "speculative-fix",
        "title": "Speculative fix",
        "description_text": "A possible workaround.",
        "problem": "Something might be broken.",
        "solution": "Try changing configuration.",
        "verification": "It should work.",
        "evidence": "No execution was performed.",
    })
    assert result.startswith("SKILL_REJECTED:")


def test_router_learning_commands():
    from agent.router import Router

    assert Router().route("Save this as a skill")["tool"] == "skill_learning"
    assert Router().route("List learned skills")["arguments"]["action"] == "list"
    assert Router().route("Search learned skills for spawn EINVAL Windows")["arguments"]["action"] == "search"
