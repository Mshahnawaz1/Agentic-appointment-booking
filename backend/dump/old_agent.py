from langchain_groq.chat_models import ChatGroq
from typing import TypedDict, Annotated, Optional
from langgraph.graph.message import add_messages
from langchain_core.messages import SystemMessage, HumanMessage, AnyMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode


import os
from dotenv import load_dotenv

from app.client import tools
# from utils.utils import logger
from backend.app.utils import get_today_date

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

model = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=GROQ_API_KEY,
    temperature=0
)

PROMPT = """ 
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
"""


class AgentState(TypedDict):
    human_input: str
    messages: Annotated[list[AnyMessage], add_messages]

# Since the mcp is asynchronous, we need to make the agent node async as well. [This was the cause of previous errors.]
async def agent_with_tools(state: AgentState):
    llm_with_tools = model.bind_tools(tools)
    response = await llm_with_tools.ainvoke(state["messages"])
    return {
        "messages": [response],
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
                        content=f"Error: {last_message.content}. Please explain the issue to the user and don't retry the same parameters."                )
            ]
        }
    return state
  
def build_prompt(state):
    messages = state["messages"].copy()
    messages.insert(0, SystemMessage(content=PROMPT.strip()+ "\n\n### Today's Date: " + get_today_date()))
    return {"messages": messages}

def should_continue(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "continue"
    return "end"

def build_agent_graph() -> StateGraph:
    graph = StateGraph(AgentState)
    
    # Streamlined Nodes
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

    # logger.info("Agent graph successfully built.")
    return graph.compile()

def agent_start():
    agent = build_agent_graph()
    sys_msg = SystemMessage(content=PROMPT.strip()+ "\n\n### Today's Date: " + get_today_date())
    agent.invoke({"messages": [sys_msg]})
    return agent

    

if __name__ == "__main__":
    r = build_agent_graph()

    question = "I would like to check availablity of Dr. Smith today at 3 PM."
    state: AgentState = {"messages": [HumanMessage(content=question)]}
    res = r.invoke(state)
    print(res['messages'])