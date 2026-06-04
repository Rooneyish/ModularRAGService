from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.schemas import ChatQueryRequest, ChatQueryResponse
from app.services.vector_db import VectorDBService
from app.services.llm_service import LLMService
from app.services.redis_memory import RedisMemoryService
from app.models.db_models import get_db

router = APIRouter(prefix="/api/v1", tags=["rag"])
vector_service = VectorDBService()
llm_service = LLMService()
memory_service = RedisMemoryService()

@router.post("/chat", response_model=ChatQueryResponse)
async def chat_endpoint(payload: ChatQueryRequest, db: Session = Depends(get_db)):
    try: 
        history = memory_service.get_history(payload.session_id)
        context_chunks = vector_service.query_similarity(payload.query, limit=4)

        reply = llm_service.execute_chat_flow(context_chunks, history, payload.query, db)
        memory_service.append_message(payload.session_id, "user", payload.query)
        memory_service.append_message(payload.session_id, "assistant", reply)

        return ChatQueryResponse(response=reply, retrieved_context=context_chunks)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat query: {e}")