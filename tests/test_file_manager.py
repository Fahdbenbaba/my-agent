def test_file_manager_create_and_read(tmp_path, monkeypatch):
    from skills.file_manager import FileManagerSkill

    monkeypatch.chdir(tmp_path)
    skill = FileManagerSkill()
    assert "created successfully" in skill.execute({"action": "create", "filepath": "hello.txt", "content": "Hello Agent"})
    assert skill.execute({"action": "read", "filepath": "hello.txt"}) == "Hello Agent"


def test_file_manager_list(tmp_path, monkeypatch):
    from skills.file_manager import FileManagerSkill

    monkeypatch.chdir(tmp_path)
    (tmp_path / "one.txt").write_text("x", encoding="utf-8")
    assert "one.txt" in FileManagerSkill().execute({"action": "list"})


def test_file_manager_blocks_path_escape(tmp_path, monkeypatch):
    from skills.file_manager import FileManagerSkill

    monkeypatch.chdir(tmp_path)
    result = FileManagerSkill().execute({"action": "read", "filepath": "../outside.txt"})
    assert result.startswith("File Manager Error:")
