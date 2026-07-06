from fastapi.testclient import TestClient
import os
import json
from fastapi import FastAPI
from app.routes.chunk import router

app = FastAPI()
app.include_router(router)

client = TestClient(app)

def test_chunk_valid_file_id():
    file_id = "test-chunk-123"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    transcripts_dir = os.path.join(project_root, "transcripts")
    os.makedirs(transcripts_dir, exist_ok=True)
    
    transcript_path = os.path.join(transcripts_dir, f"{file_id}.json")
    chunks_path = os.path.join(transcripts_dir, f"{file_id}_chunks.json")
    
    dummy_data = {
        "file_id": file_id,
        "status": "processed",
        "segments": [
            {"start": 0.0, "end": 1.0, "text": "Hello world"},
            {"start": 1.0, "end": 2.0, "text": "This is"},
            {"start": 2.0, "end": 3.0, "text": "a test"}
        ]
    }
    
    with open(transcript_path, "w", encoding="utf-8") as f:
        json.dump(dummy_data, f)
        
    response = client.post("/chunk", json={"file_id": file_id})
    assert response.status_code == 200
    
    data = response.json()
    assert data["file_id"] == file_id
    assert data["chunk_count"] == 1
    assert "chunks" in data
    assert len(data["chunks"]) == 1
    
    assert data["chunks"][0]["start"] == 0.0
    assert data["chunks"][0]["end"] == 3.0
    assert data["chunks"][0]["text"] == "Hello world This is a test"
    
    assert os.path.exists(chunks_path)
    
    os.remove(transcript_path)
    os.remove(chunks_path)

def test_chunk_invalid_file_id():
    response = client.post("/chunk", json={"file_id": "non-existent-uuid"})
    assert response.status_code == 404
