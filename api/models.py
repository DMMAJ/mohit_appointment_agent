from pydantic import BaseModel, EmailStr
from typing import List, Literal, Optional
from datetime import date, time

class TimeSlot(BaseModel):
    start_time: str
    end_time: str
    available: bool

class AvailabilityResponse(BaseModel):
    date: str
    available_slots: List[TimeSlot]

class PatientInfo(BaseModel):
    name: str
    email: EmailStr
    phone: str

class BookingRequest(BaseModel):
    appointment_type: Literal["consultation", "followup", "physical", "specialist"]
    date: str
    start_time: str
    patient: PatientInfo
    reason: str

class BookingResponse(BaseModel):
    booking_id: str
    status: str
    confirmation_code: str
    details: dict

class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    action: Optional[str] = None  # "booking_created", "show_slots", etc.
    data: Optional[dict] = None