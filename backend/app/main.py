from fastapi import FastAPI
from app.routes import upload, process, chunk, embed

app = FastAPI()

app.include_router(upload.router)
app.include_router(process.router)
app.include_router(chunk.router)
app.include_router(embed.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
