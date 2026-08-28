# agent/core.py
import os
import importlib
import inspect
import ollama
from skills.base_skill import BaseSkill

class AgentCore:
    def __init__(self, model_name="qwen3:1.7b"):
        self.model_name = model_name
        self.skills = {}
        self._load_skills()

    def _load_skills(self):
        skills_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "skills")
        for filename in os.listdir(skills_dir):
            if filename.endswith(".py") and filename != "__init__.py" and filename != "base_skill.py":
                module_name = f"skills.{filename[:-3]}"
                try:
                    module = importlib.import_module(module_name)
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if issubclass(obj, BaseSkill) and obj is not BaseSkill:
                            skill_instance = obj()
                            # تسجيل الأداة بالاسم ديالها أو اسم الكلاس
                            skill_name = getattr(skill_instance, "name", name.lower().replace("skill", ""))
                            self.skills[skill_name] = skill_instance
                except Exception as e:
                    print(f"Error loading skill {filename}: {e}")

    def run(self, user_query: str) -> str:
        # التوجيه الذكي باختيار الأداة المتوفرة أوتوماتيكياً
        available_skills = list(self.skills.keys())
        prompt = f"""
Analyze the user query and choose the most appropriate tool from this list: {available_skills}.
If no tool is needed, return 'direct'.
Return ONLY the exact tool name or 'direct'.

Query: {user_query}
Tool:
"""
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}]
            )
            decision = response['message']['content'].strip().lower()
            
            selected_skill = None
            for s_name in available_skills:
                if s_name in decision:
                    selected_skill = s_name
                    break

            if selected_skill and selected_skill in self.skills:
                skill_res = self.skills[selected_skill].execute({"query": user_query})
                
                # صياغة الجواب النهائي بناءً على النتيجة المستخرجة
                final_res = ollama.chat(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a direct local assistant. Answer the user accurately based on the tool results in their language. No filler."},
                        {"role": "user", "content": f"Query: {user_query}\nTool Result: {skill_res}"}
                    ]
                )
                return final_res['message']['content']

            else:
                # Direct chat fallback
                response = ollama.chat(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a direct local assistant. Reply in the exact same language or dialect the user uses. No filler, no intro."},
                        {"role": "user", "content": user_query}
                    ]
                )
                return response['message']['content']

        except Exception as e:
            return f"Error: {e}"