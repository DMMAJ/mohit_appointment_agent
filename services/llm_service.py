from groq import Groq
import os
import json
from dotenv import load_dotenv

load_dotenv()

class LLMService:

    def __init__(self):
        key = os.getenv("GROQ_API_KEY")
        print("GROQ API Key:", key)
        try:
            self.client = Groq(api_key=key)
            self.model = "llama-3.3-70b-versatile"
        except Exception as e:
            print("Error initializing LLMService:", e)
            self.client = None
            self.model = None

    def chat(self, user_message: str, context: str = "", conversation_history: list = None) -> str:
        """Send message to LLM with context"""
        
        system_prompt = """You are a helpful medical appointment scheduling assistant.
Your job is to:
1. Help users book medical appointments
2. Answer questions about the clinic using the provided context
3. Be friendly, empathetic, and professional

When users want to book appointments, gather:
- Reason for visit
- Preferred date/time
- Contact information (name, phone, email)

Available appointment types:
- consultation (30 min)
- followup (15 min)
- physical (45 min)
- specialist (60 min)
"""
        
        if context:
            system_prompt += f"\n\nContext (Clinic Info):\n{context}"
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # if conversation_history:
        #     messages.extend(conversation_history)
        
        messages.append({"role": "user", "content": user_message})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    
    def extract_booking_intent(self, message: str) -> dict:
        """Extract structured booking information from user message"""
        
        prompt = f"""Extract booking information from this message: "{message}"

Return JSON with these fields (use null if not mentioned):
{{
  "intent": "booking|question|other",
  "appointment_type": "consultation|followup|physical|specialist|null",
  "preferred_date": "YYYY-MM-DD or null",
  "preferred_time": "HH:MM or null",
  "reason": "reason text or null",
  "patient_name": "name or null",
  "patient_email": "email or null",
  "patient_phone": "phone or null"
}}

Only return the JSON, nothing else."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=200
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except:
            return {"intent": "other"}

# llm_service = LLMService()

if __name__ == "__main__":
    llm = LLMService()
    test_message = "Hi how are you?"
    print(llm.chat(test_message))