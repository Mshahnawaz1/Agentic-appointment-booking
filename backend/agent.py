from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from typing import Annotated, TypedDict, Optional
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage, HumanMessage, AnyMessage
from langgraph.graph.message import add_messages
from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
import json
import requests
import base64
import logging
import os
from dotenv import load_dotenv

#loading 
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

model = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=GROQ_API_KEY
)

#langgraph state
class AgentState(TypedDict):
    human_input: str
    intent: dict
    messages: Annotated[list[AnyMessage], add_messages]

# Intent Classifier Node
def intent_classifier(state: AgentState) -> AgentState:
    INTENT_SCHEMA = {
        "intent": str,
        "appointment_date": Optional[str],
        "doctor_name": Optional[str]}
    
    user_message = state["human_input"]

    # Prompt for intent classification
    prompt = f"""You are an AI assistant that classifies user intents and extracts appointment information.

Analyze the user message and:
1. Classify the intent (possible intents: "book_appointment", "cancel_appointment", "reschedule_appointment", "other")
2. Extract relevant information if the intent is appointment-related

User Message: "{user_message}"

Return ONLY a valid JSON object with the following structure (no additional text or markdown):
{{
    "intent": "the classified intent",
    "appointment_date": "extracted date in YYYY-MM-DD format or null",
    "appointment_time": "extracted time in HH:MM format or null",
    "doctor_name": "extracted doctor name or null",
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
        state["intent"] = json.loads(response)
    except json.JSONDecodeError:
        logging.error("Failed to parse JSON from model response")
        state["intent"] = {"intent": "other", "appointment_date": None, "doctor_name": None}
    return state


def get_today_date() -> str:
    """Helper function to get today's date in YYYY-MM-DD format."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d")


def build_agent_graph() -> StateGraph[AgentState]:
    graph = StateGraph(AgentState)
    graph.add_node("intent_classifier", intent_classifier)

    graph.add_edge(START, "intent_classifier")
    graph.add_edge("intent_classifier", END)

    return graph

if __name__ == "__main__":
    graph = build_agent_graph()

    assistant = graph.compile()

    initial_state: AgentState = {
        "human_input": "I would like to book an appointment with Dr. Smith next Monday at 10 AM.",
        "intent": {},
        "messages": []
    }
    final_state = assistant.invoke(initial_state)
    print("Final State:", final_state)