import httpx
from langchain_core.tools import tool
import asyncio

BASE_URL = "http://localhost:8000"

@tool
async def book_appointment(
    doctor_name: str, 
    appointment_date: str,
    patient_name: str = "John Doe",
    reason: str = "General consultation",
):
    """
    Book a medical appointment.
    
    Args:
        doctor_name: Full name of the doctor (e.g., "Dr Smith")
        appointment_date: Date in YYYY-MM-DD format
        patient_name: Name of the patient
        reason: Reason for appointment
    """
    payload = {
        "doctor_name": doctor_name,
        "patient_name": patient_name,
        "appointment_date": appointment_date,
        "reason": reason
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BASE_URL}/book_appointment", json=payload)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        return f"Error booking appointment: {str(e)}"

@tool
async def check_availability(doctor_name: str, appointment_date: str):
    """
    Check if a doctor is available on a specific date.
    
    Args:
        doctor_name: Full name of the doctor (e.g., "Dr Smith")
        appointment_date: Date in YYYY-MM-DD format (e.g., "2024-02-15")
    """
    # Fixed the typo in "appointment_date"
    payload = {"doctor_name": doctor_name, "appointment_date": appointment_date}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/check_doctor_availability",
                json=payload
            )
            response.raise_for_status()
            out = response.json()
            return f"Successfully checked availability: {out}"
    except Exception as e:
        return f"Error checking availability: {str(e)}"

tools = [book_appointment, check_availability]

if __name__ == "__main__":
    async def main():
        input_data = {"doctor_name": "Dr Smith", "appointment_date": "2024-02-15"}
        # Using ainvoke for the async tool
        result = await book_appointment.ainvoke(input_data)         
        print("Availability:", result)

    asyncio.run(main())