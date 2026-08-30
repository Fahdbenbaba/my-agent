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
| 🌍 Agent Reach | ✅ Integrated |
| 🔗 OpenConnector | ✅ Integrated |
| 🔐 OAuth Connections | ✅ Integrated |
| ▶️ YouTube / RSS access | ✅ Integrated through Agent Reach |
| 🧩 Multi-provider SaaS Actions | ✅ Integrated through OpenConnector |
| 🔁 Multi-step Execution | ✅ Working |
| ✔️ Action Verification | ✅ Working |
| 🧪 Automated Tests | ✅ **49 passed** |

---

## 🌍 Internet & Integration Layer

My Agent now has two complementary external capability layers.

### Agent Reach

**Agent Reach** is used as the internet-access layer for public content and research workflows. The integration supports:

- Web page reading through the configured Jina Reader backend
- Web search through the existing search provider abstraction
- Public GitHub repository search and public GitHub page/file reading
- YouTube search and public video metadata through `yt-dlp`
- RSS / Atom feed reading
- `doctor`, `status`, and capability discovery
- Windows-safe UTF-8 decoding for CLI output

Examples:

```text
Read https://example.com
Search GitHub for qwen
Search YouTube for Python tutorials
Read https://example.com/feed.xml as an RSS feed
Run Agent Reach doctor
```

The local Agent Reach installation is detected through the `agent-reach` CLI. The integration does not automatically install software or credentials.

### OpenConnector

**OpenConnector** is used as the connected-app / authenticated action layer. It provides a local runtime where provider credentials stay behind the connector boundary while the agent discovers and executes provider Actions.

The My Agent integration currently supports:

- Runtime health checks
- Provider/catalog discovery
- Provider credential metadata
- Connection discovery
- OAuth configuration discovery
- Starting OAuth authorization flows
- Action listing and search
- Action contract retrieval
- Action execution
- Named connection selection
- Confirmation gates for actions likely to create external side effects

Example agent intents:

```text
Check OpenConnector health
List connected providers
Search OpenConnector actions for Gmail
Show the GitHub provider configuration
Start GitHub OAuth authorization
Execute a GitHub action using the connected account
```

OpenConnector can be run locally with its Node runtime and Web Console. The current local development setup uses:

```text
API runtime:  http://localhost:3000
Web console:  http://localhost:5173
```

The project is designed so the OpenConnector runtime keeps provider credentials and OAuth state inside its own storage boundary rather than exposing raw provider tokens to the agent process.

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
             ┌──────────────────────────┼──────────────────────────┐
             │                          │                          │
             ▼                          ▼                          ▼
        Local Skills              Agent Reach                OpenConnector
             │                          │                          │
    ┌────────┼────────┐        ┌────────┼────────┐        ┌────────┼─────────┐
    ▼        ▼        ▼        ▼        ▼        ▼        ▼        ▼         ▼
 Calculator Memory  Files     Web    GitHub   YouTube  Providers OAuth    Actions
    │        │        │        │        │        │        │        │         │
    └────────┴────────┴────────┴────────┴────────┴────────┴────────┴─────────┘
                                        │
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

For connected services, provider credentials and OAuth state are handled by OpenConnector rather than being inserted into the model context.

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
- **Agent Reach** — public internet content access and capability discovery
- **OpenConnector** — connected-app discovery, OAuth, and provider Action execution

### Web Search Provider Architecture

```text
WebSearchSkill
      │
      ├── BraveSearchProvider   ← primary when configured
      │
      └── DuckDuckGoProvider    ← fallback
```

The provider layer is intentionally modular so additional search providers can be introduced later without redesigning the skill.

### Agent Reach Routing

```text
User request
    │
    ├── Read public URL ───────────────► Agent Reach / Web
    ├── Search GitHub ─────────────────► Agent Reach / GitHub
    ├── Search YouTube ────────────────► Agent Reach / YouTube
    └── Read RSS / Atom ───────────────► Agent Reach / RSS
```

### OpenConnector Routing

