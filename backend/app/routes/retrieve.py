import json
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.chroma_service import store_embeddings, retrieve_chunks
from app.services.embedding_service import generate_embeddings

router = APIRouter()

class StoreRequest(BaseModel):
    file_id: str

class RetrieveRequest(BaseModel):
    file_id: str
    query: str

@router.post("/store")
async def process_store(request: StoreRequest):
    file_id = request.file_id
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    embeddings_dir = os.path.join(project_root, "embeddings")
    
    embeddings_path = os.path.join(embeddings_dir, f"{file_id}_embeddings.json")
    
    if not os.path.exists(embeddings_path):
        raise HTTPException(status_code=404, detail="Embeddings not found")
        
    try:
        with open(embeddings_path, "r", encoding="utf-8") as f:
            chunks = json.load(f)
            
        store_embeddings(file_id, chunks)
            
        return {
            "file_id": file_id,
            "status": "stored",
            "chunk_count": len(chunks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/retrieve")
async def process_retrieve(request: RetrieveRequest):
    file_id = request.file_id
    query = request.query
    
    try:
        dummy_chunk = [{"text": query}]
        embedded_query_chunks = generate_embeddings(dummy_chunk)
        query_embedding = embedded_query_chunks[0]["embedding"]
        
        results = retrieve_chunks(file_id, query_embedding, top_k=5)
        
        return {
            "file_id": file_id,
            "query": query,
            "results": results
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
