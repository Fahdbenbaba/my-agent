import ast
import operator
import re

from skills.base_skill import BaseSkill


class CalculatorSkill(BaseSkill):
    name = "calculator"
    description = (
        "Use this tool to perform basic mathematical calculations. "
        "Example: 25 * 18"
    )
    schema = {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": description,
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "A basic mathematical expression. Example: 25 * 18",
                    }
                },
                "required": ["expression"],
            },
        },
    }

    OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    def execute(self, arguments: dict) -> str:
        expression = str(arguments.get("expression", "")).strip()
        expression = self._extract_expression(expression)

        if not expression:
            return "Error: expression is empty."

        try:
            tree = ast.parse(expression, mode="eval")
            result = self._evaluate(tree.body)
            return str(result)
        except Exception as e:
            return f"Error calculating: {e}"

    @staticmethod
    def _extract_expression(text: str) -> str:
        """Extract a mathematical expression from a natural-language request."""
        cleaned = text.strip()

        # Remove common request prefixes while keeping the expression intact.
        cleaned = re.sub(
            r"^(please\s+)?(calculate|compute|solve|what\s+is|find)\s*",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )
        cleaned = re.sub(r"\s*(and\s+tell\s+me.*|please.*)$", "", cleaned, flags=re.IGNORECASE)
        cleaned = cleaned.rstrip("?.! ")

        # If extra words remain, prefer the longest numeric/operator expression.
        match = re.search(r"[-+]?\d+(?:\s*(?:\+|-|\*|/|%|\^|\*\*)\s*[-+]?\d+)+", cleaned)
        if match:
            return match.group(0).replace("^", "**")

        return cleaned.replace("^", "**")

    def _evaluate(self, node):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
                return node.value
            raise ValueError("Only numbers are allowed.")

        if isinstance(node, ast.BinOp):
            operation = self.OPERATORS.get(type(node.op))
            if operation is None:
                raise ValueError("This operator is not allowed.")
            left = self._evaluate(node.left)
            right = self._evaluate(node.right)
            return operation(left, right)

        if isinstance(node, ast.UnaryOp):
            operation = self.OPERATORS.get(type(node.op))
            if operation is None:
                raise ValueError("This unary operator is not allowed.")
            return operation(self._evaluate(node.operand))

        raise ValueError("Invalid mathematical expression.")
