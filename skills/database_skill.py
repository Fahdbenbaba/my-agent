# skills/database_skill.py
import sqlite3
import os
from skills.base_skill import BaseSkill

class DatabaseSkill(BaseSkill):
    def __init__(self, db_path="agent_memory.db"):
        self.db_path = db_path

    def get_name(self) -> str:
        return "database_manager"

    def get_description(self) -> str:
        return "Execute SQL queries (SELECT, INSERT, UPDATE, CREATE) on a local SQLite database to store and retrieve structured data."

    def get_schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.get_name(),
                "description": self.get_description(),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The SQL query to execute against the SQLite database."
                        }
                    },
                    "required": ["query"]
                }
            }
        }

    def execute(self, args: dict) -> str:
        query = args.get("query")
        if not query:
            return "Error: No SQL query provided."

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(query)
            
            # If it's a SELECT query, fetch results
            if query.strip().lower().startswith("select"):
                rows = cursor.fetchall()
                col_names = [description[0] for description in cursor.description]
                conn.close()
                
                if not rows:
                    return "Query executed successfully. No rows returned."
                
                result = f"Columns: {col_names}\nRows:\n"
                for row in rows:
                    result += str(row) + "\n"
                return result
            else:
                conn.commit()
                conn.close()
                return "SQL query executed successfully (Database updated)."
                
        except Exception as e:
            return f"Database Error: {str(e)}"