import uuid
from fastapi import FastAPI, Depends, HTTPException
from fastapi_mcp import FastApiMCP
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from pydantic import BaseModel

from db.database import engine, get_db, Base
from db.schemas import AppointmentCreate, AppointmentOut, DoctorAvailability
from db.database import Appointment, Base
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

@app.post("/book_appointment", operation_id="book_appointment")
async def book_appointment(request: AppointmentCreate, db: Session = Depends(get_db)):
    """
    Use this tool to book an appointment with a doctor.With the cumpulsory fields being doctor_name and appointment_date."""
    doctor = request.doctor_name.strip()
    print("Appointment date is", request.appointment_date)

    # appointment_date = date(request.appointment_date)

    # check if already booked (same doctor + same time)
    existing = (
        db.query(Appointment)
        .filter(Appointment.doctor_name == doctor)
        .filter(Appointment.appointment_date == request.appointment_date)
        .first()
    )

    if existing:
        raise HTTPException(status_code=409, detail="Slot already booked for this doctor at that time")

    new_appt = Appointment(
        doctor_name=doctor,
        patient_name=request.patient_name,
        reason=request.reason,
        appointment_date=request.appointment_date,
        status="scheduled",
    )

    db.add(new_appt)
    db.commit()
    db.refresh(new_appt)

    return new_appt

@app.post("/check_doctor_availability", operation_id="doctor_availability")
async def doctor_availability(request: DoctorAvailability, db: Session = Depends(get_db)):
    """
    Use this tool to check the availability of a doctor on a given date.
    """
    doctor = request.doctor_name.strip()

    existing = (
        db.query(Appointment)
        .filter(Appointment.doctor_name == doctor)
        .filter(Appointment.appointment_date == request.appointment_date)
        .filter(Appointment.status == "scheduled")
        .first()
    )

    if existing:
        return {"message": f"Doctor NOT available at {request.appointment_date}", "status": "failed"}
    return {"message": f"Doctor available at {request.appointment_date}", "status": "success"}

@app.get("/appointments", response_model=list[AppointmentOut])
def list_appointments(db: Session = Depends(get_db)):
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
