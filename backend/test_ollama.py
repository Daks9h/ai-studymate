import asyncio
import json
import os
from app.services.ollama_service import generate_answer

def run_test():
    file_id = "73fde442-9732-461b-9e92-9cfb737110ba"
    transcripts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "transcripts")
    chunks_path = os.path.join(transcripts_dir, f"{file_id}_chunks.json")
    
    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)
        
    context_chunks = []
    for c in chunks:
        text = f"[Start: {c.get('start', 0.0)}s - End: {c.get('end', 0.0)}s] {c.get('text', '')}"
        context_chunks.append(text)
        
    prompt = """You are an AI study assistant. Given these lecture 
chunks with timestamps, create a timeline of the 
main topics covered in order.
For each topic provide:
- title: short topic title
- start: start timestamp in seconds
- end: end timestamp in seconds  
- summary: one sentence summary
Return as JSON array only, no extra text."""

    timeline_str = generate_answer(prompt, context_chunks)
    print("Ollama raw response:")
    print(timeline_str)

if __name__ == "__main__":
    run_test()
