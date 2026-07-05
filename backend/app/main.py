from fastapi import FastAPI
from app.routes import upload, process

app = FastAPI()

app.include_router(upload.router)
app.include_router(process.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
