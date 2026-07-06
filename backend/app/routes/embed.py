import json
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.embedding_service import generate_embeddings

router = APIRouter()

class EmbedRequest(BaseModel):
    file_id: str

@router.post("/embed")
async def process_embed(request: EmbedRequest):
    file_id = request.file_id
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    
    transcripts_dir = os.path.join(project_root, "transcripts")
    embeddings_dir = os.path.join(project_root, "embeddings")
    os.makedirs(embeddings_dir, exist_ok=True)
    
    chunks_path = os.path.join(transcripts_dir, f"{file_id}_chunks.json")
    embeddings_path = os.path.join(embeddings_dir, f"{file_id}_embeddings.json")
    
    if not os.path.exists(chunks_path):
        raise HTTPException(status_code=404, detail="Chunks not found")
        
    try:
        with open(chunks_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        chunks = data if isinstance(data, list) else data.get("chunks", [])
        
        embedded_chunks = generate_embeddings(chunks)
        
        with open(embeddings_path, "w", encoding="utf-8") as f:
            json.dump(embedded_chunks, f, indent=2)
            
        return {
            "file_id": file_id,
            "embedding_count": len(embedded_chunks),
            "status": "embedded"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
