# 🚀 My Agent — Local Modular AI Agent

> A local-first AI agent built in Python that can **reason, route, execute real tools, verify results, and complete multi-step tasks**.

[![Tests](https://img.shields.io/badge/tests-49%20passed-brightgreen)](https://github.com/Fahdbenbaba/my-agent)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

My Agent is a modular agent architecture built around **Ollama + Qwen 3 1.7B** for local reasoning and a set of specialized skills for real-world execution.

The core design principle is simple:

> **The model decides what should happen. Skills perform the work. Verification checks that the work actually happened.**

---

## ✨ Features

| Capability | Status |
|---|---|
| 🧮 Calculator | ✅ Working |
| 🧠 Long-term Memory | ✅ Working |
| 📁 File Manager | ✅ Working |
| 🐍 Python Sandbox | ✅ Working |
| 🌐 Browser Automation | ✅ Working |
| 🔎 Web Search | ✅ Working |
| 🛡️ Evidence Grounding | ✅ Working |
| 🔧 Git Operations | ✅ Working |
| 🗄️ SQLite Database | ✅ Working |
| 🔁 Multi-step Execution | ✅ Working |
| ✔️ Action Verification | ✅ Working |
| 🧪 Automated Tests | ✅ **49 passed** |

---

## 🏗️ Architecture

```text
                              USER
                                │
                                ▼
                       ┌─────────────────┐
                       │   AGENT CORE    │
                       │ Orchestration   │
                       └────────┬────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │     ROUTER      │
                       │ Intent → Skill │
                       └────────┬────────┘
                                │
          ┌───────────┬─────────┼─────────┬───────────┐
          ▼           ▼         ▼         ▼           ▼
      Calculator    Memory    Files    Browser      Git
          │           │         │         │           │
          ▼           ▼         ▼         ▼           ▼
       Python     Database   Search   Playwright   SQLite
                    │          │
                    └────┬─────┘
                         ▼
                 ┌──────────────────┐
                 │  EVIDENCE GUARD  │
                 │ Grounding / Fact │
                 │    Validation    │
                 └────────┬─────────┘
                          ▼
                 ┌──────────────────┐
                 │   VERIFICATION   │
                 │ Verify execution │
                 └────────┬─────────┘
                          ▼
                     FINAL RESULT
```

### Design Philosophy

The LLM is **not treated as the source of truth for tool results**.

For example, when asked for the latest Python release, the agent should obtain current evidence through web search/browser capabilities rather than relying on what the model remembers from training.

---

## 🧩 Skill System

Every skill follows a common interface through `BaseSkill`:

```python
class BaseSkill(ABC):
    name: str
    description: str
    schema: dict

    @abstractmethod
    def execute(self, arguments: dict) -> str:
        ...
```

This makes skills independent and replaceable. New capabilities can be added without rewriting the entire agent.

### Current Skills

- **Calculator** — mathematical expressions
- **Memory** — persistent long-term memory using ChromaDB
- **File Manager** — create, read, and list workspace files
- **Python Sandbox** — execute Python code with restrictions
- **Browser** — navigate and inspect web pages through Playwright
- **Web Search** — search the web with provider abstraction and evidence handling
- **Git Manager** — safe Git repository operations
- **Database** — local SQLite database operations

### Web Search Provider Architecture

```text
WebSearchSkill
      │
      ├── BraveSearchProvider   ← primary when configured
      │
      └── DuckDuckGoProvider    ← fallback
```

The provider layer is intentionally modular so additional search providers can be introduced later without redesigning the skill.

---

## 📁 Project Structure

```text
my-agent/
│
├── agent/
│   ├── core.py              # Agent orchestration and execution
│   ├── router.py            # Intent → skill routing
│   └── evidence_guard.py    # Web evidence / grounding checks
│
├── skills/
│   ├── base_skill.py        # Shared abstract skill interface
│   ├── calculator.py        # Calculator
│   ├── memory_skill.py      # ChromaDB long-term memory
│   ├── file_manager.py      # Workspace file operations
│   ├── python_sandbox.py    # Restricted Python execution
│   ├── browser_skill.py     # Browser automation
│   ├── web_search_skill.py  # Web search orchestration
│   ├── search_providers/    # Search provider implementations
│   ├── git_skill.py         # Git operations
│   └── database_skill.py    # SQLite operations
│
├── models/                  # Local LLM client
├── agent_memory/            # Persistent ChromaDB storage
├── tests/                   # Automated test suite
├── main.py                  # CLI entry point
├── requirements.txt         # Python dependencies
├── pytest.ini               # Pytest configuration
├── LICENSE                  # MIT License
└── README.md
```

---

## ⚙️ Requirements

- Python **3.10+**
- [Ollama](https://ollama.com/)
- Qwen 3 1.7B
- Git
- Playwright + Chromium
- Python dependencies from `requirements.txt`

> The project is designed to run locally. A paid hosted LLM API is not required for the core reasoning loop when Ollama is used.

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/Fahdbenbaba/my-agent.git
cd my-agent
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Install Chromium for browser automation

```bash
python -m playwright install chromium
```

### 4. Install / start Ollama

Pull the local model:

```bash
ollama pull qwen3:1.7b
```

Make sure Ollama is running locally, normally at:

```text
http://localhost:11434
```

### 5. Start the agent

```bash
python main.py
```

---

## 🧪 Testing

The repository includes automated tests covering the core architecture and skills.

Run the complete suite with:

```bash
python -m pytest
```

Current baseline:

```text
49 passed
```

A passing test suite is required before treating changes to the architecture as stable.

---

## 💡 Example Tasks

### Memory

```text
Remember that my favorite programming language is Python.
```

```text
What is my favorite programming language?
```

### Python

```text
Run Python code: print(10 * 20)
```

### Files

```text
Create a file called test.txt with the text Hello Agent
```

```text
List the files in the current directory
```

### Database

```text
Create a SQLite database called test.db
```

### Git

```text
Show me the git status of this repository
```

### Browser

```text
Open https://www.python.org and show me the page title
```

### Web Search

```text
Search the web for the latest Python release
```

### Multi-step Task

```text
Go to https://www.python.org, find the latest Python release,
and create a file called python_latest.txt containing the version
and the page title.
```

The intended execution flow is:

```text
Browser → Extract evidence → File Manager → Read/Verify → Final response
```

---

## 🛡️ Grounding & Verification

Current information is a major failure point for LLM applications. This project therefore separates **reasoning** from **evidence**.

`EvidenceGuard` helps ensure that time-sensitive web answers are based on retrieved evidence rather than unsupported model memory.

The architecture also supports verification after actions. For example, after creating a file, the agent can read the file back instead of simply trusting that the creation succeeded.

This distinction is important:

```text
❌ "I think the file was created."

✅ Create file → Read file → Verify contents → Report success
```

---

## 🔐 Security Notes

The project is intended as a local agent foundation, not as an unrestricted computer-control system.

Current protections include:

- Workspace restrictions for file/database operations
- Restricted Git command handling
- Python execution safeguards
- Evidence filtering for selected time-sensitive queries
- Action/result verification
- Modular skill boundaries

Do not give an experimental agent unrestricted access to sensitive files, credentials, production systems, or financial accounts.

---

## 📌 Current Status

**V1 — Functional Agent Foundation**

The project currently demonstrates:

- Modular Python architecture
- Local LLM integration
- Intent-based tool routing
- Real tool execution
- Browser automation
- Web search abstraction
- Evidence grounding
- Persistent vector memory
- File-system automation
- Python execution
- Git integration
- SQLite integration
- Multi-step task execution
- Verification
- Automated regression testing

The project is suitable as a **portfolio / learning project and agent architecture prototype**. It should not yet be presented as a fully autonomous production agent.

---

## 🗺️ Roadmap

Future improvements can include:

- [ ] Planner / task decomposition
- [ ] Explicit task graph and dependencies
- [ ] Automatic retry and recovery
- [ ] Better browser actions and page interaction
- [ ] Additional search providers
- [ ] Stronger Python sandbox isolation
- [ ] Continuous Integration (CI)
- [ ] Structured execution logs / observability
- [ ] Better tool schemas and validation
- [ ] More comprehensive end-to-end tests

---

## ☕ Support

If you find the project useful and want to support its development, an optional donation address can be added here manually.

**USDT — TRC20**

> Donation address: **Add your address here manually**

Thank you for supporting the project ❤️

---

## 📄 License

This project is licensed under the **MIT License**. See [`LICENSE`](LICENSE) for the complete license text.

---

## 👤 Author

**Fahdbenbaba**

Built with Python, Ollama, Qwen, Playwright, ChromaDB, and a lot of experimentation. 🚀
