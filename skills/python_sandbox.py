import io
import contextlib
from skills.base_skill import BaseSkill


class PythonSandboxSkill(BaseSkill):
    name = "python_sandbox"
    description = "Execute restricted Python code and return its output."
    schema = {
        "type": "function",
        "function": {
            "name": "python_sandbox",
            "description": description,
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "The valid Python code to execute."}
                },
                "required": ["code"],
            },
        },
    }

    def execute(self, arguments: dict) -> str:
        code = arguments.get("code")
        if not code:
            return "Error: No code provided."

        output_buffer = io.StringIO()
        safe_globals = {
            "__builtins__": {
                "abs": abs, "all": all, "any": any, "bool": bool, "dict": dict,
                "enumerate": enumerate, "filter": filter, "float": float, "int": int,
                "len": len, "list": list, "map": map, "max": max, "min": min,
                "range": range, "round": round, "set": set, "sorted": sorted,
                "str": str, "sum": sum, "tuple": tuple, "zip": zip, "print": print,
            }
        }

        try:
            with contextlib.redirect_stdout(output_buffer):
                exec(code, safe_globals)
            result = output_buffer.getvalue()
            return result if result.strip() else "Code executed successfully with no print output."
        except Exception as e:
            return f"Execution Error: {str(e)}"
