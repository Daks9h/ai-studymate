import json
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.ollama_service import generate_answer

router = APIRouter()

class ConceptsRequest(BaseModel):
    file_id: str

@router.post("/concepts")
async def process_concepts(request: ConceptsRequest):
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
            
        prompt = """You are an AI study assistant. Extract the key 
concepts from this lecture.
For each concept provide:
- term: the concept name
- definition: clear one sentence definition
- importance: why this concept matters in one sentence
Return as JSON array only, no extra text.
Extract at least 3 and at most 8 concepts."""

        concepts_str = generate_answer(prompt, context_chunks)
        print(f"Ollama raw response: {concepts_str}")
        
        # parse json array robustly
        try:
            cleaned_str = concepts_str.strip()
            
            start_idx = cleaned_str.find('[')
            end_idx = cleaned_str.rfind(']')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_str = cleaned_str[start_idx:end_idx+1]
                concepts = json.loads(json_str)
            else:
                concepts = []
        except json.JSONDecodeError:
            concepts = []
            
        return {
            "file_id": file_id,
            "concepts": concepts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
