import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.db.database import Base, Appointment
import os
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DB_URL")

engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def db():
    """Create a clean database for testing."""
    # Create tables in the Docker DB
    Base.metadata.create_all(bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Optional: Drop tables after test if you want a complete reset
        Base.metadata.drop_all(bind=engine)

def test_create_appointment(db):
    """Test inserting an appointment into the Docker Postgres DB."""
    from datetime import date
    
    # 1. Create a mock appointment
    new_appointment = Appointment(
        doctor_name="Dr. House",
        appointment_date=date(2026, 5, 20),
        patient_name="John Smith",
        reason="Limping"
    )
    
    # 2. Add to DB
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    
    # 3. Assertions
    assert new_appointment.id is not None
    assert new_appointment.doctor_name == "Dr. House"

def test_query_appointment(db):
    """Test retrieving the appointment we just created."""
    # This relies on the previous test having run, or a fresh insert
    appointment = db.query(Appointment).filter_by(doctor_name="Dr. House").first()
    assert appointment is not None
    assert appointment.patient_name == "John Smith"