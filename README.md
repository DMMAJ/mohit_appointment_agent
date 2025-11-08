# Medical Appointment Scheduling - Complete System

FastAPI backend with conversational AI (LLM + RAG) for medical appointment scheduling.

## Features
✅ Conversational chat interface (Groq LLM)
✅ FAQ answering with RAG (Qdrant)
✅ Persistent booking storage (JSON file)
✅ Mock Calendly API endpoints
✅ Multiple appointment types

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your Groq and Qdrant credentials
```

### 3. Initialize FAQ Database (Run Once)
```bash
# Start the server first
python main.py

# Then in another terminal:
curl -X POST http://localhost:8000/api/chat/ingest-faqs

OR
# Use fast API's /docs for all testing.
```

### 4. Use the System

#### Option A: Conversational Interface (Recommended)
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I need to book an appointment for a headache"
  }'
```

#### Option B: Direct API Calls
```bash
# Get availability
curl "http://localhost:8000/api/calendly/availability?date=2025-01-15&appointment_type=consultation"

# Book appointment
curl -X POST http://localhost:8000/api/calendly/book \
  -H "Content-Type: application/json" \
  -d '{
    "appointment_type": "consultation",
    "date": "2025-01-15",
    "start_time": "09:00",
    "patient": {
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+1-555-0100"
    },
    "reason": "Annual checkup"
  }'
```

## Data Persistence
- **Bookings**: Saved in `data/bookings.json`
- **Schedule**: Read from `data/doctor_schedule.json`
- **FAQs**: Stored in Qdrant Cloud

## Architecture
1. User sends message → Chat endpoint
2. LLM understands intent + RAG retrieves relevant FAQs
3. System responds naturally or books appointment
4. All bookings saved to disk

## Testing

Access Swagger UI at: http://localhost:8000/docs
