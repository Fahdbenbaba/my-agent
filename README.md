# 🚀 My Agent — Local Modular AI Agent

> A local-first AI agent built in Python that can **reason, route, execute real tools, verify results, and accumulate reusable knowledge from verified experience**.

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

My Agent is a modular agent architecture built around **Ollama + Qwen 3 1.7B** for local reasoning and a set of specialized skills for real-world execution.

The core design principle is:

> **The model decides what should happen. Skills perform the work. Verification checks that the work actually happened. Learning preserves verified discoveries for future tasks.**

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
| 📝 Persistent Execution Journal | ✅ Working |
| 🧪 Automated Tests | ✅ Working |

---

## 🧠 Continuous Skill Learning

Inspired by the core idea behind Claudeception, My Agent can turn **verified discoveries** into reusable Markdown skills. The implementation is native to the Python architecture rather than depending on Claude Code hooks.

The learning system is intentionally evidence-first:

```text
Task
  ↓
Real tool execution
  ↓
Execution result / verification
  ↓
Persistent learning journal
  ↓
Skill extraction
  ↓
Quality gates + secret redaction
  ↓
Reusable SKILL.md
  ↓
Future retrieval
```

### What can be learned

The agent should consider creating a skill after:

- non-obvious debugging discoveries
- verified workarounds
- project-specific patterns
- verified integration/configuration fixes

It should **not** turn ordinary documentation lookups or one-off facts into skills.

### Quality gates

A learned skill must have a concrete trigger, reusable solution, and verification evidence. The learning layer rejects model-only speculation, prevents known contradictory fixes, and redacts credentials, tokens, passwords, and private keys before persistence.

The execution journal is persisted under:

```text
agent_memory/learning_journal.jsonl
```

This lets verified execution context survive across agent restarts.

### Bootstrap knowledge

The repository contains one verified initial lesson from local development:

```text
agent_skills/windows-openconnector-spawn-einval/SKILL.md
```

It records the observed Windows `spawn EINVAL` problem with the OpenConnector development launcher and the verified direct API runtime workaround.

---

## 🌍 Internet & Integration Layer

My Agent has two complementary external capability layers.

### Agent Reach

Agent Reach is used for public internet content and research workflows:

- Public web page reading through Jina Reader
- Public GitHub repository search and public GitHub page/file reading
- YouTube search and public video metadata through `yt-dlp`
- RSS / Atom feed reading
- CLI diagnostics and capability discovery
- Windows-safe CLI output handling

Examples:

```text
Read https://example.com
Search GitHub for qwen
Search YouTube for Python tutorials
Read https://example.com/feed.xml as an RSS feed
Run Agent Reach doctor
```

### OpenConnector

OpenConnector is used as the connected-app / authenticated action layer. It provides a local runtime where provider credentials remain behind the connector boundary while the agent discovers and executes provider Actions.

Supported integration areas include:

- Runtime health checks
- Provider and action catalog discovery
- Connection discovery
- OAuth configuration and authorization flows
- Action listing/search/contract retrieval
- Provider Action execution
- Named connection selection
- Confirmation gates for potentially side-effectful operations

Local development runtime:

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
                     ┌──────────────────┼──────────────────┐
                     │                  │                  │
                     ▼                  ▼                  ▼
                  ROUTER          TOOL EXECUTION      LEARNING JOURNAL
                     │                  │                  │
       ┌─────────────┼─────────────┐    │                  │
       ▼             ▼             ▼    ▼                  ▼
 Local Skills    Agent Reach   OpenConnector      Verified Context
       │             │             │                    │
       └─────────────┴─────────────┴────────────────────┘
                              │
                              ▼
                     Evidence / Verification
                              │
                              ▼
                       Skill Learning Engine
                              │
                              ▼
                       Reusable SKILL.md
