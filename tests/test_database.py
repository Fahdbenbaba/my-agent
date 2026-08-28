import sqlite3

from skills.database_skill import DatabaseSkill


def test_create_database(tmp_path):
    db = tmp_path / "test.db"
    result = DatabaseSkill().execute({"action": "create_database", "db_path": str(db)})
    assert "created successfully" in result
    assert db.exists()


def test_database_query(tmp_path):
    db = tmp_path / "test.db"
    skill = DatabaseSkill()
    skill.execute({"action": "create_database", "db_path": str(db)})
    assert "updated" in skill.execute({"action": "query", "db_path": str(db), "query": "CREATE TABLE users (id INTEGER, name TEXT)"})
    skill.execute({"action": "query", "db_path": str(db), "query": "INSERT INTO users VALUES (1, 'Alice')"})
    result = skill.execute({"action": "query", "db_path": str(db), "query": "SELECT * FROM users"})
    assert "Alice" in result


def test_database_rejects_empty_query(tmp_path):
    db = tmp_path / "test.db"
    result = DatabaseSkill().execute({"action": "query", "db_path": str(db), "query": ""})
    assert result == "Database Error: No SQL query provided."
