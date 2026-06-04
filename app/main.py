import uvicorn
import httpx
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api import ingestion, rag
from app.models.db_models import init_db
from app.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    
    print(f"⚙️ Preloading {settings.LLM_MODEL_NAME} into memory...")
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                "http://localhost:11434/api/generate",
                json={"model": settings.LLM_MODEL_NAME, "keep_alive": -1},
                timeout=60.0
            )
        print(f"{settings.LLM_MODEL_NAME} successfully cached in memory!")
    except Exception as e:
        print(f"Could not preload model on startup: {e}")
        
    yield

app = FastAPI(
    title="RAG Engine",
    description="Clean architectural implementation built completely on native SDKs.",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(ingestion.router)
app.include_router(rag.router)

@app.get("/health", tags=["Utilities"])
async def health():
    return {"status": "healthy", "engine": "Llama3.1-Local"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)