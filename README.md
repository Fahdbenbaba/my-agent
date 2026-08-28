```markdown
# 🚀 Autonomous Local Modular AI Agent

A lightweight, modular, and privacy-first **Autonomous AI Agent** built entirely from scratch in Python. It runs locally using **Ollama (Qwen 1.7B)**, leveraging a smart router pattern to delegate tasks across diverse execution skills, complete with long-term vector memory.

## 🏗️ System Architecture

```text
                  AI AGENT
                     │
           ┌─────────┴─────────┐
           │                   │
       Qwen 1.7B             Tools
        (Brain)                │
           │         ┌─────────┼─────────┐
           │         │         │         │
        Planning   Search   Browser    Code
           │         │         │         │
           │       Files      APIs    Database
           │         │         │         │
           └─────────┴─────────┴─────────┘
                     │
                   Memory
                     │
               Knowledge Base
                     │
                Final Result

```

## ✨ Core Features

* **Modular Skill Architecture:** Clean separation of concerns where each tool/skill operates independently inside the `skills/` directory.
* **Local-First & Private:** Fully executed locally via Ollama without relying on expensive cloud APIs, ensuring complete data privacy.
* **Smart Orchestrator/Router:** Analyzes incoming user prompts and routes them dynamically to the correct specialized execution skill.
* **Long-Term Vector Memory:** Powered by **ChromaDB** to store, index, and recall past interactions and contextual data seamlessly.
* **Multi-Tool Integration:** Includes built-in tools for file management, code sandboxing, web searching, database queries, git operations, and calculations.

## 📁 Project Structure

```text
my-agent/
│
├── agent/
│   ├── core.py          # Core logic for Qwen LLM integration
│   └── router.py        # Intent classification and tool routing
│
├── skills/
│   ├── base_skill.py    # Abstract base class for all tools
│   ├── memory_skill.py  # ChromaDB vector memory handler
│   ├── calculator.py    # Math calculation utility
│   ├── file_manager.py  # File system interaction tool
│   ├── python_sandbox.py# Secure code execution environment
│   └── ...              # Other modular integrations
│
├── agent_memory/        # Persistent vector database storage
├── main.py              # Main application entry point & synthesis loop
└── README.md            # Project documentation

```

## ⚙️ Installation & Setup

1. **Clone the repository:**
```bash
git clone [https://github.com/Fahdbenbaba/my-agent.git](https://github.com/Fahdbenbaba/my-agent.git)
cd my-agent

```


2. **Install dependencies:**
```bash
pip install chromadb requests

```


3. **Ensure Ollama is running locally with Qwen:**
```bash
ollama run qwen3:1.7b

```


4. **Run the Agent:**
```bash
python main.py

```



---

### ☕ Support / Donation

If you like this project and want to support my work, you can donate via USDT (TRC20):
``

```
TRZb5ANp6rLCYP1cND4KpaxHVWvPTQyKkc
```
