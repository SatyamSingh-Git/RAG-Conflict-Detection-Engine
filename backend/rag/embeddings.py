"""
Embeddings module — uses Google Gemini API (gemini-embedding-001).

This replaces heavy local sentence-transformers/PyTorch (~450MB RAM)
with a lightweight API call (~0MB), critical for Render free-tier deployment.

Uses Matryoshka Representation Learning (MRL) with output_dimensionality=384
to match our existing Pinecone index dimensions.
"""
import os
from google import genai

EMBEDDING_MODEL = "gemini-embedding-001"
DIMENSIONS = 384  # Match existing Pinecone index

_client = None

def _get_client():
    """Lazy client init — runs after load_dotenv() has been called."""
    global _client
    if _client is None:
        api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY", "")
        _client = genai.Client(api_key=api_key)
    return _client


def get_embedding(text: str) -> list[float]:
    """Embed a single text string."""
    client = _get_client()
    result = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
        config={"output_dimensionality": DIMENSIONS},
    )
    return result.embeddings[0].values


def get_embeddings(texts: list[str]) -> list[list[float]]:
    """Embed a batch of text strings."""
    client = _get_client()
    results = []
    # Gemini batch limit is 100 texts per call
    batch_size = 100
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        result = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=batch,
            config={"output_dimensionality": DIMENSIONS},
        )
        results.extend([e.values for e in result.embeddings])
    return results
