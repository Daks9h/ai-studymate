import os
from unittest.mock import patch

# Set TESTING env var to avoid loading real models
os.environ["TESTING"] = "1"

from fastapi.testclient import TestClient
from fastapi import FastAPI
from app.routes.chat import router

app = FastAPI()
app.include_router(router)

client = TestClient(app)

@patch("app.routes.chat.generate_answer")
@patch("app.routes.chat.retrieve_chunks")
@patch("app.routes.chat.generate_embeddings")
def test_chat_valid(mock_generate_embeddings, mock_retrieve_chunks, mock_generate_answer):
    def fake_generate_embeddings(chunks):
        chunks[0]["embedding"] = [0.1, 0.2]
        return chunks
    mock_generate_embeddings.side_effect = fake_generate_embeddings
    
    mock_retrieve_chunks.return_value = [
        {"text": "Test chunk 1", "start": 0.0, "end": 5.0, "chunk_index": 0, "distance": 0.5},
        {"text": "Test chunk 2", "start": 5.0, "end": 10.0, "chunk_index": 1, "distance": 0.6}
    ]
    
    mock_generate_answer.return_value = "This is a test answer based on the context."
    
    response = client.post("/chat", json={"file_id": "dummy-uuid", "question": "test question?"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["file_id"] == "dummy-uuid"
    assert data["question"] == "test question?"
    assert data["answer"] == "This is a test answer based on the context."
    assert len(data["sources"]) == 2
    assert data["sources"][0]["text"] == "Test chunk 1"
    
    mock_generate_answer.assert_called_once_with("test question?", ["Test chunk 1", "Test chunk 2"])

@patch("app.routes.chat.generate_embeddings")
@patch("app.routes.chat.retrieve_chunks")
def test_chat_invalid_file_id(mock_retrieve_chunks, mock_generate_embeddings):
    def fake_generate_embeddings(chunks):
        chunks[0]["embedding"] = [0.1, 0.2]
        return chunks
    mock_generate_embeddings.side_effect = fake_generate_embeddings
    
    mock_retrieve_chunks.side_effect = ValueError("Collection for file_id non-existent-uuid not found.")
    
    response = client.post("/chat", json={"file_id": "non-existent-uuid", "question": "test question?"})
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Collection for file_id non-existent-uuid not found."
