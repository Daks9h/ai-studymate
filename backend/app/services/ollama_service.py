import httpx

def generate_answer(question: str, context_chunks: list[str]) -> str:
    chunks_text = "\n\n".join(context_chunks)
    
    prompt = f"""You are an AI study assistant. Answer the question 
based only on the provided context from a lecture.
If the answer is not in the context, say 
'I could not find this in the lecture.'

Context:
{chunks_text}

Question: {question}
Answer:"""

    response = httpx.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        },
        timeout=60.0
    )
    
    if response.status_code == 200:
        return response.json().get("response", "")
    else:
        raise Exception(f"Ollama API error: {response.text}")
