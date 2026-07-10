import os
import json
from unittest.mock import patch

# Set TESTING env var to avoid loading real models
os.environ["TESTING"] = "1"

from fastapi.testclient import TestClient
from fastapi import FastAPI
from app.routes.timeline import router

app = FastAPI()
app.include_router(router)

client = TestClient(app)

@patch("app.routes.timeline.generate_answer")
def test_timeline_valid(mock_generate_answer):
    file_id = "test-timeline-123"
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
            "title": "Topic 1",
            "start": 0.0,
            "end": 10.0,
            "summary": "Intro"
        }
    ]'''
    
    response = client.post("/timeline", json={"file_id": file_id})
    assert response.status_code == 200
    
    data = response.json()
    assert data["file_id"] == file_id
    assert "timeline" in data
    assert len(data["timeline"]) == 1
    assert data["timeline"][0]["title"] == "Topic 1"
    
    # Verify generate_answer was called properly
    mock_generate_answer.assert_called_once()
    
    os.remove(chunks_path)

def test_timeline_invalid_file_id():
    response = client.post("/timeline", json={"file_id": "non-existent-uuid"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Chunks not found"
