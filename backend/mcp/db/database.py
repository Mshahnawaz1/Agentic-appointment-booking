from datetime import timezone, date
from sqlalchemy import create_engine, Column, Integer, String, DATE, DateTime, Enum, func, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
import os
import enum
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DB_URL")
print(f"Connected to database at {DATABASE_URL}")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# status model 
class AppointmentStatus(str, enum.Enum):
    scheduled = "scheduled"
    cancelled = "cancelled"
    completed = "completed"

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    doctor_name = Column(String(100), nullable=False)
    specialization = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    appointments = relationship("Appointment", back_populates="doctor")

# database model
class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    appointment_date = Column(DATE, nullable=False, unique=True)
    patient_name = Column(String(100), nullable=True)
    reason = Column(String(255), nullable=True)
    status = Column(Enum(AppointmentStatus, name="appointment_status"), nullable=False,
    default=AppointmentStatus.scheduled
)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    doctor = relationship("Doctor", back_populates="appointments")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    from sqlalchemy import text
    Base.metadata.create_all(bind=engine)

    db = None
    try:
        db = next(get_db())

        appointment = Appointment(
            doctor_id=1,
            appointment_date=date(2024, 10, 15),
            patient_name="Luna  Doe",
            reason="Regular Checkup",
            status=AppointmentStatus.scheduled
        )
        try:
            db.add(appointment)
            db.commit()
            print("appointment added successfully.")
        except Exception as e:
            db.rollback()
            print(f"Failed to add appointment: {e}")

        docs = db.query(Doctor).all()
        for doc in docs:
            print(f"Doctor ID: {doc.id}, Name: {doc.doctor_name}, Specialization: {doc.specialization} , apointments:{len(doc.appointments)}")
        
    except Exception as e:
        print(f"Database connection failed: {e}")
    finally:
        if db:
            db.close()
