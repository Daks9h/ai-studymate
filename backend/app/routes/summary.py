import json
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.ollama_service import generate_answer

router = APIRouter()

class SummaryRequest(BaseModel):
    file_id: str

@router.post("/summary")
async def process_summary(request: SummaryRequest):
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
            text = c.get('text', '')
            context_chunks.append(text)
            
        prompt = """You are an AI study assistant. Given these lecture 
chunks, provide a comprehensive summary with:
- overview: 2-3 sentence overall summary
- key_points: list of 5 most important points
- conclusion: one sentence conclusion
Return as JSON only, no extra text."""

        summary_str = generate_answer(prompt, context_chunks)
        print(f"Ollama raw response: {summary_str}")
        
        # parse json object
        try:
            cleaned_str = summary_str.strip()
            
            # Find the first '{' and last '}'
            start_idx = cleaned_str.find('{')
            end_idx = cleaned_str.rfind('}')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_str = cleaned_str[start_idx:end_idx+1]
                summary = json.loads(json_str)
            else:
                summary = {}
        except json.JSONDecodeError:
            summary = {}
            
        return {
            "file_id": file_id,
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
