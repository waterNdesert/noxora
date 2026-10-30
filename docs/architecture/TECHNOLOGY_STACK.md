# Technology Selection & Evaluation

This document justifies the technology choices for every layer of the enterprise knowledge and AI agent platform, detailing the rationale for selecting **PostgreSQL 16+ with `pgvector` and Full-Text Search** for unified relational and hybrid retrieval.

---

## 1. Technology Selection Matrix

| Layer | Recommended Choice | Primary Alternatives | Operational Complexity | MVP & Production Fit |
| :--- | :--- | :--- | :--- | :--- |
| **Frontend Framework** | **Next.js 16 (React 19, TS)** | Vite SPA, Remix / React Router 7 | Low–Medium | Excellent for both MVP and Scale |
| **UI Components & Styles**| **Tailwind CSS + Radix UI** | Shadcn UI, Chakra UI, Material UI | Low | Highly maintainable & accessible |
| **Backend Framework** | **Python 3.13 + FastAPI** | Go (Gin), Node.js (NestJS), Rust | Low–Medium | Premier ecosystem for AI/LLM & RAG |
| **Database & Search** | **PostgreSQL 16+ (`pgvector` + FTS)**| OpenSearch 2.x, Qdrant, Milvus | **Low** | Unified relational + hybrid search |
| **Asynchronous Task Queue**| **Celery 5.x + Redis 7+ for document ingestion** | Temporal, BullMQ, ARQ | Medium | Introduced with upload/ingestion; not required for Sprint 1 |
| **Cache, Locks & Rate Limits**| **No general-purpose cache/lock/rate-limit service approved** | Redis, Dragonfly, KeyDB, Memcached | Deferred | Add only for an explicitly scoped requirement |
| **Object / Blob Storage** | **S3 API (MinIO / AWS S3 / R2)**| Local filesystem, Azure Blob | Low | Industry-standard storage API |
| **LLM Gateway** | **LiteLLM** | LangChain, LlamaIndex, Raw SDKs | Low | 100+ providers with unified schemas |
| **Embedding and reranking models** | **Provider/model unresolved; decide before embedding schema** | Local and hosted providers | TBD | Reranking remains optional pending retrieval evaluation |
| **Reverse Proxy** | **Nginx** | Traefik, Caddy, Envoy, Kong | Low–Medium | Approved same-origin browser routing and direct SSE to FastAPI |

---

## 2. In-Depth Component Justifications

### A. Database & Search: PostgreSQL 16+ with `pgvector` & Full-Text Search
- **Why It Is Appropriate**:
  - **Single Source of Truth**: Consolidating relational metadata (users, sessions, connectors) and search chunks (text, vectors, permissions) into a single PostgreSQL cluster eliminates an entire distributed database (OpenSearch).
  - **Zero Data Drift**: Document updates and deletions are committed transactionally. There is zero eventual-consistency lag between updating document metadata in Postgres and updating its search index.
  - **Hybrid Capabilities**:
    - **Keyword Retrieval**: Handled via PostgreSQL’s built-in `tsvector` and `tsquery` engine; the proposed example uses `ts_rank_cd`. This is not BM25.
    - **Vector Retrieval**: Handled via pgvector. The embedding provider, model, dimension, versioning, and final index settings must be selected before the embedding schema is implemented.
    - **Rank Fusion**: Fused using Reciprocal Rank Fusion (RRF) directly in SQL CTEs or application code.
  - **Simplified Operations**: Backup, restore, replication, and disaster recovery operate on a single database using standard tools (`pg_dump`, `WAL-G`, AWS RDS Aurora).
- **Alternatives Considered**:
  - *OpenSearch 2.x*: Powerful for multi-million chunk corpuses, but introduces significant operational overhead: requires 4–8 GB JVM heap, dedicated master/data node topology, circuit breaker tuning, and separate backup pipelines.
  - *Qdrant / Milvus / Pinecone*: Excellent vector-only engines, but require a separate keyword-search path and data synchronization.
- **Advantages**:
  - Cuts infrastructure costs and deployment complexity by > 50%.
  - Simplifies local development to a single `postgres` container.
  - Transactional consistency for document deletions and permission updates.
- **Disadvantages & Operational Boundaries**:
  - Index memory, recall, and latency depend on model dimensions, corpus, and workload and must be measured.
- **Migration Path**: The application wraps retrieval operations in `SearchProvider`. Any future provider migration requires evidence, data export/reindexing, operational planning, and security review; it is not a one-variable switch.
- **Verdict**: **Approved initial search direction. Performance and scale limits are not guarantees.**

---

### B. Frontend: Next.js 16 (App Router, React 19, TypeScript)
- **Why It Is Appropriate**: Combines Server Components for fast initial page loads with interactive Client Components for chat streaming. Built-in routing, layout nesting, and TypeScript support enable fast feature velocity.
- **Pros**: Immense community, rich ecosystem (Radix UI, Lucide), first-class streaming support.
- **Cons**: App Router caching requires disciplined configuration.
- **Verdict**: **Adopt for MVP & Production.**

---

### C. Backend: Python 3.13 + FastAPI + Pydantic v2
- **Why It Is Appropriate**: Python is the native language of the AI ecosystem (PyTorch, LiteLLM, LangChain, HuggingFace, tokenizers). FastAPI delivers asynchronous high-throughput HTTP endpoints with automatic OpenAPI validation via Pydantic v2.
- **Pros**: Native integration with AI libraries; auto-generating OpenAPI documentation; async/await support.
- **Cons**: Python GIL (Global Interpreter Lock); mitigated by running multiple Uvicorn worker processes.
- **Verdict**: **Adopt for MVP & Production.**

---

### D. Task Queue: Celery 5.x with Redis Broker
- **Why It Is Appropriate**: The approved document-ingestion pipeline runs asynchronously and needs job status, failure reporting, and retries.
- **Timing**: Introduce Celery and Redis with document upload and ingestion, currently planned for Sprint 2. They are not Sprint 1 dependencies.
- **Scope**: Begin with the ingestion workload. Add separate queues, Redis locks, caching, or rate limiting only when separately justified and scheduled.
- **Operational consideration**: Define broker persistence and recovery expectations before deploying ingestion workers.
- **Verdict**: **Approved for asynchronous ingestion, not as a generic Sprint 1 service.**

---

### E. LLM Abstraction: LiteLLM
- **Why It Is Appropriate**: Provides an identical OpenAI-compatible calling format across 100+ providers (OpenAI, Anthropic, Google Gemini, Azure, Bedrock, Groq, Ollama) with built-in prompt caching, streaming token accounting, and cost tracking.
- **Pros**: Lightweight, non-intrusive, robust cost calculation tables, active community.
- **Cons**: Occasional minor upstream mapping delays for newly announced models.
- **Verdict**: **Adopt for MVP & Production.**
