from fastapi import FastAPI, Depends, HTTPException
from fastapi_mcp import FastApiMCP
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from db.database import engine, get_db, SessionLocal, Base
from db.schemas import AppointmentCreate, AppointmentOut, Appointment, DoctorAvailability

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ✅ startup
    Base.metadata.create_all(bind=engine)
    yield

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

@app.post("/book_appointment", operation_id="book_appointment")
def book_appointment(request: AppointmentCreate, db: Session = Depends(get_db)):
    """
    Use this tool to book an appointment with a doctor.With the cumpulsory fields being doctor_name and appointment_date."""
    doctor = request.doctor_name.strip()

    # check if already booked (same doctor + same time)
    existing = (
        db.query(Appointment)
        .filter(Appointment.doctor_name == doctor)
        .filter(Appointment.date_time == request.appointment_date)
        .first()
    )

    if existing:
        raise HTTPException(status_code=409, detail="Slot already booked for this doctor at that time")

    new_appt = Appointment(
        doctor_name=doctor,
        patient_name=request.patient_name,
        reason=request.reason,
        date_time=request.appointment_date,
        status="scheduled",
    )

    db.add(new_appt)
    db.commit()
    db.refresh(new_appt)

    return new_appt

@app.post("/check_doctor_availability", operation_id="doctor_availability")
def doctor_availability(request: DoctorAvailability, db: Session = Depends(get_db)):
    """
    Use this tool to check the availability of a doctor on a given date.
    """
    doctor = request.doctor_name.strip()

    existing = (
        db.query(Appointment)
        .filter(Appointment.doctor_name == doctor)
        .filter(Appointment.date_time == request.appointment_date)
        .filter(Appointment.status == "scheduled")
        .first()
    )

    if existing:
        return {"message": f"Doctor NOT available at {request.appointment_date}", "status": "failed"}
    return {"message": f"Doctor available at {request.appointment_date}", "status": "success"}

@app.get("/appointments", response_model=list[AppointmentOut])
def list_appointments(db: Session = Depends(get_db)):
    return db.query(Appointment).all()


# mcp mounting
mcp = FastApiMCP(app, include_operations=["doctor_availablity", "book_appointment"])
mcp.mount(app, "/mcp")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app0:app", host="0.0.0.0", port=8000, reload=True)
