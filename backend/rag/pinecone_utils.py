import os
from pinecone import Pinecone

def get_pinecone_index():
    api_key = os.environ.get("PINECONE_API_KEY")
    if not api_key:
        raise ValueError("PINECONE_API_KEY is not set")
    
    pc = Pinecone(api_key=api_key)
    index_name = os.environ.get("PINECONE_INDEX_NAME", "envint-rag")
    
    return pc.Index(index_name)

def search_pinecone(query_vector: list[float], top_k: int = 5):
    index = get_pinecone_index()
    res = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True
    )
    
    matches = []
    for match in res.get("matches", []):
        matches.append({
            "id": match["id"],
            "score": match["score"],
            "metadata": match["metadata"]
        })
    return matches
