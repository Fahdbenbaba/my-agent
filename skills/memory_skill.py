# skills/memory_skill.py
import os
import json
import chromadb
from skills.base_skill import BaseSkill

class MemorySkill(BaseSkill):
    def __init__(self, db_path="./agent_memory"):
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(name="agent_long_term_memory")

    def get_name(self) -> str:
        return "memory_tool"

    def get_description(self) -> str:
        return "Store important information or search through past memories and facts."

    def get_schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.get_name(),
                "description": self.get_description(),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["store", "search"],
                            "description": "Choose whether to store a new memory or search existing memories."
                        },
                        "content": {
                            "type": "string",
                            "description": "The text to store or the query to search for."
                        }
                    },
                    "required": ["action", "content"]
                }
            }
        }

    def execute(self, args: dict) -> str:
        action = args.get("action")
        content = args.get("content")

        if action == "store":
            memory_id = str(os.urandom(4).hex())
            self.collection.add(
                documents=[content],
                ids=[memory_id]
            )
            return f"Successfully stored memory with ID: {memory_id}"

        elif action == "search":
            results = self.collection.query(
                query_texts=[content],
                n_results=2
            )
            docs = results.get("documents", [[]])[0]
            if not docs:
                return "No relevant memories found."
            return f"Found memories: {json.dumps(docs)}"
        
        return "Invalid action specified."