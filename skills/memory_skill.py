# skills/memory_skill.py
import uuid
import chromadb
from skills.base_skill import BaseSkill

class MemorySkill(BaseSkill):
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./agent_memory")
        self.collection = self.client.get_or_create_collection(name="agent_long_term_memory")

    def get_name(self) -> str:
        return "memory_tool"

    def get_description(self) -> str:
        return "Store or retrieve info from long-term ChromaDB vector memory."

    def get_schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.get_name(),
                "description": self.get_description(),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "description": "action: 'store' or 'retrieve'"},
                        "text": {"type": "string", "description": "Content to store or query for retrieval"}
                    },
                    "required": ["action", "text"]
                }
            }
        }

    def run(self, arguments):
        if isinstance(arguments, str):
            lower_arg = arguments.lower()
            # تحديد الحفظ فقط إذا كانت كلمات واضحة مثل remember أو حفظ
            store_keywords = ["remember", "حفظ", "سجل"]
            action = "store" if any(kw in lower_arg for kw in store_keywords) else "retrieve"
            return self.execute({"action": action, "text": arguments})
        return self.execute(arguments)

    def execute(self, args: dict) -> str:
        if not isinstance(args, dict): 
            args = {"action": "store", "text": str(args)}
        action = str(args.get("action", "store"))
        text = args.get("text") or args.get("content") or "Default text"
        doc_str = str(text)

        try:
            if action == "store":
                mem_id = args.get("memory_id") or str(uuid.uuid4())
                self.collection.upsert(documents=[doc_str], ids=[str(mem_id)])
                return f"Memory successfully stored with ID: {mem_id}"
            elif action == "retrieve":
                res = self.collection.query(query_texts=[doc_str], n_results=2)
                docs = res.get("documents", [[]])[0]
                return "Found matching memories:\n- " + "\n- ".join(docs) if docs else "No relevant memories found."
            return "Unknown action."
        except Exception as e:
            return f"Memory Error: {str(e)}"