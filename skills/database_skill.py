import sqlite3
from skills.base_skill import BaseSkill


class DatabaseSkill(BaseSkill):
    name = "database_manager"
    description = "Execute SQL queries on a local SQLite database to store and retrieve structured data."
    schema = {
        "type": "function",
        "function": {
            "name": "database_manager",
            "description": description,
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The SQL query to execute."}
                },
                "required": ["query"],
            },
        },
    }

    def __init__(self, db_path="agent_memory.db"):
        self.db_path = db_path

    def execute(self, arguments: dict) -> str:
        query = arguments.get("query")
        if not query:
            return "Error: No SQL query provided."

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query)

                if query.strip().lower().startswith("select"):
                    rows = cursor.fetchall()
                    columns = [description[0] for description in cursor.description]
                    if not rows:
                        return "Query executed successfully. No rows returned."
                    return f"Columns: {columns}\nRows:\n" + "\n".join(map(str, rows))

                return "SQL query executed successfully (Database updated)."
        except Exception as e:
            return f"Database Error: {str(e)}"
