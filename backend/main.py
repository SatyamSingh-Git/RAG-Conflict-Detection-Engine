from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel
from typing import List, Optional
from rag.graph import get_answer
from rag.pinecone_utils import get_pinecone_index
from rag.embeddings import get_embeddings
import os, json, shutil
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
import PyPDF2

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Envint RAG API", description="Hospital Performance RAG with Conflict Detection")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

class ChunkMeta(BaseModel):
    id: str
    score: float
    content: str
    metadata: dict

class ExplainRequest(BaseModel):
    query: str
    chunks: List[ChunkMeta]

@app.post("/api/query")
@limiter.limit("10/minute")
async def process_query(request: Request, body: QueryRequest):
    result = await get_answer(body.query)
    return result

@app.post("/api/explain-chunks")
@limiter.limit("15/minute")
async def explain_chunks(request: Request, body: ExplainRequest):
    """Explain why the top chunks matter most for the given query."""
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        return {"explanations": []}

    chunks_text = ""
    for i, c in enumerate(body.chunks[:3]):
        meta_safe = {k: v for k, v in c.metadata.items() if k != "text"}
        chunks_text += f"--- Chunk {i+1} ---\nID: {c.id}\nSimilarity: {c.score:.3f}\nMetadata: {json.dumps(meta_safe)}\nFull Content: {c.content}\n\n"

    prompt = f"""You are analyzing hospital performance documents for conflict detection.

User Query: "{body.query}"

Here are the top {len(body.chunks[:3])} retrieved document chunks:

{chunks_text}

For EACH chunk, write a concise 2-3 sentence explanation of:
1. Why this chunk is relevant to the user's query
2. What specific claims or data points it contains
3. Whether it supports or contradicts other chunks

Return ONLY a JSON array of objects with this format:
[
  {{"chunk_id": "...", "title": "short descriptive title", "relevance": "why this chunk matters most", "key_claims": ["claim 1", "claim 2"], "stance": "supports/contradicts/neutral"}}
]"""

    llm = ChatOpenAI(
        model="deepseek-chat",
        api_key=api_key,
        base_url="https://api.deepseek.com",
        max_tokens=800,
        temperature=0.3
    )

    try:
        response = llm.invoke(prompt)
        content = response.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].strip()
        explanations = json.loads(content)
    except Exception:
        explanations = []

    return {"explanations": explanations}


# ─── Document Management Endpoints ───────────────────────────────────────────

def _parse_file(file_path: str, filename: str):
    """Parse a single file and return chunks with metadata."""
    ext = filename.rsplit(".", 1)[-1].lower()
    content = ""
    metadata = {"filename": filename, "source": file_path}

    if ext == "pdf":
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    content += t + "\n"
    elif ext in ["txt", "md"]:
        with open(file_path, "r", encoding="utf-8") as f:
            raw = f.read()
        if raw.startswith("Metadata: "):
            lines = raw.split("\n")
            try:
                metadata.update(json.loads(lines[0].replace("Metadata: ", "")))
                content = "\n".join(lines[1:]).strip()
            except Exception:
                content = raw
        else:
            content = raw
    else:
        return []

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.create_documents([content], metadatas=[metadata])
    return chunks


def _ingest_chunks(chunks, filename_prefix="doc"):
    """Embed and upsert chunks to Pinecone."""
    if not chunks:
        return 0

    texts = [c.page_content for c in chunks]
    vectors = get_embeddings(texts)
    index = get_pinecone_index()

    records = []
    for i, (chunk, vec) in enumerate(zip(chunks, vectors)):
        meta = chunk.metadata.copy()
        meta["text"] = chunk.page_content
        records.append({
            "id": f"{meta.get('filename', filename_prefix)}_chunk_{i}",
            "values": vec,
            "metadata": meta,
        })

    # Batch upsert
    batch_size = 100
    for i in range(0, len(records), batch_size):
        index.upsert(vectors=records[i:i + batch_size])

    return len(records)


@app.post("/api/upload-file")
async def upload_file(file: UploadFile = File(...)):
    """Upload a document, save to data/, parse, chunk, embed, and upsert to Pinecone."""
    try:
        # Save file
        os.makedirs(DATA_DIR, exist_ok=True)
        file_path = os.path.join(DATA_DIR, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Parse and ingest
        chunks = _parse_file(file_path, file.filename)
        count = _ingest_chunks(chunks, file.filename)

        # Invalidate BM25 cache so it rebuilds on next query
        try:
            from rag.hybrid_search import _build_bm25_index
            import rag.hybrid_search as hs
            hs._bm25_index = None
        except Exception:
            pass

        return {
            "status": "success",
            "filename": file.filename,
            "chunks_created": count,
            "message": f"Ingested {file.filename} → {count} chunks upserted to Pinecone"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/api/recreate-embeddings")
async def recreate_embeddings():
    """Delete all vectors from Pinecone, then re-ingest every file in data/."""
    try:
        # 1. Clear the index
        index = get_pinecone_index()
        index.delete(delete_all=True)

        # 2. Re-ingest all files from data/
        total_chunks = 0
        files_processed = 0

        if os.path.exists(DATA_DIR):
            for fname in sorted(os.listdir(DATA_DIR)):
                fpath = os.path.join(DATA_DIR, fname)
                if os.path.isfile(fpath):
                    chunks = _parse_file(fpath, fname)
                    count = _ingest_chunks(chunks, fname)
                    total_chunks += count
                    files_processed += 1

        # Invalidate BM25 cache
        try:
            import rag.hybrid_search as hs
            hs._bm25_index = None
        except Exception:
            pass

        return {
            "status": "success",
            "files_processed": files_processed,
            "total_chunks": total_chunks,
            "message": f"Cleared index and re-ingested {files_processed} files → {total_chunks} chunks"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.delete("/api/delete-embeddings")
async def delete_embeddings():
    """Delete all vectors from the Pinecone index."""
    try:
        index = get_pinecone_index()
        index.delete(delete_all=True)

        # Invalidate BM25 cache
        try:
            import rag.hybrid_search as hs
            hs._bm25_index = None
        except Exception:
            pass

        return {
            "status": "success",
            "message": "All embeddings deleted from Pinecone index"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/health")
async def health():
    return {"status": "ok"}

