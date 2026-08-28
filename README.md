# 🚀 My Agent — Local Modular AI Agent

A **local-first, modular AI agent** built in Python. It uses **Ollama + Qwen 3 (1.7B)** as the local reasoning model and a collection of specialized skills for real task execution.

The project is designed around a simple principle:

> **The model decides what should happen; skills perform the actual work; verification checks that the work really happened.**

## ✨ What It Can Do

| Capability | Status |
|---|---|
| 🧮 Calculator | ✅ |
| 🧠 Long-term Memory | ✅ |
| 📁 File Manager | ✅ |
| 🐍 Python Sandbox | ✅ |
| 🌐 Browser Automation | ✅ |
| 🔎 Web Search + Evidence Grounding | ✅ |
| 🔧 Git Operations | ✅ |
| 🗄️ SQLite Database | ✅ |
| 🔁 Multi-step execution | ✅ |
| 🛡️ Action verification | ✅ |

### Example

The agent can handle a task such as:

```text
Go to https://www.python.org, find the latest Python release,
and create a file called python_latest.txt containing the version
and the page title.
```

The workflow can use the browser to inspect the real page, extract the information, create the requested file, read it back, and verify the result before reporting success.

## 🏗️ Architecture

```text
                         USER
                           │
                           ▼
                    ┌─────────────┐
                    │  AGENT CORE │
                    │ Orchestrator│
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │    ROUTER   │
                    │ Intent →    │
                    │ Skill       │
                    └──────┬──────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
      ┌────────┐      ┌─────────┐      ┌────────┐
      │ Search │      │ Browser │      │ Files  │
      └────────┘      └─────────┘      └────────┘
          │                │                │
          ├────────┬───────┴───────┬────────┤
          ▼        ▼               ▼        ▼
      Calculator Memory       Python      Git
                                  │
                                  ▼
                              Database
                                  │
                                  ▼
                         ┌────────────────┐
                         │   VERIFICATION │
                         │ Check real     │
                         │ execution      │
                         └───────┬────────┘
                                 │
                                 ▼
                            FINAL RESULT
```

## 🧩 Skill Architecture

Every skill follows the same interface through an abstract base class:

```python
class BaseSkill(ABC):
    name: str
    description: str
    schema: dict

    @abstractmethod
    def execute(self, arguments: dict) -> str:
        ...
```

This keeps the system modular: a new skill can be added without rewriting the entire agent.

## 📁 Project Structure

```text
my-agent/
│
├── agent/
│   ├── core.py              # Agent orchestration and execution
│   ├── router.py            # Intent and skill routing
│   └── evidence_guard.py    # Evidence / grounding checks
│
├── skills/
│   ├── base_skill.py        # Abstract skill interface
│   ├── calculator.py        # Mathematical calculations
│   ├── memory_skill.py      # Persistent vector memory
│   ├── file_manager.py      # File operations
│   ├── python_sandbox.py    # Python execution
│   ├── browser_skill.py     # Browser automation
│   ├── web_search_skill.py  # Web research
│   ├── git_skill.py         # Git operations
│   └── database_skill.py    # SQLite operations
│
├── agent_memory/            # Persistent ChromaDB data
├── models/                  # Local LLM client
├── main.py                  # CLI entry point
└── README.md
```

## ⚙️ Requirements

- Python 3.10+
- Ollama
- Qwen 3 1.7B
- Git
- Playwright + Chromium for browser automation

## 🚀 Installation

### 1. Clone

```bash
git clone https://github.com/Fahdbenbaba/my-agent.git
cd my-agent
```

### 2. Install Python dependencies

If the repository contains a `requirements.txt` file:

```bash
pip install -r requirements.txt
```

Otherwise install the core dependencies used by the project:

```bash
pip install chromadb requests playwright
```

### 3. Install the browser

```bash
python -m playwright install chromium
```

### 4. Pull the local model

```bash
ollama pull qwen3:1.7b
```

Make sure Ollama is running locally on its default endpoint:

```text
http://localhost:11434
```

### 5. Run

```bash
python main.py
```

## 🧪 Example Prompts

```text
2 + 2
```

```text
Remember that my favorite programming language is Python.
```

```text
What is my favorite programming language?
```

```text
Run Python code: print(10 * 20)
```

```text
Create a file called test.txt with the text Hello Agent
```

```text
Show me the git status of this repository
```

```text
Create a SQLite database called test.db
```

```text
Open https://www.python.org and show me the page title
```

```text
Search the web for the latest Python release
```

## 🔐 Local-First Design

The reasoning model runs locally through Ollama. This makes the project useful for experimentation with local AI agents without requiring a paid hosted LLM API for the core reasoning loop.

Web access and browser automation are separate execution capabilities, while evidence checks help prevent unsupported current-information claims from being presented as verified facts.

## 🛠️ Current Scope

This is a **V1 agent foundation** rather than a production autonomous system. The current architecture focuses on reliable modular skills, routing, execution, grounding, and verification.

Planned future improvements include:

- Planner / task decomposition
- Task graphs and dependency management
- Automatic retry and recovery
- More browser actions
- More search providers
- Stronger sandbox isolation
- Automated tests and CI
- Better observability and execution logs

## 📌 Portfolio Highlights

This project demonstrates practical experience with:

- Python application architecture
- Abstract Base Classes and modular design
- Local LLM integration
- Tool / skill routing
- Browser automation with Playwright
- Web research and evidence grounding
- Vector memory with ChromaDB
- File-system automation
- Python execution
- Git and SQLite integration
- Multi-step task execution
- Action verification

## ☕ Support the Project

If you find this project useful and would like to support its development, you can optionally make a donation.

**USDT (TRC20)**

> Donation address: TRZb5ANp6rLCYP1cND4KpaxHVWvPTQyKkc

Thank you for supporting the project ❤️

## 📄 License

Add your preferred open-source license before publishing the project for reuse by others.
