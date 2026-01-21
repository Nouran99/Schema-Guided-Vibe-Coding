from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
services_db = {}
availability_db = {}
customers_db = {}
appointments_db = {}
counter = {"service": 1, "availability": 1, "customer": 1, "appointment": 1}

# Models
class Service(BaseModel):
    name: str
    duration_minutes: int
    description: str = ""

class AvailabilitySlot(BaseModel):
    start_time: datetime
    end_time: datetime
    service_id: int

class Customer(BaseModel):
    name: str
    email: str
    phone: str = ""

class Appointment(BaseModel):
    customer_id: int
    service_id: int
    slot_id: int
    status: str = "booked"

class AppointmentUpdate(BaseModel):
    status: Optional[str] = None
    slot_id: Optional[int] = None

# Endpoints
@app.get("/api/services")
def get_services() -> List[dict]:
    return list(services_db.values())

@app.post("/api/services")
def create_service(service: Service) -> dict:
    service_id = counter["service"]
    service_dict = {"id": service_id, **service.dict()}
    services_db[service_id] = service_dict
    counter["service"] += 1
    return service_dict

@app.post("/api/availability")
def create_availability(slot: AvailabilitySlot) -> dict:
    if slot.service_id not in services_db:
        raise HTTPException(status_code=404, detail="Service not found")
    service_duration = services_db[slot.service_id]["duration_minutes"]
    slot_duration = (slot.end_time - slot.start_time).seconds // 60
    if slot_duration != service_duration:
        raise HTTPException(status_code=400, detail=f"Slot duration must be {service_duration} minutes")
    slot_id = counter["availability"]
    slot_dict = {"id": slot_id, **slot.dict()}
    availability_db[slot_id] = slot_dict
    counter["availability"] += 1
    return slot_dict

@app.get("/api/availability")
def get_availability(service_id: Optional[int] = None) -> List[dict]:
    booked_slots = [a["slot_id"] for a in appointments_db.values() if a["status"] == "booked"]
    available = [slot for slot in availability_db.values() if slot["id"] not in booked_slots]
    if service_id:
        available = [slot for slot in available if slot["service_id"] == service_id]
    return available

@app.post("/api/customers")
def create_customer(customer: Customer) -> dict:
    for cust in customers_db.values():
        if cust["email"] == customer.email:
            return cust
    customer_id = counter["customer"]
    customer_dict = {"id": customer_id, **customer.dict()}
    customers_db[customer_id] = customer_dict
    counter["customer"] += 1
    return customer_dict

@app.post("/api/appointments")
def create_appointment(appointment: Appointment) -> dict:
    if appointment.slot_id not in availability_db:
        raise HTTPException(status_code=404, detail="Slot not found")
    for appt in appointments_db.values():
        if appt["slot_id"] == appointment.slot_id and appt["status"] == "booked":
            raise HTTPException(status_code=400, detail="Slot already booked")
    appointment_id = counter["appointment"]
    appointment_dict = {"id": appointment_id, "created_at": datetime.now(), **appointment.dict()}
    appointments_db[appointment_id] = appointment_dict
    # Booking confirmation (US009)
    if appointment.customer_id in customers_db:
        customer_email = customers_db[appointment.customer_id]["email"]
        print(f"[EMAIL] Booking confirmation sent to {customer_email} for appointment {appointment_id}")
    counter["appointment"] += 1
    return appointment_dict

@app.get("/api/appointments")
def get_appointments() -> List[dict]:
    # Email reminders (US007)
    for appt in appointments_db.values():
        if appt["status"] == "booked":
            slot = availability_db.get(appt["slot_id"])
            if slot:
                time_until = (slot["start_time"] - datetime.now()).total_seconds() / 3600
                if 24 <= time_until <= 48:
                    customer = customers_db.get(appt["customer_id"])
                    if customer:
                        print(f"[REMINDER] 24h reminder sent to {customer['email']} for appointment {appt['id']}")
    return list(appointments_db.values())

@app.put("/api/appointments/{appointment_id}")
def update_appointment(appointment_id: int, update: AppointmentUpdate) -> dict:
    if appointment_id not in appointments_db:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if update.slot_id:
        if update.slot_id not in availability_db:
            raise HTTPException(status_code=404, detail="New slot not found")
        for appt in appointments_db.values():
            if appt["slot_id"] == update.slot_id and appt["status"] == "booked" and appt["id"] != appointment_id:
                raise HTTPException(status_code=400, detail="New slot already booked")
    if update.status:
        appointments_db[appointment_id]["status"] = update.status
    if update.slot_id:
        appointments_db[appointment_id]["slot_id"] = update.slot_id
    return appointments_db[appointment_id]
