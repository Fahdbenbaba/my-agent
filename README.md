# 🚀 My Agent — Local Modular AI Agent

> A local-first AI agent built in Python that can **reason, route, execute real tools, verify results, connect to external services, and learn reusable skills from verified experience**.

My Agent is a modular agent architecture built around **Ollama + Qwen 3 1.7B** for local reasoning and a growing set of specialized skills for real-world execution.

The core design principle is:

> **The model decides what should happen. Skills perform the work. Verification checks that the work happened. Continuous learning preserves verified discoveries for future tasks.**

---

## ✨ Features

| Capability | Status |
|---|---|
| 🧮 Calculator | ✅ Working |
| 🧠 Long-term Memory | ✅ Working |
| 📚 Continuous Skill Learning | ✅ Integrated |
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

---

## 🧠 Continuous Skill Learning

My Agent includes a native Python implementation inspired by the continuous-learning ideas of Claudeception, adapted to the project's existing `BaseSkill` architecture rather than depending on Claude Code's skill runtime.

The learning system stores reusable lessons as Markdown under `agent_skills/<skill-name>/SKILL.md` and supports:

- Searching and listing learned skills
- Saving verified discoveries
- Updating an existing skill version instead of blindly duplicating it
- Precise trigger conditions, problem, solution, verification, notes, and optional references
- Secret redaction for API keys, tokens, passwords, bearer tokens, and private-key material
- Quality gates that reject thin or non-reusable knowledge
- Explicit learning requests such as `Save this as a skill` and `What did we learn?`
- LLM guidance to consider skill extraction after non-obvious debugging, workarounds, project-specific discoveries, and verified integrations

Example intents:

```text
Save what we just learned as a skill
What did we learn?
List learned skills
Search learned skills for Windows spawn EINVAL
```

A learned skill is not created merely because a task was completed. The intended standard is: **reusable + non-trivial + specific + verified**.

---

## 🌍 Internet & Integration Layer

My Agent has two complementary external capability layers.

### Agent Reach

Agent Reach is the public-internet capability layer. The integration supports:

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

The local Agent Reach installation is detected through the `agent-reach` CLI. The bridge does not automatically install software or credentials.

### OpenConnector

OpenConnector is the connected-app / authenticated action layer. It provides a local runtime where provider credentials remain behind the connector boundary while the agent discovers and executes provider Actions.

The My Agent integration supports:

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

The local OpenConnector runtime uses Node.js and can expose:

```text
API runtime:  http://localhost:3000
Web console:  http://localhost:5173
```

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
             ┌──────────────────────────┼─────────────────────────────┐
             │                          │                             │
             ▼                          ▼                             ▼
        Local Skills              Agent Reach                 OpenConnector
             │                          │                             │
    ┌────────┼────────┐        ┌────────┼────────┐        ┌───────────┼──────────┐
    ▼        ▼        ▼        ▼        ▼        ▼        ▼           ▼          ▼
 Calculator Memory  Files     Web    GitHub   YouTube  Providers     OAuth     Actions
    │        │        │        │        │        │        │           │          │
    └────────┴────────┴────────┴────────┴────────┴────────┴───────────┴──────────┘
                                        │
                                        ▼
                              ┌────────────────────┐
                              │ VERIFICATION /     │
                              │ EVIDENCE GUARD     │
                              └──────────┬─────────┘
                                         ▼
                              ┌────────────────────┐
                              │ SKILL LEARNING     │
                              │ Preserve verified  │
                              │ reusable knowledge │
                              └──────────┬─────────┘
                                         ▼
                                    FINAL RESULT
```

The system separates **reasoning**, **execution**, **verification**, and **learning**. Tool results are not treated as facts unless the tool actually returned them, and learned knowledge is only persisted after quality checks.

---

## 🧩 Skill System

Every runtime skill follows the common `BaseSkill` interface:

```python
class BaseSkill(ABC):
    name: str
    description: str
    schema: dict

    @abstractmethod
    def execute(self, arguments: dict) -> str:
        ...
```

Current runtime skills include:

- **Calculator** — mathematical expressions
- **Memory** — persistent long-term memory using ChromaDB
- **Skill Learning** — save, search, list, and retrieve reusable learned knowledge
- **File Manager** — create, read, and list workspace files
- **Python Sandbox** — execute Python code with restrictions
- **Browser** — navigate and inspect web pages through Playwright
- **Web Search** — search the web with provider abstraction and evidence handling
- **Git Manager** — safe Git repository operations
- **Database** — local SQLite database operations
- **Agent Reach** — public internet content access and capability discovery
- **OpenConnector** — connected-app discovery, OAuth, and provider Action execution

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

### Learning Routing

```text
User request / completed discovery
            │
            ▼
     Skill Learning Tool
            │
      ┌─────┴─────┐
      ▼           ▼
   search       save/update
      │           │
      └─────┬─────┘
            ▼
      agent_skills/
            │
            ▼
     Future retrieval
