from pydantic import BaseModel
from datetime import date

# fast api pydantic model
class AppointmentCreate(BaseModel):
    doctor_name: str
    appointment_date: date
    patient_name: str
    reason: str

class AppointmentOut(AppointmentCreate):
    id: int
    status: str

class DoctorAvailability(BaseModel):
    doctor_name: str
    appointment_date: date