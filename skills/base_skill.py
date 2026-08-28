class BaseSkill:
    name = ""
    description = ""

    def get_schema(self) -> dict:
        """
        Return the JSON schema used by the LLM
        to understand this tool.
        """
        raise NotImplementedError

    def execute(self, arguments: dict) -> str:
        """
        Execute the tool and return a string result.
        """
        raise NotImplementedError