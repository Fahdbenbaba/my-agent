import uuid
import chromadb
from skills.base_skill import BaseSkill


class MemorySkill(BaseSkill):
    name = "memory_tool"
    description = "Store or retrieve information from long-term ChromaDB vector memory."
    schema = {
        "type": "function",
        "function": {
            "name": "memory_tool",
            "description": description,
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["store", "retrieve"]},
                    "text": {"type": "string", "description": "Content to store or query."},
                },
                "required": ["action", "text"],
            },
        },
    }

    def execute(self, arguments: dict) -> str:
        if not isinstance(arguments, dict):
            arguments = {"action": "store", "text": str(arguments)}

        action = str(arguments.get("action", "store"))
        text = arguments.get("text") or arguments.get("content") or ""
        if not text:
            return "Error: No memory text provided."

        try:
            if action == "store":
                memory_id = arguments.get("memory_id") or str(uuid.uuid4())
                self.collection.upsert(documents=[str(text)], ids=[str(memory_id)])
                return f"Memory successfully stored with ID: {memory_id}"

            if action == "retrieve":
                result = self.collection.query(query_texts=[str(text)], n_results=2)
                documents = result.get("documents", [[]])[0]
                if not documents:
                    return "No relevant memories found."
                return "Found matching memories:\n- " + "\n- ".join(documents)

            return "Unknown action. Use 'store' or 'retrieve'."
        except Exception as e:
            return f"Memory Error: {str(e)}"

    def __init__(self):
        self.client = chromadb.PersistentClient(path="./agent_memory")
        self.collection = self.client.get_or_create_collection(name="agent_long_term_memory")
