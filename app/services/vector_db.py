import uuid
from typing import List
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from app.config import settings

class VectorDBService:
    def __init__(self):
        self.qdrant_client = QdrantClient(url = settings.QDRANT_URL, check_compatibility=False)
        self.embedding_client = OpenAI(base_url=settings.EMBEDDING_BASE_URL, api_key=settings.LLM_API_KEY)
        self.collection_name = "document_KB"
        self._ensure_collection_exists()
    
    def _ensure_collection_exists(self)-> None:
        try: 
            collections = self.qdrant_client.get_collections().collections
            exists = any(col.name == self.collection_name for col in collections)
            if not exists:
                self.qdrant_client.recreate_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=768, distance=Distance.COSINE)
                )
        except Exception as e:
            print(f"Error ensuring collection exists: {e}")
        
    def _get_embedding(self, text: str, prefix: str = "") -> List[float]:
        formatted_input = f"{prefix} {text}"

        try:
            response = self.embedding_client.embeddings.create(
                input=formatted_input,
                model=settings.EMBEDDING_MODEL_NAME
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error getting embedding: {e}")
            return []
    
    def store_documents(self, doc_id: str, chunks: List[str]) -> None:
        points: List[PointStruct] = []
        for chunk in chunks:
            embedding = self._get_embedding(chunk, prefix=f"search_document: ")
            point_id = str(uuid.uuid4())
            points.append(PointStruct(id=point_id, vector=embedding, payload={"doc_id": doc_id, "text": chunk}))
        
        self.qdrant_client.upsert(collection_name=self.collection_name, points=points)

    def query_similarity(self, query: str, limit: int = 4) -> List[str]:
            query_vector = self._get_embedding(query, prefix="search_query: ")
            
            search_results = self.qdrant_client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=limit
            )
            
            return [
                point.payload["text"] 
                for point in search_results.points 
                if point.payload and "text" in point.payload
            ]