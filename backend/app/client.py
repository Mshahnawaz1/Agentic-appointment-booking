import httpx
from langchain_core.tools import tool
import datetime
import asyncio


BASE_URL = "http://localhost:8000"

@tool
def book_appointment(
    doctor_name: str, 
    appointment_date: str,
    appointment_time: str = "10:00",  # default
    reason: str = "General consultation",  # default
):
    """
    Book a medical appointment
    
    Args:
        doctor_name: Full name of the doctor (e.g., "Dr Smith")
        appointment_date: Date in YYYY-MM-DD format
        appointment_time: Time in HH:MM format (24-hour), default "10:00"
        reason: Reason for appointment, default "General consultation"
    """
    payload = {
        "doctor_name": doctor_name,
        "appointment_date": appointment_date,
        }
    print("Booking appointment with payload:", payload)

    with httpx.Client() as client:
        response = client.post(f"{BASE_URL}/book_appointment", json={
            "doctor_name": doctor_name,
            "appointment_date": appointment_date,
        })
        return response.json()

@tool
def check_availability(doctor_name: str, date: str):
    """
    Check if a doctor is available on a specific date
    
    Args:
        doctor_name: Full name of the doctor (e.g., "Dr Smith")
        date: Date in YYYY-MM-DD format (e.g., "2024-02-15")
    """

    payload = {"doctor_name": doctor_name, "date": date}
    print("Checking availability with payload:", payload)

    with httpx.Client() as client:
        response = client.post(
            f"{BASE_URL}/doctor_availablity",
            json=payload
        )
        out= response.json()
        return "successfuly checked availability: "

tools = [book_appointment, check_availability]

if __name__ == "__main__":
    import asyncio

    async def main():
        # Example usage of the tools
        input_data = {"doctor_name": "Dr Smith", "date": "2024-02-15"}

        result = await check_availability.ainvoke(input_data)        
        print("Availability:", result)

    asyncio.run(main())