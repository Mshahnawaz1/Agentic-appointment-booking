# 🩺 Agentic AI Appointment Assistant
<div align= "center">
  
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/🦜🔗_LangChain-Providers-green)](https://python.langchain.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)

</div>
An advanced, agentic workflow for healthcare scheduling. This project leverages **LangGraph** and **LangChain** to create an intelligent assistant capable of checking doctor availability and booking appointments by interacting with **MCP (Model Context Protocol)** tools via FastAPI and a PostgreSQL database.

---

## 📺 Video Demonstration
[**Watch the Agent in Action**](https://youtu.be/UoAFRcwEC20)

---

## 🚀 Key Features

* **Intelligent Reasoning:** Uses LangGraph for multi-step decision-making and tool orchestration.
* **Real-time Availability:** Seamlessly check doctor schedules via integrated MCP tools.
* **Automated Booking:** End-to-end appointment scheduling through natural language.
* **Persistent Storage:** Robust patient and appointment record management using PostgreSQL.
* **Scalable Architecture:** Containerized database setup and FastAPI-driven tool endpoints.

---

## 🛠️ Tech Stack

| Component | Technology |
| :--- | :--- |
| **Orchestration** | [LangGraph](https://github.com/langchain-ai/langgraph) |
| **Agent Framework** | [LangChain](https://github.com/langchain-ai/langchain) |
| **API Layer** | [FastAPI](https://fastapi.tiangolo.com/) (MCP Tool Integration) |
| **Database** | [PostgreSQL](https://www.postgresql.org/) |
| **Containerization** | [Docker](https://www.docker.com/) / Docker Compose |

---

## 🏛️ Architecture Overview

1.  **User Input:** "Book an appointment with Dr. Sharma tomorrow at 5 PM."
2.  **Agent Logic:** The **LangGraph** agent analyzes intent and identifies missing parameters or required data.
3.  **Tool Execution:** The agent invokes **MCP tools** (FastAPI endpoints).
4.  **Data Persistence:** Tools interact with the **PostgreSQL** database to validate or commit records.
5.  **Response:** The agent provides a natural language confirmation to the user.

### Workflow Visualization
![Workflow](static/workflow.png)

---

## 📂 Project Structure

```text
├── backend/
│   ├── app/
│   │   ├── db/            # Database configuration and Pydantic schemas
│   │   ├── agent.py       # LangGraph agent definition & logic
│   │   ├── app.py         # FastAPI main application
│   │   └── client.py      # Interface for tool interactions
│   └── dump/              # SQL dumps/backups
├── frontend/              # Frontend interface (if applicable)
├── static/                # Documentation assets & diagrams
└── tests/                 # Unit and integration tests
```
### 🚀 Getting Started
1. Prerequisites
- Python 3.10+
- Docker & Docker Compose
- uv (Recommended for fast dependency management)
2. Installation and setup
  ``` bash
  # Clone the repository
  git clone [https://github.com/Mshahnawaz1/Agentic-appointment-booking](https://github.com/Mshahnawaz1/Agentic-appointment-booking)
  cd Agentic-appointment-booking
  # Create virtual environment and install dependencies
  uv venv
  source .venv/bin/activate  # Windows: .venv\Scripts\activate
  uv pip install -r requirements.txt
  ```
3. Database Configuration
Create a .env file or export your PostgreSQL environment variables:
```
Code snippet
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypassword
POSTGRES_DB=appointments_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```
Launch the database container:
``` bash
docker-compose up -d
```
4. Running the Application
```Bash
Start the FastAPI server to expose the MCP tools:
uvicorn app.main:app --reload
API URL: http://127.0.0.1:8000
Interactive Docs: http://127.0.0.1:8000/docs
```
### 🤝 Contributing
Contributions are what make the open-source community such an amazing place to learn, inspire, and create.
- Fork the Project
- Create your Feature Branch (git checkout -b feature/AmazingFeature)
- Commit your Changes (git commit -m 'Add some AmazingFeature')
- Push to the Branch (git push origin feature/AmazingFeature)
- Open a Pull Request
