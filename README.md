# 🚀 MARS — Multi-Agent Research System

[![CI](https://github.com/YOUR_USERNAME/mars-multi-agent-research-system/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/mars-multi-agent-research-system/actions/workflows/ci.yml)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)](https://hub.docker.com/r/YOUR_USERNAME/mars-research-system)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2-green)](https://langchain-ai.github.io/langgraph/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> An autonomous multi-agent AI system that researches any topic, writes a structured report, and self-critiques until the output meets quality standards — all powered by **LangGraph**, **Groq (Llama 3.3 70B)**, and **Tavily Search**.

---

## ✨ Features

- 🤖 **4-agent orchestration** — Supervisor, Researcher, Writer, Critiquer
- 🔄 **Iterative refinement loop** — auto-revises drafts based on critique
- 🌐 **Real-time web search** via Tavily
- ⚡ **Groq-powered LLM** — 30 RPM free tier, sub-second inference
- 🖥️ **Streamlit UI** — live agent activity feed and formatted report output
- 🐳 **Docker-ready** — multi-stage build, non-root container, health check
- 🔁 **CI/CD pipeline** — GitHub Actions → Docker Hub → Render

---

## 🏗️ Architecture

```
User Query
    │
    ▼
┌─────────────┐
│  SUPERVISOR │  ◄─── Orchestrates the workflow
└──────┬──────┘       (deterministic + LLM fallback)
       │
       ├──► RESEARCHER  →  Tavily web search + LLM summarisation
       │
       ├──► WRITER      →  Synthesises research into a structured report
       │
       └──► CRITIQUER   →  Reviews draft, requests revisions or APPROVES
                │
                └──► (loop back to WRITER if revisions needed)
                └──► END when APPROVED or max revisions reached
```

**State machine** (LangGraph):
```
START → supervisor → researcher → supervisor → writer → critiquer → supervisor → END
```

---

## ⚡ Quickstart

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- [Groq API key](https://console.groq.com) (free)
- [Tavily API key](https://app.tavily.com) (free)

### 1. Clone & install

```bash
git clone https://github.com/YOUR_USERNAME/mars-multi-agent-research-system.git
cd mars-multi-agent-research-system
uv sync
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and fill in your API keys
```

```env
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

### 3. Run the app

```bash
uv run streamlit run app.py
# → Open http://localhost:8501
```

---

## 🐳 Docker

### Local run with Docker Compose

```bash
# Copy and fill in your .env first
cp .env.example .env

docker compose up --build
# → Open http://localhost:8501
```

### Manual Docker build & run

```bash
docker build -t mars-research-system .

docker run -p 8501:8501 \
  -e GROQ_API_KEY=your_key \
  -e TAVILY_API_KEY=your_key \
  mars-research-system
```

---

## 🧪 Development

### Install dev tools

```bash
uv sync
```

### Run tests (no API keys required)

```bash
uv run pytest tests/ -v
# or
make test
```

### Lint

```bash
uv run ruff check .
# or
make lint
```

### All dev commands

| Command           | Description                        |
|-------------------|------------------------------------|
| `make install`    | Install all dependencies           |
| `make run`        | Start the Streamlit app            |
| `make test`       | Run all unit tests                 |
| `make lint`       | Run ruff linter                    |
| `make lint-fix`   | Auto-fix ruff lint errors          |
| `make docker-up`  | Start with docker-compose          |
| `make docker-down`| Stop docker-compose services       |

---

## 🔑 Environment Variables

| Variable          | Required | Description                                      |
|-------------------|----------|--------------------------------------------------|
| `GROQ_API_KEY`    | ✅ Yes   | Groq API key — [get it here](https://console.groq.com) |
| `TAVILY_API_KEY`  | ✅ Yes   | Tavily Search key — [get it here](https://app.tavily.com) |

---

## 🚀 Deployment

### Option A — Render (Docker, recommended)

1. **Push to GitHub** and ensure CI passes.
2. On [Render](https://render.com), create a **New Web Service**.
3. Select **"Deploy an existing image"** → use `YOUR_DOCKERHUB_USERNAME/mars-research-system:latest`.
4. Set environment variables (`GROQ_API_KEY`, `TAVILY_API_KEY`) in the Render dashboard.
5. Set the **Deploy Hook URL** as `RENDER_DEPLOY_HOOK_URL` in your GitHub repo secrets.
6. Every push to `main` will now auto-deploy via the CD pipeline.

### Option B — Streamlit Community Cloud (zero-infra)

1. Push your repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) → **Deploy an app**.
3. Select your repo, branch `main`, and main file `app.py`.
4. Add `GROQ_API_KEY` and `TAVILY_API_KEY` in **Secrets** (TOML format).
5. Click **Deploy** — done. No Docker needed.

### Option C — Railway

```bash
railway login
railway init
railway up
# Set env vars in the Railway dashboard
```

---

## 🔁 CI/CD Pipeline

```
Push to main
    │
    ├── CI (.github/workflows/ci.yml)
    │   ├── Job 1: ruff lint
    │   ├── Job 2: pytest (no API keys needed)
    │   └── Job 3: docker build (validate image)
    │
    └── CD (.github/workflows/cd.yml)  [only on main push]
        ├── Push Docker image → Docker Hub
        │   Tags: latest + sha-<commit>
        └── Trigger Render deploy hook
```

**Required GitHub Secrets for CD:**

| Secret                  | How to get it                                           |
|-------------------------|---------------------------------------------------------|
| `DOCKERHUB_USERNAME`    | Your Docker Hub username                               |
| `DOCKERHUB_TOKEN`       | Docker Hub → Account Settings → Security → Access Token |
| `RENDER_DEPLOY_HOOK_URL`| Render → Service → Settings → Deploy Hooks → Add       |

---

## 📁 Project Structure

```
mars-multi-agent-research-system/
├── .github/
│   └── workflows/
│       ├── ci.yml          # Lint → Test → Docker build
│       └── cd.yml          # Docker Hub push → Render deploy
├── mars/                   # Core Python package
│   ├── __init__.py        # Exposes compiled graph
│   ├── agents.py          # Groq + Tavily Agent Nodes
│   ├── graph.py           # LangGraph workflow definition
│   └── prompts.py         # LLM Prompt Templates
├── tests/
│   ├── test_agents_unit.py # Unit tests (all mocked, no API calls)
│   └── test_tools.py       # _call_llm + researcher tests
├── scripts/
│   └── visualize_graph.py # Visualizes the compiled graph
├── assets/
│   └── research_graph.png # Generated graph diagram
├── app.py                  # Streamlit UI Entrypoint
├── Dockerfile              # Multi-stage production Docker build
├── docker-compose.yml      # Local dev orchestration
├── .env.example            # Safe env template (commit this, not .env)
├── pyproject.toml          # Project metadata + ruff + pytest config
├── Makefile                # Developer shortcuts
└── uv.lock                 # Pinned dependency lockfile
```

---

## 🛡️ Tech Stack

| Layer       | Technology                    |
|-------------|-------------------------------|
| LLM         | Groq — Llama 3.3 70B Versatile |
| Orchestration | LangGraph                   |
| Search      | Tavily Search API             |
| UI          | Streamlit                     |
| Packaging   | uv (Astral)                   |
| Linting     | ruff                          |
| Testing     | pytest + unittest.mock        |
| Container   | Docker (multi-stage)          |
| CI/CD       | GitHub Actions                |
| Hosting     | Render / Streamlit Cloud      |

---

## 📄 License

MIT — see [LICENSE](LICENSE)
>>>>>>> 90f0c3a (Commit Before Deployment)

=======
# 🚀 MARS — Multi-Agent Research System

[![CI](https://github.com/YOUR_USERNAME/mars-multi-agent-research-system/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/mars-multi-agent-research-system/actions/workflows/ci.yml)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)](https://hub.docker.com/r/YOUR_USERNAME/mars-research-system)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2-green)](https://langchain-ai.github.io/langgraph/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> An autonomous multi-agent AI system that researches any topic, writes a structured report, and self-critiques until the output meets quality standards — all powered by **LangGraph**, **Groq (Llama 3.3 70B)**, and **Tavily Search**.

---

## ✨ Features

- 🤖 **4-agent orchestration** — Supervisor, Researcher, Writer, Critiquer
- 🔄 **Iterative refinement loop** — auto-revises drafts based on critique
- 🌐 **Real-time web search** via Tavily
- ⚡ **Groq-powered LLM** — 30 RPM free tier, sub-second inference
- 🖥️ **Streamlit UI** — live agent activity feed and formatted report output
- 🐳 **Docker-ready** — multi-stage build, non-root container, health check
- 🔁 **CI/CD pipeline** — GitHub Actions → Docker Hub → Render

---

## 🏗️ Architecture

```
User Query
    │
    ▼
┌─────────────┐
│  SUPERVISOR │  ◄─── Orchestrates the workflow
└──────┬──────┘       (deterministic + LLM fallback)
       │
       ├──► RESEARCHER  →  Tavily web search + LLM summarisation
       │
       ├──► WRITER      →  Synthesises research into a structured report
       │
       └──► CRITIQUER   →  Reviews draft, requests revisions or APPROVES
                │
                └──► (loop back to WRITER if revisions needed)
                └──► END when APPROVED or max revisions reached
```

**State machine** (LangGraph):
```
START → supervisor → researcher → supervisor → writer → critiquer → supervisor → END
```

---

## ⚡ Quickstart

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- [Groq API key](https://console.groq.com) (free)
- [Tavily API key](https://app.tavily.com) (free)

### 1. Clone & install

```bash
git clone https://github.com/YOUR_USERNAME/mars-multi-agent-research-system.git
cd mars-multi-agent-research-system
uv sync
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and fill in your API keys
```

```env
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

### 3. Run the app

```bash
uv run streamlit run app.py
# → Open http://localhost:8501
```

---

## 🐳 Docker

### Local run with Docker Compose

```bash
# Copy and fill in your .env first
cp .env.example .env

docker compose up --build
# → Open http://localhost:8501
```

### Manual Docker build & run

```bash
docker build -t mars-research-system .

docker run -p 8501:8501 \
  -e GROQ_API_KEY=your_key \
  -e TAVILY_API_KEY=your_key \
  mars-research-system
```

---

## 🧪 Development

### Install dev tools

```bash
uv sync
```

### Run tests (no API keys required)

```bash
uv run pytest tests/ -v
# or
make test
```

### Lint

```bash
uv run ruff check .
# or
make lint
```

### All dev commands

| Command           | Description                        |
|-------------------|------------------------------------|
| `make install`    | Install all dependencies           |
| `make run`        | Start the Streamlit app            |
| `make test`       | Run all unit tests                 |
| `make lint`       | Run ruff linter                    |
| `make lint-fix`   | Auto-fix ruff lint errors          |
| `make docker-up`  | Start with docker-compose          |
| `make docker-down`| Stop docker-compose services       |

---

## 🔑 Environment Variables

| Variable          | Required | Description                                      |
|-------------------|----------|--------------------------------------------------|
| `GROQ_API_KEY`    | ✅ Yes   | Groq API key — [get it here](https://console.groq.com) |
| `TAVILY_API_KEY`  | ✅ Yes   | Tavily Search key — [get it here](https://app.tavily.com) |

---

## 🚀 Deployment

### Option A — Render (Docker, recommended)

1. **Push to GitHub** and ensure CI passes.
2. On [Render](https://render.com), create a **New Web Service**.
3. Select **"Deploy an existing image"** → use `YOUR_DOCKERHUB_USERNAME/mars-research-system:latest`.
4. Set environment variables (`GROQ_API_KEY`, `TAVILY_API_KEY`) in the Render dashboard.
5. Set the **Deploy Hook URL** as `RENDER_DEPLOY_HOOK_URL` in your GitHub repo secrets.
6. Every push to `main` will now auto-deploy via the CD pipeline.

### Option B — Streamlit Community Cloud (zero-infra)

1. Push your repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) → **Deploy an app**.
3. Select your repo, branch `main`, and main file `app.py`.
4. Add `GROQ_API_KEY` and `TAVILY_API_KEY` in **Secrets** (TOML format).
5. Click **Deploy** — done. No Docker needed.

### Option C — Railway

```bash
railway login
railway init
railway up
# Set env vars in the Railway dashboard
```

---

## 🔁 CI/CD Pipeline

```
Push to main
    │
    ├── CI (.github/workflows/ci.yml)
    │   ├── Job 1: ruff lint
    │   ├── Job 2: pytest (no API keys needed)
    │   └── Job 3: docker build (validate image)
    │
    └── CD (.github/workflows/cd.yml)  [only on main push]
        ├── Push Docker image → Docker Hub
        │   Tags: latest + sha-<commit>
        └── Trigger Render deploy hook
```

**Required GitHub Secrets for CD:**

| Secret                  | How to get it                                           |
|-------------------------|---------------------------------------------------------|
| `DOCKERHUB_USERNAME`    | Your Docker Hub username                               |
| `DOCKERHUB_TOKEN`       | Docker Hub → Account Settings → Security → Access Token |
| `RENDER_DEPLOY_HOOK_URL`| Render → Service → Settings → Deploy Hooks → Add       |

---

## 📁 Project Structure

```
mars-multi-agent-research-system/
├── .github/
│   └── workflows/
│       ├── ci.yml          # Lint → Test → Docker build
│       └── cd.yml          # Docker Hub push → Render deploy
├── mars/                   # Core Python package
│   ├── __init__.py        # Exposes compiled graph
│   ├── agents.py          # Groq + Tavily Agent Nodes
│   ├── graph.py           # LangGraph workflow definition
│   └── prompts.py         # LLM Prompt Templates
├── tests/
│   ├── test_agents_unit.py # Unit tests (all mocked, no API calls)
│   └── test_tools.py       # _call_llm + researcher tests
├── scripts/
│   └── visualize_graph.py # Visualizes the compiled graph
├── assets/
│   └── research_graph.png # Generated graph diagram
├── app.py                  # Streamlit UI Entrypoint
├── Dockerfile              # Multi-stage production Docker build
├── docker-compose.yml      # Local dev orchestration
├── .env.example            # Safe env template (commit this, not .env)
├── pyproject.toml          # Project metadata + ruff + pytest config
├── Makefile                # Developer shortcuts
└── uv.lock                 # Pinned dependency lockfile
```

---

## 🛡️ Tech Stack

| Layer       | Technology                    |
|-------------|-------------------------------|
| LLM         | Groq — Llama 3.3 70B Versatile |
| Orchestration | LangGraph                   |
| Search      | Tavily Search API             |
| UI          | Streamlit                     |
| Packaging   | uv (Astral)                   |
| Linting     | ruff                          |
| Testing     | pytest + unittest.mock        |
| Container   | Docker (multi-stage)          |
| CI/CD       | GitHub Actions                |
| Hosting     | Render / Streamlit Cloud      |

---

## 📄 License

MIT — see [LICENSE](LICENSE)

=======
# 🚀 MARS — Multi-Agent Research System

[![CI](https://github.com/YOUR_USERNAME/mars-multi-agent-research-system/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/mars-multi-agent-research-system/actions/workflows/ci.yml)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)](https://hub.docker.com/r/YOUR_USERNAME/mars-research-system)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2-green)](https://langchain-ai.github.io/langgraph/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> An autonomous multi-agent AI system that researches any topic, writes a structured report, and self-critiques until the output meets quality standards — all powered by **LangGraph**, **Groq (Llama 3.3 70B)**, and **Tavily Search**.

---

## ✨ Features

- 🤖 **4-agent orchestration** — Supervisor, Researcher, Writer, Critiquer
- 🔄 **Iterative refinement loop** — auto-revises drafts based on critique
- 🌐 **Real-time web search** via Tavily
- ⚡ **Groq-powered LLM** — 30 RPM free tier, sub-second inference
- 🖥️ **Streamlit UI** — live agent activity feed and formatted report output
- 🐳 **Docker-ready** — multi-stage build, non-root container, health check
- 🔁 **CI/CD pipeline** — GitHub Actions → Docker Hub → Render

---

## 🏗️ Architecture

```
User Query
    │
    ▼
┌─────────────┐
│  SUPERVISOR │  ◄─── Orchestrates the workflow
└──────┬──────┘       (deterministic + LLM fallback)
       │
       ├──► RESEARCHER  →  Tavily web search + LLM summarisation
       │
       ├──► WRITER      →  Synthesises research into a structured report
       │
       └──► CRITIQUER   →  Reviews draft, requests revisions or APPROVES
                │
                └──► (loop back to WRITER if revisions needed)
                └──► END when APPROVED or max revisions reached
```

**State machine** (LangGraph):
```
START → supervisor → researcher → supervisor → writer → critiquer → supervisor → END
```

---

## ⚡ Quickstart

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- [Groq API key](https://console.groq.com) (free)
- [Tavily API key](https://app.tavily.com) (free)

### 1. Clone & install

```bash
git clone https://github.com/YOUR_USERNAME/mars-multi-agent-research-system.git
cd mars-multi-agent-research-system
uv sync
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and fill in your API keys
```

```env
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

### 3. Run the app

```bash
uv run streamlit run app.py
# → Open http://localhost:8501
```

---

## 🐳 Docker

### Local run with Docker Compose

```bash
# Copy and fill in your .env first
cp .env.example .env

docker compose up --build
# → Open http://localhost:8501
```

### Manual Docker build & run

```bash
docker build -t mars-research-system .

docker run -p 8501:8501 \
  -e GROQ_API_KEY=your_key \
  -e TAVILY_API_KEY=your_key \
  mars-research-system
```

---

## 🧪 Development

### Install dev tools

```bash
uv sync
```

### Run tests (no API keys required)

```bash
uv run pytest tests/ -v
# or
make test
```

### Lint

```bash
uv run ruff check .
# or
make lint
```

### All dev commands

| Command           | Description                        |
|-------------------|------------------------------------|
| `make install`    | Install all dependencies           |
| `make run`        | Start the Streamlit app            |
| `make test`       | Run all unit tests                 |
| `make lint`       | Run ruff linter                    |
| `make lint-fix`   | Auto-fix ruff lint errors          |
| `make docker-up`  | Start with docker-compose          |
| `make docker-down`| Stop docker-compose services       |

---

## 🔑 Environment Variables

| Variable          | Required | Description                                      |
|-------------------|----------|--------------------------------------------------|
| `GROQ_API_KEY`    | ✅ Yes   | Groq API key — [get it here](https://console.groq.com) |
| `TAVILY_API_KEY`  | ✅ Yes   | Tavily Search key — [get it here](https://app.tavily.com) |

---

## 🚀 Deployment

### Option A — Render (Docker, recommended)

1. **Push to GitHub** and ensure CI passes.
2. On [Render](https://render.com), create a **New Web Service**.
3. Select **"Deploy an existing image"** → use `YOUR_DOCKERHUB_USERNAME/mars-research-system:latest`.
4. Set environment variables (`GROQ_API_KEY`, `TAVILY_API_KEY`) in the Render dashboard.
5. Set the **Deploy Hook URL** as `RENDER_DEPLOY_HOOK_URL` in your GitHub repo secrets.
6. Every push to `main` will now auto-deploy via the CD pipeline.

### Option B — Streamlit Community Cloud (zero-infra)

1. Push your repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) → **Deploy an app**.
3. Select your repo, branch `main`, and main file `app.py`.
4. Add `GROQ_API_KEY` and `TAVILY_API_KEY` in **Secrets** (TOML format).
5. Click **Deploy** — done. No Docker needed.

### Option C — Railway

```bash
railway login
railway init
railway up
# Set env vars in the Railway dashboard
```

---

## 🔁 CI/CD Pipeline

```
Push to main
    │
    ├── CI (.github/workflows/ci.yml)
    │   ├── Job 1: ruff lint
    │   ├── Job 2: pytest (no API keys needed)
    │   └── Job 3: docker build (validate image)
    │
    └── CD (.github/workflows/cd.yml)  [only on main push]
        ├── Push Docker image → Docker Hub
        │   Tags: latest + sha-<commit>
        └── Trigger Render deploy hook
```

**Required GitHub Secrets for CD:**

| Secret                  | How to get it                                           |
|-------------------------|---------------------------------------------------------|
| `DOCKERHUB_USERNAME`    | Your Docker Hub username                               |
| `DOCKERHUB_TOKEN`       | Docker Hub → Account Settings → Security → Access Token |
| `RENDER_DEPLOY_HOOK_URL`| Render → Service → Settings → Deploy Hooks → Add       |

---

## 📁 Project Structure

```
mars-multi-agent-research-system/
├── .github/
│   └── workflows/
│       ├── ci.yml          # Lint → Test → Docker build
│       └── cd.yml          # Docker Hub push → Render deploy
├── mars/                   # Core Python package
│   ├── __init__.py        # Exposes compiled graph
│   ├── agents.py          # Groq + Tavily Agent Nodes
│   ├── graph.py           # LangGraph workflow definition
│   └── prompts.py         # LLM Prompt Templates
├── tests/
│   ├── test_agents_unit.py # Unit tests (all mocked, no API calls)
│   └── test_tools.py       # _call_llm + researcher tests
├── scripts/
│   └── visualize_graph.py # Visualizes the compiled graph
├── assets/
│   └── research_graph.png # Generated graph diagram
├── app.py                  # Streamlit UI Entrypoint
├── Dockerfile              # Multi-stage production Docker build
├── docker-compose.yml      # Local dev orchestration
├── .env.example            # Safe env template (commit this, not .env)
├── pyproject.toml          # Project metadata + ruff + pytest config
├── Makefile                # Developer shortcuts
└── uv.lock                 # Pinned dependency lockfile
```

---

## 🛡️ Tech Stack

| Layer       | Technology                    |
|-------------|-------------------------------|
| LLM         | Groq — Llama 3.3 70B Versatile |
| Orchestration | LangGraph                   |
| Search      | Tavily Search API             |
| UI          | Streamlit                     |
| Packaging   | uv (Astral)                   |
| Linting     | ruff                          |
| Testing     | pytest + unittest.mock        |
| Container   | Docker (multi-stage)          |
| CI/CD       | GitHub Actions                |
| Hosting     | Render / Streamlit Cloud      |

---

## 📄 License

MIT — see [LICENSE](LICENSE)
>>>>>>> 90f0c3a (Commit Before Deployment)
