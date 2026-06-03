from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    LLM_API_KEY: str = "local-qwen"
    LLM_BASE_URL: str = "http://localhost:11434/v1"
    LLM_MODEL_NAME: str = "Qwen2.5-7B-Instruct"  
    
    EMBEDDING_BASE_URL: str = "http://localhost:11434/v1"
    EMBEDDING_MODEL_NAME: str = "nomic-embed-text-v1"  

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    QDRANT_URL: str = "http://localhost:6333"
    DATABASE_URL: str = "sqlite:///./palmmind_metadata.db"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()