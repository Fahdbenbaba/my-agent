import os
import sqlite3

from skills.base_skill import BaseSkill


class DatabaseSkill(BaseSkill):
    name = "database_manager"
    description = "Create and execute SQL queries on local SQLite databases."
    schema = {
        "type": "function",
        "function": {
            "name": "database_manager",
            "description": description,
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["create_database", "query"],
                        "description": "Create a database file or execute SQL."
                    },
                    "db_path": {
                        "type": "string",
                        "description": "SQLite database filename/path. Defaults to agent_memory.db."
                    },
                    "query": {
                        "type": "string",
                        "description": "SQL query to execute when action is query."
                    }
                },
                "required": ["action"]
            }
        }
    }

    def __init__(self, db_path="agent_memory.db"):
        self.db_path = db_path

    def execute(self, arguments: dict) -> str:
        action = str(arguments.get("action", "query")).strip().lower()
        db_path = str(arguments.get("db_path") or self.db_path).strip()

        if not db_path:
            return "Database Error: No database path provided."

        # Keep database files inside the current workspace.
        absolute = os.path.abspath(db_path)
        workspace = os.path.abspath(os.getcwd())
        if os.path.commonpath([absolute, workspace]) != workspace:
            return "Database Error: Database path must stay inside the workspace."

        try:
            if action == "create_database":
                with sqlite3.connect(absolute):
                    pass
                return f"SQLite database created successfully: {db_path}"

            if action != "query":
                return "Database Error: action must be 'create_database' or 'query'."

            query = str(arguments.get("query", "")).strip()
            if not query:
                return "Database Error: No SQL query provided."

            with sqlite3.connect(absolute) as conn:
                cursor = conn.cursor()
                cursor.execute(query)

                if query.lower().startswith("select"):
                    rows = cursor.fetchall()
                    columns = [description[0] for description in cursor.description]
                    if not rows:
                        return "Query executed successfully. No rows returned."
                    return f"Columns: {columns}\nRows:\n" + "\n".join(map(str, rows))

                return "SQL query executed successfully (Database updated)."
        except Exception as e:
            return f"Database Error: {str(e)}"
