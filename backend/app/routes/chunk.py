import json
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.chunker_service import chunk_transcript

router = APIRouter()

class ChunkRequest(BaseModel):
    file_id: str

@router.post("/chunk")
async def process_chunk(request: ChunkRequest):
    file_id = request.file_id
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    transcripts_dir = os.path.join(project_root, "transcripts")
    
    transcript_path = os.path.join(transcripts_dir, f"{file_id}.json")
    chunks_path = os.path.join(transcripts_dir, f"{file_id}_chunks.json")
    
    if not os.path.exists(transcript_path):
        raise HTTPException(status_code=404, detail="Transcript not found")
        
    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        segments = data.get("segments", [])
        
        chunks = chunk_transcript(segments)
        
        with open(chunks_path, "w", encoding="utf-8") as f:
            json.dump(chunks, f, indent=2)
            
        return {
            "file_id": file_id,
            "chunk_count": len(chunks),
            "chunks": chunks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
