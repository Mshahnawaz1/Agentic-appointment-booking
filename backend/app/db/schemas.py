from sqlalchemy import Column, Integer, String, DateTime,Enum, func
from pydantic import BaseModel
from sqlalchemy.orm import declarative_base
from datetime import datetime

import enum

Base = declarative_base()

# fast api pydantic model
class AppointmentCreate(BaseModel):
    doctor_name: str
    appointment_date: datetime
    patient_name: str
    reason: str

class AppointmentOut(AppointmentCreate):
    id: int
    status: str

class AppointmentStatus(str, enum.Enum):
    scheduled = "scheduled"
    cancelled = "cancelled"
    completed = "completed"

class DoctorAvailability(BaseModel):
    doctor_name: str
    appointment_date: datetime

# database model
class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    doctor_name = Column(String(100), nullable=False)
    appointment_date = Column(DateTime(timezone=True), nullable=False)
    patient_name = Column(String(100), nullable=True)
    reason = Column(String(255), nullable=True)
    status = Column(Enum(AppointmentStatus, name="appointment_status"), nullable=False,
    default=AppointmentStatus.scheduled
)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True)