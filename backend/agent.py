from langchain_groq.chat_models import ChatGroq
from typing import TypedDict, Annotated, Optional
from langgraph.graph.message import add_messages
from langchain_core.messages import SystemMessage, HumanMessage, AnyMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode


import os
from dotenv import load_dotenv

from app.client import tools
# from utils.utils import logger
from utils.utils import get_today_date

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

model = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=GROQ_API_KEY,
    temperature=0
)

PROMPT = """ You are a professional appoitment and reporting assistant. 
Your task is to chat with customers, understand their needs regarding medical appointments,
and assist them in booking appointment, checking availablity using the tools provided.

If information is missing for tool calling ask the user for missing information.

Once the task is done stop the conversation by thanking the user. Don't call any tool after that.
"""


class AgentState(TypedDict):
    human_input: str
    messages: Annotated[list[AnyMessage], add_messages]


def agent_with_tools(state: AgentState):
    llm_with_tools = model.bind_tools(tools)

    return {
        "messages": [llm_with_tools.invoke(state["messages"])],
    }
  
def build_prompt(state):
    messages = state["messages"].copy()
    messages.insert(0, SystemMessage(content=PROMPT.strip()))
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
    graph.add_node("build_prompt", build_prompt)
    graph.add_node("tools", ToolNode(tools))

    graph.add_edge(START, "build_prompt")
    graph.add_edge("build_prompt", "agent")
    graph.add_conditional_edges(
        "agent", 
        should_continue, 
        {
            "continue": "tools", 
            "end": END
        }
    )
    graph.add_edge("tools", "agent")

    # logger.info("Agent graph successfully built.")
    return graph.compile()

if __name__ == "__main__":
    r = build_agent_graph()

    question = "I would like to check availablity of Dr. Smith today at 3 PM."
    state: AgentState = {"messages": [HumanMessage(content=question)]}
    res = r.invoke(state)
    print(res['messages'])