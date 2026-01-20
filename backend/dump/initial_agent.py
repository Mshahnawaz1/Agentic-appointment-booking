from langchain_groq import ChatGroq
from typing import Annotated, TypedDict, Optional
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage, HumanMessage, AnyMessage
from langgraph.graph.message import add_messages
from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
import json
import logging
import os
from dotenv import load_dotenv
import datetime

from backend.app.client import tools

#loading 
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

model = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=GROQ_API_KEY,
    temperature=0
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#langgraph state


# Intent Classifier Node
def intent_classifier(state: AgentState) -> AgentState:
    INTENT_SCHEMA = {
        "intent": str,
        "appointment_date": Optional[datetime.date],
        "doctor_name": Optional[str],
        "patient_name": Optional[str]
    }
    
    user_message = state["human_input"]

    # Prompt for intent classification
    prompt = f"""
    You are helpful medical appointment booking assistant AI assistant that classifies user intents and extracts appointment information.

Analyze the user message and:
1. Classify the intent (possible intents: "book_appointment", "cancel_appointment", "reschedule_appointment", "other")
2. Extract relevant information if the intent is appointment-related

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
    logger.info(f"Intent Classifier Response: {response.content}")

    try:
        state["intent"] = json.loads(response.content)
    except json.JSONDecodeError:
        logging.error("Failed to parse JSON from model response")
        state["intent"] = {"intent": "other", "appointment_date": None, "doctor_name": None, "patient_name": None}
    return state


def get_today_date() -> str:
    """Helper function to get today's date in YYYY-MM-DD format."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d")


from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage



def agent_with_tools(state: AgentState):
    # 1. Provide Context: Give the model the date and its role here.
    # This replaces the need for a separate intent_classifier node.
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    system_prompt = SystemMessage(content=(
        f"You are a medical booking assistant. Today's date is {today}. "
        "Use the provided tools to check availability or book appointments. "
        "If information is missing (like a date), ask the user for it."
    ))
    
    llm_with_tools = model.bind_tools(tools)
    

    
    # We return the response; add_messages handles the appending
    return {"messages": [response]}



if __name__ == "__main__":
    app = build_agent_graph()

    initial_state: AgentState = {
        "human_input": "I would like to check the availability of Dr. Smith today.",
        "intent": {},
    }
    final_state = app.invoke(initial_state)
    print("Final State:", final_state)