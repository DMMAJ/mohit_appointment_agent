from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.calendly import router as calendly_router
from api.chat import router as chat_router
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Medical Appointment Scheduling API",
    description="Conversational scheduling with LLM + RAG",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(calendly_router)
app.include_router(chat_router)

@app.get("/")
def root():
    return {
        "message": "Medical Appointment Scheduling API",
        "endpoints": {
            "chat": "POST /api/chat - Conversational interface",
            "ingest": "POST /api/chat/ingest-faqs - Setup FAQ database",
            "availability": "GET /api/calendly/availability",
            "book": "POST /api/calendly/book"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)