import pytest

from skills.calculator import CalculatorSkill


@pytest.fixture
def calculator():
    return CalculatorSkill()


def test_addition(calculator):
    assert calculator.execute({"expression": "2 + 2"}) == "4"


def test_multiplication_from_natural_language(calculator):
    assert calculator.execute({"expression": "Calculate 25 * 18 and tell me the result."}) == "450"


def test_operator_precedence(calculator):
    assert calculator.execute({"expression": "2 + 3 * 4"}) == "14"


def test_power(calculator):
    assert calculator.execute({"expression": "2 ** 10"}) == "1024"


def test_invalid_expression_is_rejected(calculator):
    result = calculator.execute({"expression": "__import__('os').system('echo bad')"})
    assert result.startswith("Error calculating:")


def test_empty_expression(calculator):
    assert calculator.execute({"expression": ""}) == "Error: expression is empty."
