from fastapi import APIRouter, HTTPException
from .models import ChatMessage, ChatResponse
# from services.llm_service import llm_service
from services.llm_service import LLMService
# from services.rag_service import rag_service
from services.rag_service import RAGService
import uuid

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Store conversation history (in-memory for simplicity)
conversations = {}

@router.post("/", response_model=ChatResponse)
def chat(message: ChatMessage):
    """Conversational endpoint - handles both booking and FAQ"""
    
    # Get or create conversation
    conv_id = message.conversation_id or str(uuid.uuid4())
    history = conversations.get(conv_id, [])
    
    # Search FAQs for relevant context
    faq_results = RAGService.search_faq(message.message)
    context = "\n".join([
        f"Q: {r['question']}\nA: {r['answer']}"
        for r in faq_results if r['score'] > 0.5
    ])
    
    # Get LLM response
    response_text = LLMService.chat(
        user_message=message.message,
        context=context,
        conversation_history=history
    )
    
    # Update conversation history
    history.append({"role": "user", "content": message.message})
    history.append({"role": "assistant", "content": response_text})
    conversations[conv_id] = history[-10:]  # Keep last 10 messages
    
    # Extract intent for future action
    intent = LLMService.extract_booking_intent(message.message)
    
    return ChatResponse(
        response=response_text,
        conversation_id=conv_id,
        action=intent.get("intent"),
        data=intent if intent.get("intent") == "booking" else None
    )

@router.post("/ingest-faqs")
def ingest_faqs():
    """Setup Qdrant and ingest FAQ data - run this once"""
    try:
        RAGService.setup_collection()
        RAGService.ingest_faqs()
        return {"message": "FAQs ingested successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))