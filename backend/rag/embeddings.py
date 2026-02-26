"""
Embeddings module — uses Google Gemini API (text-embedding-004).

This replaces heavy local sentence-transformers/PyTorch (~450MB RAM)
with a lightweight API call (~0MB), critical for Render free-tier deployment.

Gemini text-embedding-004 is free-tier (up to 1500 requests/min) and
output_dimensionality=384 matches our existing Pinecone index dimensions.
"""
import os
import google.generativeai as genai

# Configure Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))

EMBEDDING_MODEL = "models/text-embedding-004"
DIMENSIONS = 384  # Match existing Pinecone index (was BGE-small 384d)


def get_embedding(text: str) -> list[float]:
    """Embed a single text string."""
    result = genai.embed_content(
        model=EMBEDDING_MODEL,
        content=text,
        output_dimensionality=DIMENSIONS,
    )
    return result["embedding"]


def get_embeddings(texts: list[str]) -> list[list[float]]:
    """Embed a batch of text strings."""
    results = []
    # Gemini batch limit is 100 texts per call
    batch_size = 100
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        result = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=batch,
            output_dimensionality=DIMENSIONS,
        )
        results.extend(result["embedding"])
    return results
