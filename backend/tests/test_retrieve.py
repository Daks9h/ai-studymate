import os
import json
from unittest.mock import patch, MagicMock

# Set TESTING env var to avoid loading real models
os.environ["TESTING"] = "1"

from fastapi.testclient import TestClient
from fastapi import FastAPI
from app.routes.retrieve import router

app = FastAPI()
app.include_router(router)

client = TestClient(app)

@patch("app.routes.retrieve.store_embeddings")
def test_store_valid_file_id(mock_store_embeddings):
    file_id = "test-store-123"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    embeddings_dir = os.path.join(project_root, "embeddings")
    os.makedirs(embeddings_dir, exist_ok=True)
    
    embeddings_path = os.path.join(embeddings_dir, f"{file_id}_embeddings.json")
    
    dummy_data = [
        {"chunk_index": 0, "start": 0.0, "end": 19.0, "text": "This is a test chunk.", "embedding": [0.1, 0.2]}
    ]
    
    with open(embeddings_path, "w", encoding="utf-8") as f:
        json.dump(dummy_data, f)
        
    response = client.post("/store", json={"file_id": file_id})
    assert response.status_code == 200
    
    data = response.json()
    assert data["file_id"] == file_id
    assert data["status"] == "stored"
    assert data["chunk_count"] == 1
    
    mock_store_embeddings.assert_called_once()
    
    os.remove(embeddings_path)

def test_store_invalid_file_id():
    response = client.post("/store", json={"file_id": "non-existent-uuid"})
    assert response.status_code == 404

@patch("app.routes.retrieve.retrieve_chunks")
@patch("app.routes.retrieve.generate_embeddings")
def test_retrieve_valid(mock_generate_embeddings, mock_retrieve_chunks):
    def fake_generate_embeddings(chunks):
        chunks[0]["embedding"] = [0.1, 0.2]
        return chunks
    mock_generate_embeddings.side_effect = fake_generate_embeddings
    
    mock_retrieve_chunks.return_value = [
        {"text": "Test result", "start": 0.0, "end": 5.0, "chunk_index": 0, "distance": 0.5}
    ]
    
    response = client.post("/retrieve", json={"file_id": "dummy-uuid", "query": "hello"})
    assert response.status_code == 200
    
    data = response.json()
    assert data["file_id"] == "dummy-uuid"
    assert data["query"] == "hello"
    assert len(data["results"]) == 1
    assert data["results"][0]["text"] == "Test result"
