from pydantic import BaseModel, ConfigDict
from datetime import date

# fast api pydantic model
class BookAppointment(BaseModel):
    doctor_id: int
    appointment_date: date
    patient_name: str | None
    reason: str | None

class AppointmentOut(BookAppointment):
    id: int
    status: str

class Tool_response(BaseModel):
    message: str
    status : str
    data : dict | None

class DoctorAvailability(BaseModel):
    doctor_id: int
    appointment_date: date

class Doctor_schema(BaseModel):
    id: int
    doctor_name: str
    specialization: str | None
    model_config = ConfigDict(from_attributes=True)

class Appointment_schema(BaseModel):
    id: int
    doctor_id: int
    appointment_date: date
    patient_name: str | None
    reason: str | None
    status: str
    # This makes output to be read as json from orm objects
    model_config = ConfigDict(from_attributes=True)