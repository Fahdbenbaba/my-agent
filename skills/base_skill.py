from abc import ABC, abstractmethod


class BaseSkill(ABC):
    """
    Base class for all Agent skills.

    Every skill must define:
    - name: unique tool name
    - description: what the skill does
    - schema: JSON-compatible tool schema
    - execute(): the method used to run the skill

    `run()` is kept as a backward-compatible alias for older callers.
    """

    name: str
    description: str
    schema: dict

    @abstractmethod
    def execute(self, arguments: dict) -> str:
        """
        Execute the skill with the provided arguments.
        """
        pass

    def run(self, arguments: dict) -> str:
        """Backward-compatible alias for execute()."""
        return self.execute(arguments)
