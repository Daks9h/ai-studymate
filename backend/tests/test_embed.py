import os
import json
from unittest.mock import patch

# Set TESTING env var before importing app to prevent loading the real model
os.environ["TESTING"] = "1"

from fastapi.testclient import TestClient
from fastapi import FastAPI
from app.routes.embed import router

app = FastAPI()
app.include_router(router)

client = TestClient(app)

@patch("app.routes.embed.generate_embeddings")
def test_embed_valid_file_id(mock_generate_embeddings):
    def fake_generate_embeddings(chunks):
        for chunk in chunks:
            chunk["embedding"] = [0.1, 0.2, 0.3]
        return chunks
    mock_generate_embeddings.side_effect = fake_generate_embeddings
    
    file_id = "test-embed-123"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    transcripts_dir = os.path.join(project_root, "transcripts")
    embeddings_dir = os.path.join(project_root, "embeddings")
    os.makedirs(transcripts_dir, exist_ok=True)
    os.makedirs(embeddings_dir, exist_ok=True)
    
    chunks_path = os.path.join(transcripts_dir, f"{file_id}_chunks.json")
    embeddings_path = os.path.join(embeddings_dir, f"{file_id}_embeddings.json")
    
    dummy_data = {
        "file_id": file_id,
        "chunk_count": 1,
        "chunks": [
            {"chunk_index": 0, "start": 0.0, "end": 19.0, "text": "This is a test chunk."}
        ]
    }
    
    with open(chunks_path, "w", encoding="utf-8") as f:
        json.dump(dummy_data, f)
        
    response = client.post("/embed", json={"file_id": file_id})
    assert response.status_code == 200
    
    data = response.json()
    assert data["file_id"] == file_id
    assert data["embedding_count"] == 1
    assert data["status"] == "embedded"
    
    assert os.path.exists(embeddings_path)
    
    with open(embeddings_path, "r", encoding="utf-8") as f:
        saved_data = json.load(f)
    assert len(saved_data) == 1
    assert "embedding" in saved_data[0]
    
    os.remove(chunks_path)
    os.remove(embeddings_path)

def test_embed_invalid_file_id():
    response = client.post("/embed", json={"file_id": "non-existent-uuid"})
    assert response.status_code == 404
