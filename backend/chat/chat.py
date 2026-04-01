"""
Main chat interface also ruunnig the agent instance

Run: 
uv run chat/chat.py
PYTHONPATH=. uv run chat/chat.py -- this solves the import error
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.concurrency import asynccontextmanager
from langchain_core.messages import HumanMessage, SystemMessage
from starlette.middleware.cors import CORSMiddleware
import uuid
from pydantic import BaseModel
from langgraph.checkpoint.memory import MemorySaver

from agents.agent import build_agent_graph, SYS_PROMPT
from agents.mcp_client import mcp_tools


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    global agent_app, tools
    tools = []
    try:
        tools = await mcp_tools()
    except Exception as e:
        print("Tools not loaded")
    agent_app = build_agent_graph(tools).compile(checkpointer=MemorySaver())
    print("Starting up... chat")
    yield
    print("Shutting down...")

app = FastAPI(title="Chat interface + MCP", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to the trusted origins
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

class ChatRequest(BaseModel):
    message: str
    thread_id: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    thread_id = request.thread_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
   
# Check if the thread exists. (for sys prompt)
    try: 
        state = await agent_app.aget_state(config)
        if not state.values:
            # First time this thread is used: Inject System + Human
            initial_input = {
                "messages": [
                    SystemMessage(content=SYS_PROMPT),
                    HumanMessage(content=request.message)
                ]
            }
        else:
            # Thread exists: Just add the new HumanMessage
            # LangGraph's 'add_messages' reducer appends this to history automatically
            initial_input = {
                "messages": [HumanMessage(content=request.message)]
            }

        final_state = await agent_app.ainvoke(initial_input, config=config)
        assistant_response = final_state["messages"][-1].content
        return {
            "response": assistant_response,
            "thread_id": thread_id  # Return it so the frontend can send it back next time
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("chat:app", host="0.0.0.0", port=8001, reload=True)
