import uuid
from fastapi import FastAPI, Depends, HTTPException
from fastapi_mcp import FastApiMCP
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from pydantic import BaseModel

from db.database import engine, get_db, Base
from db.schemas import BookAppointment, Tool_response, AppointmentOut, DoctorAvailability, Doctor_schema, Appointment_schema
from db.database import Appointment, Base, Doctor
from datetime import date

from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, SystemMessage
from agent import build_agent_graph, SYS_PROMPT

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ✅ startup
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="Simple FastAPI + MCP", lifespan=lifespan)
agent_app = build_agent_graph().compile(checkpointer=MemorySaver())

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/book_appointment", response_model=Tool_response, operation_id="book_appointment")
async def book_appointment(request: BookAppointment, db: Session = Depends(get_db)):
    """
    Use this tool to book an appointment with a doctor. With the cumpulsory fields being doctor_id and appointment_date."""
    doctor_id = request.doctor_id
    doctor_exists = db.query(Doctor).filter(Doctor.id == doctor_id).first()

    appointment_available = (
        db.query(Appointment)
        .filter(Appointment.doctor_id == doctor_id)
        .filter(Appointment.appointment_date == request.appointment_date)
        .first()
    )
    if not doctor_exists:
        res = {"message": f"Doctor not found for the id: {doctor_id}", "status": "failed", "data": None}
        return res
    if appointment_available:
        res = {"message": f"Slot already booked for this doctor on {request.appointment_date}", "status": "failed", "data": None}
        return res

    new_appt = Appointment(
        doctor_id=doctor_id,
        patient_name=request.patient_name,
        reason=request.reason,
        appointment_date=request.appointment_date,
    )

    try:
        db.add(new_appt)
        db.commit()
        db.refresh(new_appt)
    except Exception as e:
        db.rollback()
        res = {"message": f"Failed to book appointment: {e}", "status": "failed", "data": None}
        return res
    res = {"message": f"Appointment booked successfully", "status": "success", "data": {"appointment_id": new_appt.id}}
    return res

@app.post("/check_doctor_availability/", response_model=Tool_response, operation_id="doctor_availability")
async def doctor_availability(request: DoctorAvailability, db: Session = Depends(get_db)):
    """
    Use this tool to check the availability of a doctor. With compulsory fields being doctor_id and appointment_date.
    """
    doctor = request.doctor_id

    existing = (
        db.query(Appointment)
        .filter(Appointment.doctor_id == doctor)
        .filter(Appointment.appointment_date == request.appointment_date)
        .filter(Appointment.status == "scheduled")
        .first()
    )

    if existing:
        return {"message": f"Doctor NOT available at {request.appointment_date}", "status": "failed", "data": None}
    return {"message": f"Doctor available at {request.appointment_date}", "status": "success", "data": None}

@app.post("/list_doctors", response_model=list[Doctor_schema], operation_id="list_doctors")
def list_doctors(db: Session = Depends(get_db)):
    """This endpoint retrieves all doctors from the database.
    """
    return db.query(Doctor).all()

@app.get("/appointments", response_model=list[Appointment_schema], operation_id="check_all_appointments")
def list_appointments(db: Session = Depends(get_db)):
    """This endpoint retrieves all appointments for doctor from the database. It requires doctor_id as input.
    """
    return db.query(Appointment).all()

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


# mcp mounting
mcp = FastApiMCP(app, include_operations=["doctor_availability", "book_appointment", "check_all_appointments"])
mcp.mount(app, "/mcp")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
