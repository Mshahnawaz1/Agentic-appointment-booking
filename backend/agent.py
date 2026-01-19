from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage, HumanMessage, AnyMessage
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field
from typing import Annotated, TypedDict, Optional, Literal
import json
import logging
import os
from dotenv import load_dotenv
import datetime

from pydantic import Field

from client import tools, book_appointment, check_availability

#loading 
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

model = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=GROQ_API_KEY
)
print("Model initialized.")

class IntentSchema(BaseModel):
    """Extract intent and entities for the medical booking system."""
    intent: Literal["book_appointment", "check_availability", "other"]
    doctor_name: Optional[str] = Field(None, description="Name of the doctor")
    appointment_date: Optional[str] = Field(None, description="Date (YYYY-MM-DD)")

#langgraph state
class AgentState(TypedDict):
    human_input: str
    extracted_data: dict
    messages: Annotated[list[AnyMessage], add_messages]


# Intent Classifier Node
def intent_classifier(state: AgentState) -> AgentState:
    INTENT_SCHEMA = {
        "intent": str,
        "appointment_date": Optional[datetime.date],
        "doctor_name": Optional[str],
    }
    
    user_message = state["human_input"]

    # Prompt for intent classification
    prompt = f"""You are an AI assistant that classifies user intents and extracts appointment information.

Analyze the user message and:
1. Extract relevant information if the intent is appointment-related

User Message: "{user_message}"

Return ONLY a valid JSON object with the following structure (no additional text or markdown):
{{
    "intent": "the classified intent",
    "appointment_date": "extracted date in YYYY-MM-DD format or null",
    "doctor_name": "extracted doctor name or null",
    "patient_name": "extracted patient name or null",
    "confidence": confidence score between 0 and 1
}}

Rules:
- Set fields to null if information is not mentioned
- For dates, convert relative dates (tomorrow, next Monday) to specific dates
- Today's date is {get_today_date()}
- Be precise with confidence scores

User Input: {user_message}
"""   
# Parse into json
    response = model.invoke(prompt)
    try:
        state["extracted_data"] = json.loads(response.content)
    except json.JSONDecodeError:
        logging.error("Failed to parse JSON from model response")
        state["extracted_data"] = {"intent": "other", "appointment_date": None, "doctor_name": None, "patient_name": None}
    
    return state

def extraction_node(state: AgentState):
    # This node turns "Book Dr. Ahuja tomorrow morning" into structured JSON
    llm = model.with_structured_output(IntentSchema)
    result = llm.invoke(state["human_input"])

    return {"extracted_data": result.content}

def call_book_node(state: AgentState):
    # This node calls your @tool with the extracted JSON
    data = state["extracted_data"]
    # Unpack the JSON directly into your tool
    result = book_appointment.ainvoke({
        "doctor_name": data["doctor_name"],
        "appointment_date": data["appointment_date"],
    })
    return {"tool_result": result}

def get_today_date() -> str:
    """Helper function to get today's date in YYYY-MM-DD format."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d")


def agent_with_tools(state: AgentState):
    llm_with_tools = model.bind_tools(tools)
    user_input = state["human_input"]
    response = llm_with_tools.invoke(user_input)
    return {"messages": [response]}

def build_agent_graph() -> StateGraph[AgentState]:

    graph = StateGraph(AgentState)
    graph.add_node("intent_classifier", intent_classifier)
    graph.add_node("agent", agent_with_tools)
    graph.add_node("tools", ToolNode(tools))

    graph.add_edge(START, "intent_classifier")
    graph.add_edge("intent_classifier", "agent")
    graph.add_conditional_edges("agent", should_continue, {"continue": "tools", "end": END})
    graph.add_edge("tools", "agent")

    print("Graph built successfully.")
    return graph.compile()

def should_continue(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "continue"
    return "end"

if __name__ == "__main__":
    app = build_agent_graph()

    initial_state: AgentState = {
        "human_input": "I would like to check availablity of Dr. Smith next Monday at 10 AM.",
        "intent": {},
    }
    final_state = app.invoke(initial_state)
    print("Final State:", final_state)