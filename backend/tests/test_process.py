from fastapi.testclient import TestClient
from app.main import app
from pathlib import Path
import json
import pytest

client = TestClient(app)

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOADS_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"
TRANSCRIPTS_DIR = BASE_DIR / "transcripts"

def test_process_invalid_file_id():
    response = client.post("/process", json={"file_id": "invalid-uuid"})
    assert response.status_code == 404

def test_process_valid_file_id(monkeypatch):
    file_id = "test-uuid-process"
    
    # Create dummy upload file
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    dummy_file = UPLOADS_DIR / f"{file_id}.mp3"
    dummy_file.write_text("dummy audio content")
    
    # Mock transcribe function to avoid running whisper during tests
    def mock_transcribe(audio_path):
        return [{"start": 0.0, "end": 5.2, "text": "Hello world"}]
        
    import app.routes.process
    monkeypatch.setattr(app.routes.process, "transcribe", mock_transcribe)
    
    response = client.post("/process", json={"file_id": file_id})
    assert response.status_code == 200
    
    data = response.json()
    assert data["file_id"] == file_id
    assert data["status"] == "processed"
    assert len(data["segments"]) == 1
    assert data["segments"][0]["text"] == "Hello world"
    
    # Clean up
    dummy_file.unlink()
    transcript_file = TRANSCRIPTS_DIR / f"{file_id}.json"
    if transcript_file.exists():
        transcript_file.unlink()
