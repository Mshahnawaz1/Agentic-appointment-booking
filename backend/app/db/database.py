from datetime import timezone, datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DB_USER = os.getenv("POSTGRES_USER", "myuser")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "mypassword")
DB_NAME = os.getenv("POSTGRES_DB", "school")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    from sqlalchemy import text
    from schemas import Appointment
    Base.metadata.create_all(bind=engine)

    db = None
    try:
        db = next(get_db())

        new_appt = Appointment(
            doctor_name="Dr Smith",
            patient_name="Cola",
            reason="Fever",
            appointment_date=datetime(2026, 1, 19, 10, 0, tzinfo=timezone.utc),
            status="scheduled"
        )
        # db.query(Appointment).all()

        db.add(new_appt)
        db.commit()
        db.refresh(new_appt)

    except Exception as e:
        print(f"Database connection failed: {e}")
    finally:
        if db:
            db.close()
