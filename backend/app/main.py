from fastapi import FastAPI
from app.routes import upload, process, chunk, embed, retrieve, chat, timeline, summary, concepts, quiz

app = FastAPI()

app.include_router(upload.router)
app.include_router(process.router)
app.include_router(chunk.router)
app.include_router(embed.router)
app.include_router(retrieve.router)
app.include_router(chat.router)
app.include_router(timeline.router)
app.include_router(summary.router)
app.include_router(concepts.router)
app.include_router(quiz.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
