from sentence_transformers import SentenceTransformer
import os

model = None
try:
    if not os.environ.get("TESTING"):
        model = SentenceTransformer('BAAI/bge-small-en-v1.5')
except Exception as e:
    print(f"Failed to load embedding model: {e}")

def generate_embeddings(chunks):
    if not model:
        raise RuntimeError("Embedding model is not loaded.")
        
    texts = [chunk.get("text", "") for chunk in chunks]
    
    embeddings = model.encode(texts)
    
    for i, chunk in enumerate(chunks):
        chunk["embedding"] = embeddings[i].tolist()
        
    return chunks