```text
User request
    │
    ├── providers / connections ───────► OpenConnector discovery
    ├── OAuth / login ─────────────────► OpenConnector OAuth
    ├── action search ─────────────────► OpenConnector action catalog
    └── execute an app action ──────────► OpenConnector runtime
```

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
│   ├── base_skill.py            # Shared abstract skill interface
│   ├── calculator.py            # Calculator
│   ├── memory_skill.py          # ChromaDB long-term memory
│   ├── file_manager.py          # Workspace file operations
│   ├── python_sandbox.py        # Restricted Python execution
│   ├── browser_skill.py         # Browser automation
│   ├── web_search_skill.py      # Web search orchestration
│   ├── agent_reach_skill.py     # Agent Reach integration
│   ├── open_connector_skill.py  # OpenConnector integration
│   ├── search_providers/        # Search provider implementations
│   ├── git_skill.py             # Git operations
│   └── database_skill.py        # SQLite operations
│
├── models/                      # Local LLM client
├── agent_memory/                # Persistent ChromaDB storage
├── tests/                       # Automated test suite
├── main.py                      # CLI entry point
├── requirements.txt             # Python dependencies
├── pytest.ini                   # Pytest configuration
├── LICENSE                      # MIT License
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
- Agent Reach CLI for Agent Reach-backed capabilities
- Node.js for a local OpenConnector runtime

> The project is designed to run locally. A paid hosted LLM API is not required for the core reasoning loop when Ollama is used.

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/Fahdbenbaba/my-agent.git
cd my-agent
```

### 2. Install Python dependencies

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

### 5. Optional: Agent Reach

Install and configure Agent Reach separately, then verify it with:

```bash
agent-reach doctor --json
```

The My Agent bridge detects the local `agent-reach` executable and exposes its configured capabilities.

### 6. Optional: OpenConnector

Clone OpenConnector separately and install its dependencies:

```bash
git clone https://github.com/oomol-lab/open-connector.git
cd open-connector
npm install
```

For Windows local development, start the API runtime directly:

```bash
npm run dev:api
```

The API runs on:

```text
http://localhost:3000
```

In another terminal, start the web console:

```bash
npm run dev --workspace web
```

The web console runs on:

```text
http://localhost:5173
```

For GitHub OAuth, configure an OAuth application whose callback matches the local OpenConnector callback URL:

```text
http://localhost:3000/oauth/callback
```

Keep OAuth client secrets and runtime encryption keys out of source control. OpenConnector supports runtime encryption and authenticated runtime access through environment variables and runtime tokens.

### 7. Start My Agent

From the My Agent repository:

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

Agent Reach routing and integration tests cover capability discovery, public web/GitHub/YouTube/RSS routing, CLI handling, and regression cases.

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

### Agent Reach

```text
Read https://example.com
```

```text
Search GitHub for qwen
```

```text
Search YouTube for Python tutorials
```

### OpenConnector

```text
Check OpenConnector health
```

```text
List connected providers
```

```text
Search OpenConnector actions for GitHub
```

```text
Show the GitHub provider configuration
```

```text
Execute github.get_current_user through OpenConnector
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

## 🛡️ Grounding, Verification & Connected-Service Safety

Current information is a major failure point for LLM applications. This project therefore separates **reasoning** from **evidence**.

`EvidenceGuard` helps ensure that time-sensitive web answers are based on retrieved evidence rather than unsupported model memory.

The architecture also supports verification after actions. For example, after creating a file, the agent can read the file back instead of simply trusting that the creation succeeded.

For connected services, OpenConnector keeps provider credentials and OAuth state inside its runtime boundary. My Agent receives action metadata and execution results rather than raw provider credentials.

For potentially destructive or external side-effect actions, the OpenConnector skill requires an explicit confirmation signal before execution.

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
- Explicit confirmation for potentially side-effectful OpenConnector Actions
- Provider credentials kept inside the OpenConnector runtime boundary

Do not give an experimental agent unrestricted access to sensitive files, credentials, production systems, or financial accounts.

For local OpenConnector deployments, enable runtime encryption and runtime authentication before exposing the connector outside your own machine.

---

## 📌 Current Status

**V1 — Functional Agent Foundation + Internet / Connected-App Integrations**

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
- Agent Reach public internet integration
- OpenConnector connected-app integration
- OAuth-based provider connections
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
- [ ] More Agent Reach channels and richer public-content workflows
- [ ] Better OpenConnector action planning across multiple connected apps
- [ ] Stronger Python sandbox isolation
- [ ] Continuous Integration (CI)
- [ ] Structured execution logs / observability
- [ ] Better tool schemas and validation
- [ ] More comprehensive end-to-end tests

---

## ☕ Support

If you find the project useful and want to support its development, an optional donation address can be added here manually.

**USDT — TRC20**

> Donation address:   TRZb5ANp6rLCYP1cND4KpaxHVWvPTQyKkc

Thank you for supporting the project ❤️

---

## 📄 License

This project is licensed under the **MIT License**. See [`LICENSE`](LICENSE) for the complete license text.

---

## 👤 Author

**JILABI.DEV**

Built with Python, Ollama, Qwen, Playwright, ChromaDB, Agent Reach, and OpenConnector. 🚀
