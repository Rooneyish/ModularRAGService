import json
from typing import List, Dict
from openai import OpenAI
from sqlalchemy.orm import Session
from app.config import settings
from app.models.db_models import InterviewBooking

class LLMService:
    def __init__(self) -> None:
        self.client = OpenAI(
            base_url=settings.LLM_BASE_URL,
            api_key=settings.LLM_API_KEY
        )

    def execute_chat_flow(self, context_chunks: List[str], chat_history: List[Dict[str, str]], user_query: str, db_session: Session) -> str:
        context_string = "\n\n".join(context_chunks)
        
        system_instruction = (
            "You are an advanced conversational AI assistant utilizing a local Qwen model core.\n"
            "Formulate answers utilizing the provided context material and conversation logs.\n"
            "If the information cannot be found in the context, politely inform the user you don't know.\n\n"
            "--- MANDATORY INTERVIEW BOOKING RULE ---\n"
            "If the user explicitly states they want to book, schedule, or reserve an interview, you MUST extract: "
            "name, email, date, and time. You MUST provide a polite conversational response AND append a clean JSON "
            "data payload enclosed precisely in structural `<BOOKING>` tags at the very end of your response.\n"
            "Example format:\n"
            "<BOOKING>{\"name\": \"John Doe\", \"email\": \"john@example.com\", \"date\": \"2026-06-15\", \"time\": \"14:30\"}</BOOKING>\n\n"
            f"--- REFERENCED CONTEXT MATERIAL ---\n{context_string}"
        )

        messages = [{"role": "system", "content": system_instruction}]
        for turn in chat_history:
            messages.append({"role": turn["role"], "content": turn["content"]})
        messages.append({"role": "user", "content": user_query})

        response = self.client.chat.completions.create(
            model=settings.LLM_MODEL_NAME,
            messages=messages,
            temperature=0.3
        )
        
        raw_output = response.choices[0].message.content
        return self._intercept_and_commit_bookings(raw_output, db_session)

    def _intercept_and_commit_bookings(self, text: str, db_session: Session) -> str:
        if "<BOOKING>" in text and "</BOOKING>" in text:
            try:
                start_idx = text.find("<BOOKING>") + len("<BOOKING>")
                end_idx = text.find("</BOOKING>")
                json_str = text[start_idx:end_idx].strip()
                data = json.loads(json_str)
                
                booking = InterviewBooking(
                    name=data.get("name", "Unknown"),
                    email=data.get("email", "Unknown"),
                    booking_date=data.get("date", "Unknown"),
                    booking_time=data.get("time", "Unknown")
                )
                db_session.add(booking)
                db_session.commit()
                
                clean_text = text.replace(text[text.find("<BOOKING>"):end_idx + len("</BOOKING>")], "")
                return clean_text.strip() + "\n\n*[System: Your interview has been successfully logged in our records!]*"
            except Exception as e:
                return text + f"\n\n*[System Alert: Failed parsing booking metadata parameters: {str(e)}]*"
        return text