# Single-Page Design Document: Envint RAG Scalability & Architecture

## System Architecture Overview

The Envint RAG system follows a **three-stage pipeline**: Ingestion → Hybrid Retrieval → LLM Synthesis.

**Ingestion:** Mixed-format documents (PDF, TXT, MD) are parsed, chunked (500 chars, 50 overlap via `RecursiveCharacterTextSplitter`), embedded locally using `BAAI/bge-small-en-v1.5` (384 dims), and upserted into Pinecone Serverless. An n8n automation workflow watches the data directory for new files and triggers re-ingestion.

**Retrieval:** Queries hit a **hybrid search** layer combining Pinecone cosine similarity (semantic) with BM25 keyword matching (lexical). Results are merged via **Reciprocal Rank Fusion** (k=60, 70% vector / 30% BM25), ensuring both meaning-based and exact-term hits contribute to the final ranking.

**Synthesis:** The top-5 fused chunks flow into a **LangGraph** agent that invokes DeepSeek with a strict JSON prompt. The LLM extracts factual claims, cross-references them for contradictions, and returns structured conflict evidence with an `llm_confidence` self-assessment (0-100). A backend calibration module computes the final weighted confidence score from 4 signals.

---

## Scaling to 10,000+ Documents

### 1. Ingestion Bottleneck
**Current:** Synchronous parsing — ingesting 10K PDFs serially would take hours.

**Solution:** Distribute parsing via a task queue (**Celery + Redis** or **AWS SQS + Lambda**). The n8n workflow triggers SQS messages; stateless Lambda workers parse, chunk, and embed in parallel. Estimated throughput: ~500 docs/minute with 10 concurrent workers.

**Trade-off:** Additional infrastructure cost (~$50/month for SQS + Lambda) vs. 100x faster ingestion.

### 2. Embedding Compute
**Current:** Local CPU inference with BGE (~200ms per chunk).

**Solution at scale:** Deploy the embedding model on a GPU instance (**vLLM** or **TensorRT-LLM** on an A10G) for ~10ms/chunk. Alternatively, use hosted APIs like OpenAI `text-embedding-3-small` ($0.02/1M tokens) or Cohere Embed v3.

**Trade-off:** GPU instance ($0.50/hr) vs. API cost. At 10K docs (~50K chunks, ~2.5M tokens), API cost ≈ $0.05 total — API wins at this scale.

### 3. Retrieval Degradation
**Current:** Naive top-K vector search + BM25.

**Solution at scale:** Add a **reranker** model (e.g., `BGE-Reranker-v2-m3` or Cohere Rerank) as a second-pass filter. Retrieve top-20 via hybrid search, then rerank to top-5 with cross-encoder scoring. This maintains precision as corpus grows.

**Trade-off:** Adds ~200ms latency per query but significantly improves relevance for large corpora.

### 4. BM25 Index Scaling
**Current:** In-memory BM25 index rebuilt from Pinecone on cold start.

**Solution at scale:** Use **Elasticsearch** or **OpenSearch** for persistent BM25 indexing, or switch to **Weaviate** which has built-in BM25 + vector hybrid search.

---

## Cost Analysis

| Component | Current Cost | At 10K Docs | At 100K Docs |
|---|---|---|---|
| **Pinecone** (Serverless) | Free tier | ~$5/month | ~$30/month |
| **DeepSeek** (per query) | ~$0.002/query | Same | Same |
| **BGE Embeddings** (local) | $0 (CPU) | GPU: $0.50/hr | API: $0.50 total |
| **Infrastructure** (FastAPI) | Free (local) | EC2 t3.medium: $30/mo | ECS Fargate: $50/mo |
| **n8n** (automation) | Free (self-hosted) | Same | Same |
| **Total (monthly)** | **~$0** | **~$35/month** | **~$80/month** |

---

## Production Observability & Monitoring

### Latency Monitoring
- Instrument FastAPI with **Prometheus** metrics middleware
- Track separately: embedding time, Pinecone query time, BM25 time, LLM generation time
- Dashboard in **Grafana** with P50/P95/P99 latency panels
- Alert on: P95 latency > 5s, error rate > 1%

### RAG Quality Monitoring
- **LangSmith** or **Phoenix** for tracing every retrieval + generation step
- Track: `llm_confidence` distribution over time, conflict detection rate, hallucination flags
- **LLM-as-a-Judge**: Periodic batch evaluation where a separate LLM scores answer quality against ground truth

### Embedding Drift Detection
- Monitor cosine similarity distribution of new embeddings against corpus centroid
- If mean similarity drops below threshold → flag for model refresh
- Version embedding models with separate Pinecone indexes (e.g., `envint-rag-v1`, `envint-rag-v2`)

### Operational
- Health endpoint (`/health`) for load balancer readiness probes
- Rate limiting via `slowapi` (10 queries/min per IP)
- Structured JSON logging for all API requests

---

## Backup & Recovery Strategy

| Layer | Strategy |
|---|---|
| **Source Documents** | Versioned S3 bucket (immutable source of truth) |
| **Pinecone Index** | Automated daily backups via Pinecone Collections |
| **Application Config** | Git-versioned `.env.example` + secrets in AWS Secrets Manager |
| **Recovery SLA** | Full re-ingestion from S3 → Pinecone in ~30 minutes for 10K docs |

### Embedding Model Migration
When upgrading embedding models (e.g., BGE-small → BGE-large), create a new versioned index, re-embed all source docs from S3, validate retrieval quality on benchmark queries, then atomic swap the index reference.

---

## Security Considerations
- CORS restricted to known frontend origins in production
- API keys stored in environment variables, never committed
- Rate limiting prevents abuse
- Input sanitization on all query parameters
- No PII stored in vector metadata
