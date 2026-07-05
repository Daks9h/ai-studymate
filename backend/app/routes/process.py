from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import json

from app.services.ffmpeg_service import extract_audio
from app.services.whisper_service import transcribe

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
UPLOADS_DIR = BASE_DIR / "uploads"
TRANSCRIPTS_DIR = BASE_DIR / "transcripts"

class ProcessRequest(BaseModel):
    file_id: str

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".webm"}
AUDIO_EXTENSIONS = {".mp3", ".wav"}

@router.post("/process")
async def process_file(request: ProcessRequest):
    file_id = request.file_id
    
    print(f"BASE_DIR: {BASE_DIR}")
    print(f"UPLOADS_DIR: {UPLOADS_DIR}")
    print(f"Looking for file_id: {file_id}")
    
    # Find the file in uploads directory
    target_file = None
    for file_path in UPLOADS_DIR.glob(f"{file_id}.*"):
        target_file = file_path
        break
        
    if not target_file:
        raise HTTPException(status_code=404, detail="File not found")
        
    ext = target_file.suffix.lower()
    
    try:
        if ext in VIDEO_EXTENSIONS:
            audio_path = extract_audio(target_file)
            segments = transcribe(audio_path)
        elif ext in AUDIO_EXTENSIONS:
            segments = transcribe(target_file)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format for processing")
            
        # Save transcript as JSON
        TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
        transcript_path = TRANSCRIPTS_DIR / f"{file_id}.json"
        
        transcript_data = {
            "file_id": file_id,
            "status": "processed",
            "segments": segments
        }
        
        with open(transcript_path, "w", encoding="utf-8") as f:
            json.dump(transcript_data, f, ensure_ascii=False, indent=2)
            
        return transcript_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
