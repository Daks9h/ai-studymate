import json
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.ollama_service import generate_answer

router = APIRouter()

class QuizRequest(BaseModel):
    file_id: str
    num_questions: int = 5

@router.post("/quiz")
async def process_quiz(request: QuizRequest):
    file_id = request.file_id
    num_questions = request.num_questions
    
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
            
        prompt = f"""You are an AI study assistant. Generate {num_questions} 
multiple choice questions from this lecture content.
For each question provide:
- question: the question text
- options: list of 4 options labeled A, B, C, D
- correct_answer: the correct option letter (A/B/C/D)
- explanation: brief explanation of why it is correct
Return as JSON array only, no extra text."""

        quiz_str = generate_answer(prompt, context_chunks)
        print(f"Ollama raw response: {quiz_str}")
        
        # parse json array robustly
        try:
            cleaned_str = quiz_str.strip()
            
            start_idx = cleaned_str.find('[')
            end_idx = cleaned_str.rfind(']')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_str = cleaned_str[start_idx:end_idx+1]
                quiz = json.loads(json_str)
            else:
                quiz = []
        except json.JSONDecodeError:
            quiz = []
            
        return {
            "file_id": file_id,
            "num_questions": num_questions,
            "quiz": quiz
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
