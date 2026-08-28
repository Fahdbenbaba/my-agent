# skills/python_sandbox.py
import sys
import io
import contextlib
from skills.base_skill import BaseSkill

class PythonSandboxSkill(BaseSkill):
    def get_name(self) -> str:
        return "python_sandbox"

    def get_description(self) -> str:
        return "Execute Python code in a safe sandbox and return the output or results."

    def get_schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.get_name(),
                "description": self.get_description(),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "The valid Python code to execute."
                        }
                    },
                    "required": ["code"]
                }
            }
        }

    def execute(self, args: dict) -> str:
        code = args.get("code")
        if not code:
            return "Error: No code provided."

        # Capture standard output
        output_buffer = io.StringIO()
        
        # Restricted safe globals environment
        safe_globals = {
            "__builtins__": {
                'abs': abs, 'all': all, 'any': any, 'bool': bool, 'dict': dict,
                'enumerate': enumerate, 'filter': filter, 'float': float, 'int': int,
                'len': len, 'list': list, 'map': map, 'max': max, 'min': min,
                'range': range, 'round': round, 'set': set, 'sorted': sorted,
                'str': str, 'sum': sum, 'tuple': tuple, 'zip': zip, 'print': print
            }
        }

        try:
            with contextlib.redirect_stdout(output_buffer):
                # Execute the code snippet
                exec(code, safe_globals)
            
            result = output_buffer.getvalue()
            if not result.strip():
                return "Code executed successfully with no print output."
            return result
        except Exception as e:
            return f"Execution Error: {str(e)}"