from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from db.database import engine
from backend.app.db.schemas import AppointmentCreate, AppointmentOut
import datetime

app = FastAPI(title="Simple FastAPI + MCP Demo")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with the Inspector's URL
    allow_methods=["*"],
    allow_headers=["*"],
)

def on_startup():
    from db.database import Base
    Base.metadata.create_all(bind=engine)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/book_appointment", operation_id="book_appointment")
def get_data(request: AppointmentCreate):
    """
    Use this tool to book an appointment with a doctor.
    """
    docter = (request.doctor_name or "").strip()
    date_time = request.appointment_date
    if docter == "Dr Smith":
        return {"message": f"Successfully booked, {docter} on {date_time}", 
                "status": "success"}

    return {"message": "booking unsuccessful", "status": "failed"}


@app.post("/doctor_availablity", operation_id="doctor_availablity")
async def get_name(request: AppointmentOut):
    """
    Use this tool to check the availablity of doctor
    """
    doctor = (request.doctor_name or "").strip()
    date_time = request.date
    if doctor == "Dr Smith":
        return {"message": f"Success: {doctor} is ready on {date_time}", "status": "success"}
    return {"message": "Doctor not available", "status": "failed"}

@app.get("/appointments", response_model=list[AppointmentOut])
async def list_appointments():
    return db


mcp = FastApiMCP(app, include_operations=["doctor_availablity", "book_appointment"])
mcp.mount(app, "/mcp")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
