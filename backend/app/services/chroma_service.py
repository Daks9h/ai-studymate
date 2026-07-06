import os
import chromadb

# Initialize ChromaDB persistent client
# We resolve the path relative to project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
chroma_path = os.path.join(project_root, "embeddings", "chroma")

client = None
try:
    if not os.environ.get("TESTING"):
        client = chromadb.PersistentClient(path=chroma_path)
except Exception as e:
    print(f"Failed to initialize ChromaDB: {e}")

def store_embeddings(file_id, chunks_with_embeddings):
    if not client:
        raise RuntimeError("ChromaDB client is not loaded.")
        
    collection = client.get_or_create_collection(name=file_id)
    
    ids = []
    embeddings = []
    documents = []
    metadatas = []
    
    for chunk in chunks_with_embeddings:
        ids.append(str(chunk.get("chunk_index")))
        embeddings.append(chunk.get("embedding"))
        documents.append(chunk.get("text"))
        metadatas.append({
            "start": chunk.get("start"),
            "end": chunk.get("end"),
            "chunk_index": chunk.get("chunk_index")
        })
        
    if ids:
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

def retrieve_chunks(file_id, query_embedding, top_k=5):
    if not client:
        raise RuntimeError("ChromaDB client is not loaded.")
        
    try:
        collection = client.get_collection(name=file_id)
    except Exception:
        raise ValueError(f"Collection for file_id {file_id} not found.")
        
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    
    formatted_results = []
    if results and results.get("ids") and results["ids"][0]:
        for i in range(len(results["ids"][0])):
            formatted_results.append({
                "text": results["documents"][0][i],
                "start": results["metadatas"][0][i]["start"],
                "end": results["metadatas"][0][i]["end"],
                "chunk_index": results["metadatas"][0][i]["chunk_index"],
                "distance": results["distances"][0][i] if "distances" in results and results["distances"] else None
            })
            
    return formatted_results
