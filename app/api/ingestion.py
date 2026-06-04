import uuid
import io
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from pypdf import PdfReader
from app.services.vector_db import VectorDBService
from app.services.chunking import ChunkingEngine
from app.models.db_models import DocumentMetadata, get_db
import datetime

router = APIRouter(prefix="/api/v1", tags=["ingestion"])
vector_service = VectorDBService()

@router.post("/ingest")
async def ingest_document(
    file: UploadFile = File(...),
    chunking_strategy: str = Form(..., description = "Either 'fixed' or 'recursive'"),
    db: Session = Depends(get_db)
): 
    if not file.filename.endswith((".pdf", ".txt")):
        raise HTTPException(status_code=400, detail="Only PDF and TXT files are supported.")

    content = await file.read()
    extracted_text = ""

    if file.filename.endswith(".pdf"):
        try:
            reader = PdfReader(io.BytesIO(content))
            for page in reader.pages:
                text = page.extract_text() 
                if text:
                    extracted_text += text + "\n"
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing PDF: {e}")
    else:
        extracted_text = content.decode("utf-8", errors="ignore")

    if not extracted_text.strip():
        raise HTTPException(status_code=400, detail="No text could be extracted from the document.")
    
    if chunking_strategy == "fixed":
        chunks = ChunkingEngine().chunk_fixed_size(extracted_text)
    elif chunking_strategy == "recursive":
        chunks = ChunkingEngine().chunk_recursive_paragraph(extracted_text)
    else:
        raise HTTPException(status_code=400, detail="Invalid chunking strategy. Use 'fixed' or 'recursive'.")

    doc_id = str(uuid.uuid4())
    vector_service.store_documents(doc_id, chunks)

    db_record = DocumentMetadata(id=doc_id, filename=file.filename, chunking_strategy=chunking_strategy, created_at=datetime.datetime.utcnow().isoformat())
    db.add(db_record)
    db.commit()

    return{
        "status": "success",
        "document_id": doc_id,
        "filename": file.filename,
        "chunking_strategy": chunking_strategy,
        "num_chunks": len(chunks)
    }