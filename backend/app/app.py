import uuid
from fastapi import FastAPI, Depends, HTTPException
from fastapi_mcp import FastApiMCP
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from pydantic import BaseModel
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from pydantic import BaseModel, EmailStr, Field

from db.schemas import Tool_response
from datetime import date
from langchain_core.messages import HumanMessage, SystemMessage

from db.database import engine, get_db, Base
from db.schemas import BookAppointment, Tool_response, AppointmentOut, DoctorAvailability, Doctor_schema, Appointment_schema
from db.database import Appointment, Base, Doctor
from agent import build_agent_graph, SYS_PROMPT
from mcp_client import mcp_tools

from dotenv import load_dotenv
load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")  
APP_PASSWORD = os.getenv("APP_PASSWORD")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    print("Starting up...mcp tools")
    # Base.metadata.create_all(bind=engine)
    yield
    print("Shutting down...")

app = FastAPI(title="Simple FastAPI + MCP", lifespan=lifespan)

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
    res = {"message": f"Appointment booked successfully", "status": "success", "data": {"appointment_id": new_appt.id, "doctor_name": doctor_exists.doctor_name, "appointment_date": str(new_appt.appointment_date)}}
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
    """This endpoint retrieves all doctors with their doctor_id from the database.
    """
    return db.query(Doctor).all()

@app.get("/appointments", response_model=list[Appointment_schema], operation_id="check_all_appointments")
def list_appointments(db: Session = Depends(get_db)):
    """This endpoint retrieves all appointments for doctor from the database. It requires doctor_id as input.
    """
    return db.query(Appointment).all()

class SendEmailRequest(BaseModel):
    to_email: EmailStr = Field(..., description="Receiver email address")
    subject: str = Field(..., min_length=1, max_length=150)
    body: str = Field(..., min_length=1, description="Email message body")
    body_type: str = Field("plain", description="plain or html")


@app.post("/send_email_gmail", operation_id="send_email_gmail", response_model=Tool_response)
async def send_email_gmail(request: SendEmailRequest):
    """
    This tool is used to send confirmation email to patients using Gmail.
    """
    gmail_address = os.getenv("EMAIL_ADDRESS")
    gmail_app_password = os.getenv("APP_PASSWORD")

    if not gmail_address or not gmail_app_password:
        res = {"message": f"Environment variables EMAIL_ADDRESS or APP_PASSWORD are missing", "status": "error", "data": {}}
        return res

    try:
        msg = MIMEMultipart()
        msg["From"] = gmail_address
        msg["To"] = request.to_email
        msg["Subject"] = request.subject

        mime_type = "html" if request.body_type.lower() == "html" else "plain"
        msg.attach(MIMEText(request.body, mime_type))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(gmail_address, gmail_app_password)
            server.sendmail(gmail_address, request.to_email, msg.as_string())

        return {"message": "Email sent successfully", "status": "success", "data": {}}

    except Exception as e:
        return {"message": f"Failed to send email: {str(e)}", "status": "error", "data": {}}
    
# mcp mounting
mcp = FastApiMCP(app, include_operations=["doctor_availability", "book_appointment", "check_all_appointments","list_doctors", "send_email_gmail"])
mcp.mount(mount_path="/mcp")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
# uv run uvicorn app:app --reload 