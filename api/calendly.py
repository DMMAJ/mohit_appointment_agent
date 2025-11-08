from fastapi import APIRouter, HTTPException, Query
from typing import Literal
from datetime import datetime, timedelta
from .models import (
    AvailabilityResponse, 
    BookingRequest, 
    BookingResponse,
    TimeSlot
)
from services.storage_service import storage

router = APIRouter(prefix="/api/calendly", tags=["calendly"])

DURATIONS = {
    "consultation": 30,
    "followup": 15,
    "physical": 45,
    "specialist": 60
}

@router.get("/availability", response_model=AvailabilityResponse)
def get_availability(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    appointment_type: Literal["consultation", "followup", "physical", "specialist"] = Query("consultation")
):
    """Get available slots for a specific date"""
    
    # Validate date
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    if datetime.strptime(date, "%Y-%m-%d").date() < datetime.now().date():
        raise HTTPException(status_code=400, detail="Cannot book appointments in the past")
    
    # Load schedule
    schedule = storage.load_schedule()
    slots = schedule.get(date, generate_default_slots())
    
    # Get already booked slots
    booked_times = storage.get_booked_slots(date)
    
    # Mark booked slots as unavailable
    for slot in slots:
        if slot["start_time"] in booked_times:
            slot["available"] = False
    
    return AvailabilityResponse(
        date=date,
        available_slots=[TimeSlot(**slot) for slot in slots]
    )

@router.post("/book", response_model=BookingResponse)
def book_appointment(booking: BookingRequest):
    """Book an appointment"""
    
    # Validate date
    try:
        booking_date = datetime.strptime(booking.date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")
    
    if booking_date < datetime.now().date():
        raise HTTPException(status_code=400, detail="Cannot book in the past")
    
    # Check if slot is available
    schedule = storage.load_schedule()
    slots = schedule.get(booking.date, generate_default_slots())
    
    requested_slot = next(
        (s for s in slots if s["start_time"] == booking.start_time),
        None
    )
    
    if not requested_slot:
        raise HTTPException(status_code=404, detail="Time slot not found")
    
    # Check if already booked
    booked_times = storage.get_booked_slots(booking.date)
    if booking.start_time in booked_times:
        raise HTTPException(status_code=409, detail="Time slot already booked")
    
    # Create booking
    bookings = storage.load_bookings()
    booking_id = f"APPT-{booking.date}-{len(bookings) + 1:03d}"
    confirmation_code = f"CNF{len(bookings) + 1:05d}"
    
    booking_details = {
        "booking_id": booking_id,
        "date": booking.date,
        "time": booking.start_time,
        "duration": DURATIONS[booking.appointment_type],
        "type": booking.appointment_type,
        "patient": booking.patient.dict(),
        "reason": booking.reason
    }
    
    # Save to disk
    storage.add_booking(booking_id, booking_details)
    
    return BookingResponse(
        booking_id=booking_id,
        status="confirmed",
        confirmation_code=confirmation_code,
        details=booking_details
    )

def generate_default_slots():
    """Generate 9 AM - 5 PM slots"""
    slots = []
    for hour in range(9, 17):
        for minute in [0, 30]:
            start = f"{hour:02d}:{minute:02d}"
            end_minute = minute + 30
            end_hour = hour if end_minute < 60 else hour + 1
            end_minute = end_minute if end_minute < 60 else 0
            end = f"{end_hour:02d}:{end_minute:02d}"
            
            slots.append({
                "start_time": start,
                "end_time": end,
                "available": True
            })
    return slots