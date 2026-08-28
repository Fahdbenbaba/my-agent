import uuid
from datetime import datetime, timezone

import chromadb

from skills.base_skill import BaseSkill


class MemorySkill(BaseSkill):
    name = "memory"
    description = "Store or retrieve information from long-term ChromaDB memory."
    schema = {
        "type": "function",
        "function": {
            "name": "memory",
            "description": description,
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["store", "retrieve"],
                        "description": "Whether to store a memory or retrieve matching memories.",
                    },
                    "text": {
                        "type": "string",
                        "description": "The memory to store or the query used to retrieve memories.",
                    },
                },
                "required": ["action", "text"],
            },
        },
    }

    def __init__(self):
        self.client = chromadb.PersistentClient(path="./agent_memory")
        self.collection = self.client.get_or_create_collection(
            name="agent_long_term_memory"
        )

    def execute(self, arguments: dict) -> str:
        if not isinstance(arguments, dict):
            return "Memory Error: arguments must be a dictionary."

        action = str(arguments.get("action", "")).strip().lower()
        text = str(arguments.get("text", arguments.get("content", ""))).strip()

        if action not in {"store", "retrieve"}:
            return "Memory Error: action must be 'store' or 'retrieve'."
        if not text:
            return "Memory Error: no memory text/query provided."

        try:
            if action == "store":
                memory_id = str(uuid.uuid4())
                self.collection.add(
                    documents=[text],
                    ids=[memory_id],
                    metadatas=[
                        {
                            "type": "user_memory",
                            "created_at": datetime.now(timezone.utc).isoformat(),
                        }
                    ],
                )
                return f"Memory stored successfully: {text}"

            result = self.collection.query(
                query_texts=[text],
                n_results=min(5, self.collection.count()),
                include=["documents", "metadatas", "distances"],
            )

            documents = result.get("documents", [[]])[0]
            distances = result.get("distances", [[]])[0]

            if not documents:
                return "No relevant memories found."

            # Chroma returns nearest results first. Keep only reasonably relevant
            # results when distances are available; older installations may omit them.
            matches = []
            for index, document in enumerate(documents):
                distance = distances[index] if index < len(distances) else None
                if distance is None or distance <= 1.2:
                    matches.append(document)

            if not matches:
                return "No sufficiently relevant memories found."

            return "Relevant memories:\n- " + "\n- ".join(matches)

        except Exception as e:
            return f"Memory Error: {str(e)}"
