import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime

BOOKINGS_FILE = Path("data/bookings.json")
SCHEDULE_FILE = Path("data/doctor_schedule.json")

class StorageService:
    def __init__(self):
        # Ensure bookings file exists
        if not BOOKINGS_FILE.exists():
            self.save_bookings({})
    
    def load_bookings(self) -> Dict:
        """Load all bookings from disk"""
        with open(BOOKINGS_FILE, 'r') as f:
            return json.load(f)
    
    def save_bookings(self, bookings: Dict):
        """Save bookings to disk"""
        with open(BOOKINGS_FILE, 'w') as f:
            json.dump(bookings, f, indent=2)
    
    def add_booking(self, booking_id: str, booking_data: dict):
        """Add a new booking"""
        bookings = self.load_bookings()
        bookings[booking_id] = {
            **booking_data,
            "created_at": datetime.now().isoformat()
        }
        self.save_bookings(bookings)
        return bookings[booking_id]
    
    def load_schedule(self) -> Dict:
        """Load doctor schedule"""
        with open(SCHEDULE_FILE, 'r') as f:
            return json.load(f)
    
    def update_schedule(self, schedule: Dict):
        """Update schedule (mark slots as booked)"""
        with open(SCHEDULE_FILE, 'w') as f:
            json.dump(schedule, f, indent=2)
    
    def get_booked_slots(self, date: str) -> List[str]:
        """Get all booked slots for a specific date"""
        bookings = self.load_bookings()
        return [
            b["time"] for b in bookings.values() 
            if b.get("date") == date
        ]

storage = StorageService()