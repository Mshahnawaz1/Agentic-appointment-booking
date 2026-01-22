# 🩺 Agentic AI Doctor Appointment Assistant

Video demo: [video  link](https://youtu.be/UoAFRcwEC20)

An Agentic AI Assistant for booking doctor appointments and checking appointment availability.
This project uses LangGraph + LangChain to build an agentic workflow that interacts with MCP tools exposed via FastAPI. Appointment and patient records are stored in PostgreSQL, running in Docker.

## Features

- ✅ Check doctor appointment availability
- ✅ Book new appointments via agent actins
- ✅ Store patient & appointment data in PostgreSQL
- ✅ Agentic workflow using LangGraph (multi-step reasoning + tool usage)
- ✅ MCP tool integration using FastAPI endpoints

## Tech Stack

- LangGraph → agentic workflow orchestration
- LangChain → tool calling + LLM integration
- FastAPI → MCP tool endpoints + backend APIs
- PostgreSQL → appointment + patient database
- Docker / Docker Compose → containerized database setup

### Workflows
#### Implemented
![alt text](static/workflow.png)

#### Tested
![alt text](static/image.png)
![alt text](static/output.png)

📌 Architecture Overview

1. User sends a request (example: "Book an appointment with Dr. Sharma tomorrow at 5 PM")

2. LangGraph agent analyzes intent and decides next action

3. Agent calls MCP tools hosted as FastAPI endpoints

4. Tools interact with PostgreSQL to fetch/store data

5. Agent returns final confirmation to the user

## 📂 Project Structure
```
├── backend/
│   ├── app/
│   │   ├── db/
│   │   │   ├── database.py
│   │   │   └── schemas.py
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── app.py
│   │   ├── client.py
│   └── dump/
├── frontend/
├── static/
├── tests/
│   ├── agent_test.py
│   └── db_test.py
```


### Database Schema
![alt text](static/image-1.png)

⚙️ Setup Instructions
1. 
```
git clone github.com/Mshahnawaz1/Agentic-appointment-booking
cd github.com/Mshahnawaz1/Agentic-appointment-booking

Create virtual env (use uv preferred) and install dependecies
pip install -r requirements.txt

Create docker container of database.
docker-compose up -d
```
2. Start PostgreSQL using Docker
```
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypassword
POSTGRES_DB=appointments_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```
```
docker compose up -d
docker ps
```



▶️ Run the FastAPI MCP Tools Server
```
uvicorn app.main:app --reload
FastAPI will be available at:
http://127.0.0.1:8000
Swagger docs: http://127.0.0.1:8000/docs
```

## Future Improvements

Add authentication (JWT / OAuth)

Add doctor schedules & time-slot generation

Add appointment reminder system (email/SMS)

Add evaluation logs for agent tool calls

🤝 Contributing

Contributions are welcome!
Feel free to open issues or submit pull requests for enhancements.

📜 License

This project is licensed under the MIT License (or update based on your preference).
