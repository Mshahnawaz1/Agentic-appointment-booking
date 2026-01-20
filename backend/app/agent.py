from langchain_groq.chat_models import ChatGroq
from typing import TypedDict, Annotated, Optional
from langgraph.graph.message import add_messages
from langchain_core.messages import SystemMessage, HumanMessage, AnyMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from dotenv import load_dotenv
import os

from client import tools
from utils import get_today_date

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

model = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=GROQ_API_KEY,
    temperature=0
)

SYS_PROMPT = """ 
### Role
You are a highly efficient Medical Appointment and Reporting Assistant. Your goal is to guide users through the scheduling process with clinical precision and professional warmth.

### Operational Workflow (Graph Logic)
1. Greet: Start by acknowledging the user.
2. Context Retrieval: Check the conversation history for Doctor names, Dates, and Times.
3. Validation:
   - If a specific Doctor/Date/Time is missing, ASK for it.
   - For dates/times, assume the current year is 2026. 
   - FORMAT: Always interpret and pass dates to tools in 'YYYY-MM-DD HH:MM' format.
4. Tool Execution: Once all parameters (e.g., doctor_name, appointment_time) are clear, invoke the tool. 
5. Reporting: Translate the tool's raw output (e.g., success/failure) into a clear message for the user.

### Constraints & Guardrails
- Data Format: When a user says "Tomorrow at 10 AM," calculate the exact date based on the current date (Tuesday, Jan 20, 2026) and format it as '2026-01-21 10:00'.
- One Task at a Time: Do not call multiple tools simultaneously unless necessary.
- Finality: After a successful booking or report delivery, thank the user and signal the end of the transaction. Do not suggest further tools unless prompted.
""" + "\n\n### Today's Date: " + get_today_date()


class AgentState(TypedDict):
    human_input: str
    messages: Annotated[list[AnyMessage], add_messages]

# Since the mcp is asynchronous, we need to make the agent node async as well. [This was the cause of previous errors.]
async def agent_with_tools(state: AgentState):
    llm_with_tools = model.bind_tools(tools)
    response = await llm_with_tools.ainvoke(state["messages"])
    return {
        "messages": [response]
    }

def handle_tool_error(state):
    """
    This node intercepts the output from the 'tools' node. 
    If an error occurred, it formats a message telling the agent what happened.
    """
    last_message = state["messages"][-1]
    if "error" in last_message.content.lower():
        return {
            "messages": [
                ToolMessage(
                    tool_call_id=last_message.tool_call_id,
                    content=f"Error: {last_message.content}. Please explain the error in human readable form and dont try to call the tool again."
                )
            ]
        }
    return state
  
def build_agent_graph() -> StateGraph:
    graph = StateGraph(AgentState)
    
    graph.add_node("agent", agent_with_tools)
    graph.add_node("error_handler", handle_tool_error)
    graph.add_node("tools", ToolNode(tools))

    graph.add_edge(START, "agent")
    graph.add_conditional_edges(
        "agent", 
        tools_condition
    )
    graph.add_edge("tools", "error_handler")
    graph.add_edge("error_handler", "agent")
    # graph.add_edge('agent', END)

    # logger.info("Agent graph successfully built.")
    return graph

