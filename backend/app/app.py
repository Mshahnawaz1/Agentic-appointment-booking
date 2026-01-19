from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import datetime

app = FastAPI(title="Simple FastAPI + MCP Demo")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with the Inspector's URL
    allow_methods=["*"],
    allow_headers=["*"],
)

class AskRequest(BaseModel):
    query: str

class AppointmentRequest(BaseModel):
    doctor_name: str
    appointment_date: datetime.date

class doctor_availablity(BaseModel):
    doctor_name: str
    date: datetime.date

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/book_appointment", operation_id="book_appointment")
def get_data(request: AppointmentRequest):
    docter = (request.doctor_name or "").strip()
    date_time = request.appointment_date
    if docter == "Dr Smith":
        return {"message": f"Sorry, {docter} is not available on {date_time}"}

    return {"message": "booking successful"}


@app.post("/doctor_availablity", operation_id="doctor_availablity")
async def get_name(request: doctor_availablity):
    doctor = (request.doctor_name or "").strip()
    date_time = request.date
    if doctor == "Dr Smith":
        return {"message": f"Sorry, {doctor} is not ready on {date_time}"}
    return {"name": "cola"}

mcp = FastApiMCP(app, include_operations=["doctor_availablity", "book_appointment"])
mcp.mount(app, "/mcp")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
