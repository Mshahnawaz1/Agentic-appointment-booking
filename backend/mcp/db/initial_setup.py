"""
setup.py — Seeds the database with initial doctors from doctors.jsonl
Run: 
uv run python mcp/db/initial_setup.py
Note: Run once when first setup of project
"""

import json
import os
from pathlib import Path

from sqlalchemy.orm import Session
from dotenv import load_dotenv

load_dotenv()

# Adjust import path depending on how you run this
from db.database import engine, SessionLocal, Base, Doctor


DOCTORS_JSONL = Path(__file__).parent / "doctors.jsonl"


def load_doctors_from_jsonl(path: Path) -> list[dict]:
    doctors = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                doctors.append(json.loads(line))
    return doctors


def seed_doctors(db: Session, doctors: list[dict]) -> None:
    try:
        existing = db.query(Doctor).count()
    except Exception as e:
        print("Database is not responding")
        return 
    
    if existing > 0:
        print(f"⚠️  Skipping seed — {existing} doctor(s) already exist in the database.")
        return

    for doc in doctors:
        doctor = Doctor(
            doctor_name=doc["doctor_name"],
            specialization=doc.get("specialization"),
        )
        db.add(doctor)

    db.commit()
    print(f"✅ Seeded {len(doctors)} doctors successfully.")


def seed_doctors():
    print("🔧 Connecting to db")
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Database is not responding: Error is {e}")
        raise 

    print(f"📂 Reading doctors from: {DOCTORS_JSONL}")
    doctors = load_doctors_from_jsonl(DOCTORS_JSONL)
    print(f"   Found {len(doctors)} records.")

    db = SessionLocal()
    try:
        seed_doctors(db, doctors)

        # Confirm by printing seeded doctors
        all_doctors = db.query(Doctor).all()
        print("\n📋 Doctors in database:")
        for doc in all_doctors:
            print(f"   [{doc.id}] {doc.doctor_name} — {doc.specialization}")
    except Exception as e:
        db.rollback()
        print(f"❌ Seeding failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_doctors()