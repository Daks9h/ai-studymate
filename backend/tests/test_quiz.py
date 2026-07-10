import os
import json
from unittest.mock import patch

# Set TESTING env var to avoid loading real models
os.environ["TESTING"] = "1"

from fastapi.testclient import TestClient
from fastapi import FastAPI
from app.routes.quiz import router

app = FastAPI()
app.include_router(router)

client = TestClient(app)

@patch("app.routes.quiz.generate_answer")
def test_quiz_valid(mock_generate_answer):
    file_id = "test-quiz-123"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    transcripts_dir = os.path.join(project_root, "transcripts")
    os.makedirs(transcripts_dir, exist_ok=True)
    
    chunks_path = os.path.join(transcripts_dir, f"{file_id}_chunks.json")
    
    dummy_chunks = [
        {"chunk_index": 0, "start": 0.0, "end": 10.0, "text": "Topic 1 start"}
    ]
    with open(chunks_path, "w", encoding="utf-8") as f:
        json.dump(dummy_chunks, f)
        
    mock_generate_answer.return_value = '''[
        {
            "question": "What is Topic 1?",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "A",
            "explanation": "Because it is."
        }
    ]'''
    
    response = client.post("/quiz", json={"file_id": file_id, "num_questions": 1})
    assert response.status_code == 200
    
    data = response.json()
    assert data["file_id"] == file_id
    assert data["num_questions"] == 1
    assert "quiz" in data
    assert len(data["quiz"]) == 1
    assert data["quiz"][0]["question"] == "What is Topic 1?"
    
    # Verify generate_answer was called properly
    mock_generate_answer.assert_called_once()
    
    os.remove(chunks_path)

def test_quiz_invalid_file_id():
    response = client.post("/quiz", json={"file_id": "non-existent-uuid", "num_questions": 5})
    assert response.status_code == 404
    assert response.json()["detail"] == "Chunks not found"
