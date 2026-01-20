from datetime import timezone, date
from sqlalchemy import create_engine, Column, Integer, String, DATE, DateTime, Enum, func
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import enum

DB_USER = os.getenv("POSTGRES_USER", "myuser")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "mypassword")
DB_NAME = os.getenv("POSTGRES_DB", "school")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# status model 
class AppointmentStatus(str, enum.Enum):
    scheduled = "scheduled"
    cancelled = "cancelled"
    completed = "completed"

# database model
class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    doctor_name = Column(String(100), nullable=False)
    appointment_date = Column(DATE, nullable=False)
    patient_name = Column(String(100), nullable=True)
    reason = Column(String(255), nullable=True)
    status = Column(Enum(AppointmentStatus, name="appointment_status"), nullable=False,
    default=AppointmentStatus.scheduled
)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True)

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

        new_appt = Appointment(
            doctor_name="Dr Smith",
            patient_name="Cola",
            reason="Fever",
            appointment_date=date(2026, 1, 19),
            status="scheduled"
        )
        appoint = db.query(Appointment).all()
        for a in appoint:
            print(a.doctor_name, a.appointment_date)

        db.add(new_appt)
        db.commit()
        db.refresh(new_appt)

    except Exception as e:
        print(f"Database connection failed: {e}")
    finally:
        if db:
            db.close()
