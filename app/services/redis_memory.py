import json
from typing import List, Dict
import redis
from app.config import settings

class RedisMemoryService:
    def __init__(self) -> None:
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True
        )
        self.expiry_seconds = 3600  

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        key = f"chat_session:{session_id}"
        raw_data = self.client.get(key)
        if not raw_data:
            return []
        return json.loads(raw_data)

    def append_message(self, session_id: str, role: str, content: str) -> None:
        key = f"chat_session:{session_id}"
        history = self.get_history(session_id)
        history.append({"role": role, "content": content})
        
        if len(history) > 16:
            history = history[-16:]
            
        self.client.setex(key, self.expiry_seconds, json.dumps(history))