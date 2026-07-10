from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.chroma_service import retrieve_chunks
from app.services.embedding_service import generate_embeddings
from app.services.ollama_service import generate_answer

router = APIRouter()

class ChatRequest(BaseModel):
    file_id: str
    question: str

@router.post("/chat")
async def process_chat(request: ChatRequest):
    file_id = request.file_id
    question = request.question
    
    try:
        # Generate embedding for the question
        dummy_chunk = [{"text": question}]
        embedded_query_chunks = generate_embeddings(dummy_chunk)
        query_embedding = embedded_query_chunks[0]["embedding"]
        
        # Retrieve top 5 chunks
        results = retrieve_chunks(file_id, query_embedding, top_k=5)
        
        # Extract text for context
        context_chunks = [result["text"] for result in results]
        
        # Generate answer using Ollama
        answer = generate_answer(question, context_chunks)
        
        # Format sources: return chunks with timestamps (start, end)
        sources = [
            {
                "text": result["text"],
                "start": result["start"],
                "end": result["end"]
            }
            for result in results
        ]
        
        return {
            "file_id": file_id,
            "question": question,
            "answer": answer,
            "sources": sources
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
