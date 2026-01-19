import httpx
from langchain_core.tools import tool
import datetime
import asyncio


BASE_URL = "http://localhost:8000"

@tool
def book_appointment(doctor_name: str, appointment_date: str, appointment_time: str, reason: str, phone: str = None):
    """Book a medical appointment for a patient"""
    with httpx.Client() as client:
        response = client.post(f"{BASE_URL}/book_appointment", json={
            "doctor_name": doctor_name,
            "appointment_date": appointment_date,
        })
        return response.json()

@tool
def check_availability(doctor_name: str, date: str):
    """Check if a doctor is available on a specific date"""
    with httpx.Client() as client:
        response = client.post(
            f"{BASE_URL}/doctor_availablity",
            json={"doctor_name": doctor_name, "date": date}
        )
        return response.json()

tools = [book_appointment, check_availability]

if __name__ == "__main__":
    import asyncio

    async def main():
        # Example usage of the tools
        input_data = {"doctor_name": "Dr Smith", "date": "2024-02-15"}

        result = await check_availability.ainvoke(input_data)        
        print("Availability:", result)

    asyncio.run(main())