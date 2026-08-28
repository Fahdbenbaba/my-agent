from unittest.mock import MagicMock, patch

from skills.memory_skill import MemorySkill


def make_skill():
    with patch("skills.memory_skill.chromadb.PersistentClient") as client_cls:
        collection = MagicMock()
        collection.count.return_value = 0
        client = MagicMock()
        client.get_or_create_collection.return_value = collection
        client_cls.return_value = client
        skill = MemorySkill()
        return skill, collection


def test_memory_invalid_action():
    skill, _ = make_skill()
    assert skill.execute({"action": "delete", "text": "x"}).startswith("Memory Error:")


def test_memory_empty_text():
    skill, _ = make_skill()
    assert skill.execute({"action": "store", "text": ""}) == "Memory Error: no memory text/query provided."


def test_memory_store():
    skill, collection = make_skill()
    result = skill.execute({"action": "store", "text": "Python is my favorite language"})
    assert result.startswith("Memory stored successfully:")
    collection.add.assert_called_once()


def test_memory_retrieve_without_memories():
    skill, collection = make_skill()
    collection.count.return_value = 0
    assert skill.execute({"action": "retrieve", "text": "Python"}) == "No relevant memories found."