```

---

## 📁 Project Structure

```text
my-agent/
│
├── agent/
│   ├── core.py                  # Agent orchestration and execution
│   ├── router.py                # Intent → skill routing
│   └── evidence_guard.py        # Web evidence / grounding checks
│
├── skills/
│   ├── base_skill.py            # Shared abstract skill interface
│   ├── calculator.py            # Calculator
│   ├── memory_skill.py          # ChromaDB long-term memory
│   ├── skill_learning.py        # Continuous reusable-skill learning
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
├── agent_skills/                # Persisted learned Markdown skills
├── models/                      # Local LLM client
├── agent_memory/                # Persistent ChromaDB storage
├── tests/                       # Automated tests
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

### 6. Optional: OpenConnector

OpenConnector can be run separately as a local Node.js service:

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

Keep OAuth client secrets, runtime tokens, and encryption keys out of source control.

### 7. Start My Agent

From the My Agent repository:

```bash
python main.py
```

---

## 🧪 Testing

Run the complete suite with:

```bash
python -m pytest
```

Tests cover the core architecture, routing, Agent Reach integration, OpenConnector integration, and continuous skill learning.

The skill-learning tests verify:

- Saving and retrieving a learned skill
- Secret redaction
- Learning-intent routing

---

## 💡 Example Tasks

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

### Continuous Learning

```text
Save what we just learned as a skill
```

```text
What did we learn?
```

```text
List learned skills
```

```text
Search learned skills for Windows spawn EINVAL
```

When a discovery is worth preserving, the intended lifecycle is:

```text
Discover → Verify → Check existing skills → Save/update → Retrieve later
```

---

## 🛡️ Grounding, Verification & Learning Safety

`EvidenceGuard` helps ensure that time-sensitive web answers are based on retrieved evidence rather than unsupported model memory.

The architecture also supports verification after actions. For example, after creating a file, the agent can read the file back instead of simply trusting that creation succeeded.

The continuous-learning system intentionally does **not** save every interaction. A lesson should be reusable, non-trivial, specific, and verified. It should not merely duplicate documentation or preserve a one-off fact.

Learned skills are stored as Markdown rather than executable code. They are knowledge artifacts for future retrieval, not an unrestricted code-generation channel.

For connected services, OpenConnector keeps provider credentials and OAuth state inside its runtime boundary. My Agent receives action metadata and execution results rather than raw provider credentials.

Potentially destructive or externally side-effectful OpenConnector Actions require explicit confirmation.

---

## 🔐 Security Notes

Current protections include:

- Workspace restrictions for file/database operations
- Restricted Git command handling
- Python execution safeguards
- Evidence filtering for selected time-sensitive queries
- Action/result verification
- Modular skill boundaries
- Explicit confirmation for potentially side-effectful OpenConnector Actions
- Provider credentials kept inside the OpenConnector runtime boundary
- Secret redaction before learned knowledge is persisted

Do not give an experimental agent unrestricted access to sensitive files, credentials, production systems, or financial accounts.

For local OpenConnector deployments, enable runtime encryption and runtime authentication before exposing the connector outside your own machine.

---

## 📌 Current Status

**V1 — Functional Agent Foundation + Internet + Connected Apps + Continuous Learning**

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
- Continuous reusable-skill learning
- Multi-step task execution
- Verification
- Automated regression testing

The project remains an **agent architecture prototype / learning project** rather than a production-grade unrestricted autonomous system.

---

## 🗺️ Roadmap

Future improvements can include:

- [ ] Planner / task decomposition
- [ ] Explicit task graph and dependencies
- [ ] Automatic retry and recovery
- [ ] Better browser actions and page interaction
- [ ] Richer Agent Reach channel coverage
- [ ] Better OpenConnector action planning across multiple connected apps
- [ ] Semantic retrieval over learned skills
- [ ] Automatic lesson scoring and deduplication
- [ ] Skill dependency / related-skill graph
- [ ] Stronger Python sandbox isolation
- [ ] Continuous Integration (CI)
- [ ] Structured execution logs / observability
- [ ] Better tool schemas and validation
- [ ] More comprehensive end-to-end tests

---

## 📄 License

This project is licensed under the **MIT License**. See [`LICENSE`](LICENSE) for the complete license text.

---

## 👤 Author

**JILABI.DEV**

Built with Python, Ollama, Qwen, Playwright, ChromaDB, Agent Reach, OpenConnector, and a lot of experimentation. 🚀
