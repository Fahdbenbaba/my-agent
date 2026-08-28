from skills.base_skill import BaseSkill


def test_base_skill_contract_is_defined():
    assert hasattr(BaseSkill, "name")
    assert hasattr(BaseSkill, "description")
    assert hasattr(BaseSkill, "schema")
    assert hasattr(BaseSkill, "execute")
