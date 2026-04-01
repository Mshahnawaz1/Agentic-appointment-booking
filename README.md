# 🩺 Agentic AI Appointment Assistant

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/🦜🔗_LangGraph-Agentic-green)](https://github.com/langchain-ai/langgraph)
[![LangChain](https://img.shields.io/badge/🦜🔗_LangChain-Providers-blue)](https://python.langchain.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![React](https://img.shields.io/badge/React-TypeScript-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev/)

**An intelligent, agentic healthcare scheduling system powered by LangGraph, MCP tools, and natural language understanding.**

[📺 Watch Demo](https://youtu.be/UoAFRcwEC20) · [🐛 Report Bug](https://github.com/Mshahnawaz1/Agentic-appointment-booking/issues) · [✨ Request Feature](https://github.com/Mshahnawaz1/Agentic-appointment-booking/issues)

</div>

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Database Setup](#database-setup)
  - [Running the App](#running-the-application)
- [Frontend](#-frontend)
- [Testing](#-testing)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Overview

The **Agentic AI Appointment Assistant** is a full-stack, production-grade healthcare scheduling platform. It leverages **LangGraph** for agentic multi-step reasoning and **LangChain** for LLM orchestration, enabling users to check doctor availability and book appointments through natural language — no forms, no dropdowns, just conversation.

The system uses **MCP (Model Context Protocol)** to expose scheduling tools as FastAPI endpoints, backed by a **PostgreSQL** database for persistent storage, and served through a polished **React + TypeScript** frontend.

> **Example:** _"Book an appointment with Dr. Sharma this Friday at 3 PM"_ → The agent checks availability, confirms the slot, creates the record, and responds with a confirmation.

---

## 🚀 Key Features

| Feature | Description |
|---|---|
| 🤖 **Intelligent Reasoning** | LangGraph agent handles multi-step decision-making, slot resolution, and tool orchestration |
| 🗣️ **Natural Language Booking** | End-to-end appointment scheduling via conversational input |
| 📅 **Real-time Availability** | Live doctor schedule checking through integrated MCP tool endpoints |
| 🏥 **Patient Management** | Persistent patient and appointment record management via PostgreSQL |
| ⚡ **MCP Tool Integration** | FastAPI-powered MCP server exposing scheduling tools to the agent |
| 🐳 **Containerized Setup** | Docker Compose for easy, reproducible database bootstrapping |
| 🖥️ **React Frontend** | Full-featured chat interface with Shadcn/UI components |
| 🧪 **Test Suite** | Agent and database integration tests included |

---

## 🛠️ Tech Stack

### Backend
| Layer | Technology |
|---|---|
| **Agent Orchestration** | [LangGraph](https://github.com/langchain-ai/langgraph) |
| **LLM Framework** | [LangChain](https://github.com/langchain-ai/langchain) |
| **API / MCP Server** | [FastAPI](https://fastapi.tiangolo.com/) |
| **Database** | [PostgreSQL](https://www.postgresql.org/) |
| **ORM / Validation** | [Pydantic](https://docs.pydantic.dev/) |
| **Containerization** | [Docker](https://www.docker.com/) & Docker Compose |
| **Package Manager** | [uv](https://github.com/astral-sh/uv) |

### Frontend
| Layer | Technology |
|---|---|
| **Framework** | [React 18](https://react.dev/) + [TypeScript](https://www.typescriptlang.org/) |
| **Build Tool** | [Vite](https://vitejs.dev/) |
| **UI Components** | [Shadcn/UI](https://ui.shadcn.com/) + [Tailwind CSS](https://tailwindcss.com/) |
| **Testing** | [Vitest](https://vitest.dev/) |

---

## 🏛️ Architecture

```
User (Natural Language)
        │
        ▼
  ┌─────────────┐
  │  React UI   │  ← Chat interface (TypeScript + Shadcn/UI)
  └──────┬──────┘
         │ HTTP
         ▼
  ┌─────────────────────┐
  │   FastAPI App        │  ← Entry point / chat handler
  └──────────┬──────────┘
             │
             ▼
  ┌─────────────────────┐
  │   LangGraph Agent   │  ← Reasoning, planning, tool selection
  │   (agent.py)        │
  └──────────┬──────────┘
             │  Tool calls via MCP
             ▼
  ┌─────────────────────┐
  │   MCP Server        │  ← FastAPI endpoints exposing scheduling tools
  │   (server.py)       │
  └──────────┬──────────┘
             │  SQL queries
             ▼
  ┌─────────────────────┐
  │    PostgreSQL DB     │  ← Doctors, patients, appointments
  └─────────────────────┘
```

### Agent Workflow

1. **User Input** — Natural language request arrives at the chat endpoint
2. **Intent Analysis** — LangGraph agent parses intent and identifies required parameters
3. **Tool Selection** — Agent selects appropriate MCP tools (check availability, create booking, etc.)
4. **Tool Execution** — FastAPI MCP server executes the tool against PostgreSQL
5. **Response Generation** — Agent synthesizes results into a natural language confirmation

![Workflow Diagram](static/workflow.png)

---

## 📂 Project Structure

```
agentic-appointment-booking/
│
├── backend/
│   ├── agents/
│   │   ├── agent.py          # LangGraph agent definition & reasoning logic
│   │   ├── mcp_client.py     # MCP client for tool communication
│   │   └── providers.py      # LLM provider configuration
│   │
│   ├── chat/
│   │   ├── chat.py           # Chat handler / conversation manager
│   │   └── prototype.ipynb   # Development prototyping notebook
│   │
│   ├── mcp/
│   │   ├── db/
│   │   │   ├── database.py   # DB connection & session management
│   │   │   ├── doctors.jsonl # Seed data for doctors
│   │   │   ├── initial_setup.py  # DB schema init & seeding
│   │   │   └── schemas.py    # Pydantic models & DB schemas
│   │   ├── client.py         # MCP client utilities
│   │   └── server.py         # FastAPI MCP tool server
│   │
│   ├── tests/
│   │   └── run_cli.py        # CLI test runner for agent interactions
│   │
│   ├── utils/
│   │   └── utils.py          # Shared utility functions
│   │
│   ├── docker-compose.yml    # PostgreSQL container definition
│   ├── Dockerfile            # Backend container image
│   └── pyproject.toml        # Python dependencies (uv)
│
├── frontend/
├── tests/
│   ├── agent_test.py         # Agent integration tests
│   └── db_test.py            # Database tests
├── static/                   # Workflow diagrams & demo assets
└── README.md
```

---

## ⚡ Getting Started

### Prerequisites

Make sure you have the following installed:

- **Python 3.10+**
- **Docker** & **Docker Compose**
- **Node.js 18+** & **npm/bun** (for frontend)
- **[uv](https://github.com/astral-sh/uv)** — fast Python package manager *(recommended)*

---

### Installation

#### 1. Clone the repository

```bash
git clone https://github.com/Mshahnawaz1/Agentic-appointment-booking.git
cd Agentic-appointment-booking
```

#### 2. Set up backend

```bash
cd backend

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate

uv pip install -r pyproject.toml
```

#### 3. Configure environment variables

Copy the example env file and fill in your values:

```bash
cp .env.example .env
```

```env
GOOGLE_API_KEY="REQUIRED"
HF_API = "required"

EMAIL_ADDRESS = "" #For sending emails
APP_PASSWORD = ""

MCP_SERVER_URL="http://localhost:8000/mcp"
DB_URL="postgresql://myuser:mypassword@postgres:5432/school"
```

---

### Database Setup

#### Start the PostgreSQL container

```bash
cd backend
docker-compose up -d
```

#### Initialize the schema and seed doctor data

```bash
python mcp/db/initial_setup.py
```

This will create the required tables and populate them with initial doctor records from `doctors.jsonl`.

---

### Running the Application

Choose the setup that suits you:

<details open>
<summary><b>🐳 Option A — Docker (all services)</b></summary>

```bash
docker-compose up --build
```

That's it. Docker Compose will start the database, MCP server, chat API, and frontend together.

| Service | URL |
|---|---|
| Chat API | http://127.0.0.1:8000 |
| MCP Server | http://127.0.0.1:8001 |
| Frontend | http://localhost:5173 |
| API Docs | http://127.0.0.1:8000/docs |

To stop all services:
```bash
docker-compose down
```

</details>

<details>
<summary><b>🖥️ Option B — Local (without Docker)</b></summary>

**Terminal 1 — MCP Tool Server**
```bash
cd backend
uvicorn mcp.server:app --reload --port 8001
```

**Terminal 2 — Chat API**
```bash
cd backend
uvicorn chat.chat:app --reload --port 8000
```

**Terminal 3 — Frontend**
```bash
cd frontend
npm install && npm run dev
```

| Service | URL |
|---|---|
| Chat API | http://127.0.0.1:8000 |
| MCP Server | http://127.0.0.1:8001 |
| Frontend | http://localhost:5173 |
| API Docs | http://127.0.0.1:8000/docs |

</details>

---

## 🧪 Testing

#### Backend — Agent & Database tests

```bash
# From the project root
python -m pytest tests/

# Or run individual test files
python tests/agent_test.py
python tests/db_test.py
```

#### Backend — CLI agent interaction

```bash
python backend/tests/run_cli.py
```

#### Frontend — Vitest unit tests

```bash
cd frontend
npm run test
```

---

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions are **greatly appreciated**.

1. **Fork** the repository
2. **Create** your feature branch
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. **Commit** your changes
   ```bash
   git commit -m 'Add some AmazingFeature'
   ```
4. **Push** to the branch
   ```bash
   git push origin feature/AmazingFeature
   ```
5. **Open** a Pull Request

Please make sure your code follows the existing style and includes relevant tests.

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.

---

## 🙏 Acknowledgements

- [LangGraph](https://github.com/langchain-ai/langgraph) — Agentic workflow orchestration
- [LangChain](https://github.com/langchain-ai/langchain) — LLM abstraction layer
- [FastAPI](https://fastapi.tiangolo.com/) — High-performance Python API framework
- [Shadcn/UI](https://ui.shadcn.com/) — Beautiful, accessible React components
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) — Tool communication standard

---

<div align="center">
  Made with ❤️ by <a href="https://github.com/Mshahnawaz1">Mshahnawaz1</a>
</div>
