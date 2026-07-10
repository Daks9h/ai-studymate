import os
import json
from unittest.mock import patch

# Set TESTING env var to avoid loading real models
os.environ["TESTING"] = "1"

from fastapi.testclient import TestClient
from fastapi import FastAPI
from app.routes.summary import router

app = FastAPI()
app.include_router(router)

client = TestClient(app)

@patch("app.routes.summary.generate_answer")
def test_summary_valid(mock_generate_answer):
    file_id = "test-summary-123"
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
        
    mock_generate_answer.return_value = '''{
        "overview": "This is an overview.",
        "key_points": ["Point 1", "Point 2"],
        "conclusion": "This is a conclusion."
    }'''
    
    response = client.post("/summary", json={"file_id": file_id})
    assert response.status_code == 200
    
    data = response.json()
    assert data["file_id"] == file_id
    assert "summary" in data
    assert data["summary"]["overview"] == "This is an overview."
    
    # Verify generate_answer was called properly
    mock_generate_answer.assert_called_once()
    
    os.remove(chunks_path)

def test_summary_invalid_file_id():
    response = client.post("/summary", json={"file_id": "non-existent-uuid"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Chunks not found"
