import uuid
import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter()

ALLOWED_EXTENSIONS = {".mp4", ".mkv", ".webm", ".mp3", ".wav", ".pdf", ".txt"}
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
UPLOADS_DIR = BASE_DIR / "uploads"

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    file_id = str(uuid.uuid4())
    filename = file.filename
    new_filename = f"{file_id}{ext}"
    
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    file_path = UPLOADS_DIR / new_filename
    
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {
        "file_id": file_id,
        "filename": filename,
        "status": "uploaded"
    }
