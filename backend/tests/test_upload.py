import io
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_upload_valid_file():
    file_content = b"hello world"
    files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
    response = client.post("/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "file_id" in data
    assert data["filename"] == "test.txt"
    assert data["status"] == "uploaded"

def test_upload_invalid_file():
    file_content = b"hello world"
    files = {"file": ("test.exe", io.BytesIO(file_content), "application/x-msdownload")}
    response = client.post("/upload", files=files)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid file type"
