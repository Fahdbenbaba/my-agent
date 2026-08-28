import uuid
import chromadb
from skills.base_skill import BaseSkill


class MemorySkill(BaseSkill):
    name = "memory"
    description = "Store or retrieve information from long-term ChromaDB vector memory."
    schema = {
        "type": "function",
        "function": {
            "name": "memory",
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

    def __init__(self):
        self.client = chromadb.PersistentClient(path="./agent_memory")
        self.collection = self.client.get_or_create_collection(name="agent_long_term_memory")

    def execute(self, arguments: dict) -> str:
        if not isinstance(arguments, dict):
            return "Error: Memory arguments must be a dictionary."

        action = str(arguments.get("action", "")).strip().lower()
        text = str(arguments.get("text", "")).strip()

        if action not in {"store", "retrieve"}:
            return "Error: action must be 'store' or 'retrieve'."
        if not text:
            return "Error: No memory text provided."

        try:
            if action == "store":
                memory_id = str(arguments.get("memory_id") or uuid.uuid4())
                self.collection.upsert(
                    documents=[text],
                    ids=[memory_id],
                    metadatas=[{"type": "long_term_memory"}],
                )
                return f"Memory successfully stored: {text}"

            result = self.collection.query(query_texts=[text], n_results=3)
            documents = result.get("documents", [[]])[0]
            if not documents:
                return "No relevant memories found."
            return "Found matching memories:\n- " + "\n- ".join(documents)
        except Exception as e:
            return f"Memory Error: {e}"
