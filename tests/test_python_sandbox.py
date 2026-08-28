from skills.python_sandbox import PythonSandboxSkill


def test_python_sandbox_print():
    assert PythonSandboxSkill().execute({"code": "print(10 * 20)"}).strip() == "200"


def test_python_sandbox_basic_math():
    result = PythonSandboxSkill().execute({"code": "print(sum(range(1, 6)))"})
    assert result.strip() == "15"


def test_python_sandbox_empty_code():
    assert PythonSandboxSkill().execute({"code": ""}) == "Error: No code provided."


def test_python_sandbox_rejects_unavailable_builtin():
    result = PythonSandboxSkill().execute({"code": "open('forbidden.txt', 'w')"})
    assert result.startswith("Execution Error:")