```

The LLM is **not** treated as the source of truth for tool results. Tool output and verification evidence are kept separate from model reasoning, then reused by the learning layer.

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

Current skills include:

- Calculator
- Memory
- File Manager
- Python Sandbox
- Browser
- Web Search
- Git Manager
- Database
- Agent Reach
- OpenConnector
- Skill Learning

### Skill Learning actions

```text
list    → list learned skills
search  → search learned skills
save    → save a verified reusable lesson
get     → retrieve one learned skill
```

Example:

```text
List learned skills
Search learned skills for spawn EINVAL Windows
Save what we learned as a reusable skill
```

The save operation requires enough verified evidence to prevent hallucinated lessons.

---

## 📁 Project Structure

```text
my-agent/
│
├── agent/
│   ├── core.py
│   ├── router.py
│   └── evidence_guard.py
│
├── skills/
│   ├── base_skill.py
│   ├── calculator.py
│   ├── memory_skill.py
│   ├── file_manager.py
│   ├── python_sandbox.py
│   ├── browser_skill.py
│   ├── web_search_skill.py
│   ├── agent_reach_skill.py
│   ├── open_connector_skill.py
│   ├── skill_learning.py
│   ├── search_providers/
│   ├── git_skill.py
│   └── database_skill.py
│
├── agent_skills/
│   └── windows-openconnector-spawn-einval/
│       └── SKILL.md
│
├── agent_memory/
│   ├── learning_journal.jsonl
│   └── ...
│
├── models/
├── tests/
├── main.py
├── requirements.txt
├── pytest.ini
├── LICENSE
└── README.md
```

---

## ⚙️ Requirements

- Python **3.10+**
- Ollama
- Qwen 3 1.7B
- Git
- Playwright + Chromium
- Python dependencies from `requirements.txt`
- Agent Reach CLI for Agent Reach-backed capabilities
- Node.js for a local OpenConnector runtime

The core reasoning loop can run locally with Ollama without a paid hosted LLM API.

---

## 🚀 Installation

### Clone My Agent

```bash
git clone https://github.com/Fahdbenbaba/my-agent.git
cd my-agent
```

### Install Python dependencies

```bash
python -m pip install -r requirements.txt
```

### Install Chromium

```bash
python -m playwright install chromium
```

### Start Ollama

```bash
ollama pull qwen3:1.7b
```

Ensure Ollama is available at:

```text
http://localhost:11434
```

### Agent Reach

Install/configure Agent Reach separately and verify:

```bash
agent-reach doctor --json
```

### OpenConnector

Clone OpenConnector separately:

```bash
git clone https://github.com/oomol-lab/open-connector.git
cd open-connector
npm install
```

On Windows, start the API runtime directly:

```bash
npm run dev:api
```

The API runs on:

```text
http://localhost:3000
```

Start the local web console in another terminal:

```bash
npm run dev --workspace web
```

The web console runs on:

```text
http://localhost:5173
```

For GitHub OAuth, configure the callback:

```text
http://localhost:3000/oauth/callback
```

Keep OAuth secrets and runtime encryption keys out of source control.

### Start My Agent

```bash
cd ../my-agent
python main.py
```

---

## 🧪 Testing

Run the test suite with:

```bash
python -m pytest
```

The regression suite covers routing, Agent Reach integration, learning behavior, secret redaction, and other core skills.

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

### Skill Learning

```text
List learned skills
```

```text
Search learned skills for Windows spawn EINVAL
```

After a verified debugging task:

```text
Save what we learned as a reusable skill
```

---

## 🛡️ Security & Verification

Current protections include:

- Workspace restrictions for file/database operations
- Restricted Git command handling
- Python execution safeguards
- Evidence filtering for selected web queries
- Action/result verification
- Persistent learning journal with secret redaction
- Learned-skill quality gates
- Explicit confirmation for potentially side-effectful OpenConnector Actions
- Provider credentials kept inside the OpenConnector runtime boundary

For local OpenConnector deployments, enable runtime authentication and encryption before exposing the connector outside the local machine.

Do not give an experimental agent unrestricted access to sensitive files, credentials, production systems, or financial accounts.

---

## 📌 Current Status

**V1 — Functional Local Agent + Internet + Connected Apps + Verified Learning**

The project currently demonstrates:

- Modular Python architecture
- Local LLM integration
- Intent-based tool routing
- Real tool execution
- Browser automation
- Web search abstraction
- Evidence grounding
- Persistent vector memory
- Persistent execution journal
- File-system automation
- Python execution
- Git integration
- SQLite integration
- Agent Reach public internet integration
- OpenConnector connected-app integration
- OAuth-based provider connections
- Verified continuous skill learning
- Multi-step task execution
- Automated regression testing

This remains a **portfolio / learning project and agent architecture prototype**, not a fully autonomous production system.

---

## 🗺️ Roadmap

- [ ] Better task decomposition / planner
- [ ] Automatic retry and recovery
- [ ] Richer browser interaction
- [ ] More Agent Reach channels
- [ ] More OpenConnector providers and cross-app workflows
- [ ] Stronger Python sandbox isolation
- [ ] Structured execution logs / observability
- [ ] Better tool schemas and validation
- [ ] More end-to-end tests
- [ ] Automatic skill retrieval before relevant tasks
- [ ] Skill confidence / provenance scoring
