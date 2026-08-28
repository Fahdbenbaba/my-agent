from skills.base_skill import BaseSkill


def test_base_skill_contract_is_defined():
    # These are annotations required by the BaseSkill contract.
    assert "name" in BaseSkill.__annotations__
    assert "description" in BaseSkill.__annotations__
    assert "schema" in BaseSkill.__annotations__

    # execute() is the required abstract operation.
    assert getattr(BaseSkill.execute, "__isabstractmethod__", False) is True


def test_run_is_backward_compatible_alias():
    assert callable(BaseSkill.run)
