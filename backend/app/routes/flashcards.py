import json
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.ollama_service import generate_answer

router = APIRouter()

class FlashcardsRequest(BaseModel):
    file_id: str
    num_cards: int = 10

@router.post("/flashcards")
async def process_flashcards(request: FlashcardsRequest):
    file_id = request.file_id
    num_cards = request.num_cards
    
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
            
        prompt = f"""You are an AI study assistant. Generate {num_cards} 
flashcards from this lecture content.
For each flashcard provide:
- front: a question or concept to remember
- back: the answer or explanation
- hint: a one word memory hint
Return as JSON array only, no extra text."""

        flashcards_str = generate_answer(prompt, context_chunks)
        print(f"Ollama raw response: {flashcards_str}")
        
        # parse json array robustly
        try:
            cleaned_str = flashcards_str.strip()
            
            start_idx = cleaned_str.find('[')
            end_idx = cleaned_str.rfind(']')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_str = cleaned_str[start_idx:end_idx+1]
                flashcards = json.loads(json_str)
            else:
                flashcards = []
        except json.JSONDecodeError:
            flashcards = []
            
        return {
            "file_id": file_id,
            "num_cards": num_cards,
            "flashcards": flashcards
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
