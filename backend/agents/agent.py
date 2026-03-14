"""
The main agent orchestration. 
"""

from langchain_groq.chat_models import ChatGroq
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from dotenv import load_dotenv
import os

from utils.utils import get_today_date

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
   - FORMAT: Always interpret and pass dates to tools in 'YYYY-MM-DD HH:MM' format.
4. Tool Execution: When tool use is triggered, ensure all the required parameters are present.
   - If any parameter is missing, PROMPT the user to provide it before proceeding. Or get them using tools available.

5. Reporting: Translate the tool's raw output (e.g., success/failure) into a clear message for the user.

### Constraints & Guardrails
- Data Format: When a user says "Tomorrow at 10 AM," calculate the exact date based on the current date and format it as 'YYYY-MM-DD HH:MM'.
- One Task at a Time: Only call multiple tools when necessary to fulfill the user's request.
- Finality: After a successful booking or report delivery, thank the user and signal the end of the transaction. Do not suggest further tools unless prompted.
""" + "\n\n### Today's Date: " + get_today_date()

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

async def agent_with_tools(state: AgentState, tools:list) -> AgentState:
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
    if isinstance(last_message, ToolMessage) and last_message.status == "error":
        return {
            "messages": [
                ToolMessage(
                    tool_call_id=last_message.tool_call_id,
                    content=f"Tool failed: {last_message.content}. Explain the error to the user and do not retry."
                )
            ]
        }
    return state
  
def build_agent_graph(tools: list) -> StateGraph:
    graph = StateGraph(AgentState)
    llm_with_tools = model.bind_tools(tools)

    async def agent_node(state: AgentState) -> AgentState:
        response = await llm_with_tools.ainvoke(state["messages"])
        return {"messages": [response]}

    def route_after_tools(state: AgentState) -> str:
        last = state["messages"][-1]
        if isinstance(last, ToolMessage) and last.status == "error":
            return "error_handler"
        return "agent"

    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(tools, handle_tool_errors=True))
    graph.add_node("error_handler", handle_tool_error)

    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", tools_condition)
    graph.add_conditional_edges("tools", route_after_tools)
    graph.add_edge("error_handler", "agent")

    return graph

