import json
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.ollama_service import generate_answer

router = APIRouter()

class TimelineRequest(BaseModel):
    file_id: str

@router.post("/timeline")
async def process_timeline(request: TimelineRequest):
    file_id = request.file_id
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    transcripts_dir = os.path.join(project_root, "transcripts")
    
    chunks_path = os.path.join(transcripts_dir, f"{file_id}_chunks.json")
    
    if not os.path.exists(chunks_path):
        raise HTTPException(status_code=404, detail="Chunks not found")
        
    try:
        with open(chunks_path, "r", encoding="utf-8") as f:
            chunks = json.load(f)
            
        context_chunks = []
        for c in chunks:
            text = f"[Start: {c.get('start', 0.0)}s - End: {c.get('end', 0.0)}s] {c.get('text', '')}"
            context_chunks.append(text)
            
        prompt = """You are an AI study assistant. Given these lecture 
chunks with timestamps, create a timeline of the 
main topics covered in order.
For each topic provide:
- title: short topic title
- start: start timestamp in seconds
- end: end timestamp in seconds  
- summary: one sentence summary
Return as JSON array only, no extra text."""

        timeline_str = generate_answer(prompt, context_chunks)
        print(f"Ollama raw response: {timeline_str}")
        
        # parse json array
        try:
            cleaned_str = timeline_str.strip()
            
            # Find the first '[' and last ']'
            start_idx = cleaned_str.find('[')
            end_idx = cleaned_str.rfind(']')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_str = cleaned_str[start_idx:end_idx+1]
                timeline = json.loads(json_str)
            else:
                timeline = []
        except json.JSONDecodeError:
            timeline = []
            
        return {
            "file_id": file_id,
            "timeline": timeline
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
