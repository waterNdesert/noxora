# Architecture Decision Records (ADRs)

This document records the foundational architectural decisions, rationale, alternatives considered, and trade-offs for the enterprise knowledge intelligence platform, featuring a **unified PostgreSQL 16+ hybrid search engine with `pgvector`**.

---

## ADR-001: Choice of PostgreSQL 16+ with `pgvector` & FTS for Unified Hybrid Retrieval

### Status: Accepted (Supersedes OpenSearch-mandatory design)
### Context:
Enterprise workplace search requires retrieving documents through both semantic intent (conceptual synonyms) and exact keyword matches (acronyms, code identifiers, employee names, exact error codes), while enforcing strict tenant and user access control lists (ACLs). Requiring OpenSearch for initial deployment adds severe operational overhead: a dedicated Java Virtual Machine (JVM) cluster (4–8 GB heap), circuit breaker tuning, separate backups, and dual-database eventual consistency lag.

### Decision:
**Approved initial search architecture:** PostgreSQL 16+ with `pgvector` and PostgreSQL Full-Text Search (FTS), accessed through the `SearchProvider` contract. OpenSearch and Qdrant are possible future providers only; they are not part of the approved implementation.

1. Deploy **PostgreSQL 16+ with the `pgvector` extension and Full-Text Search (FTS)** as the unified data store for both relational metadata and hybrid search.
2. Abstract all search, indexing, and deletion operations behind an abstract **`SearchProvider`** interface, with **`PgVectorSearchProvider`** as the default implementation.
3. Use HNSW indexing on vector embeddings (`vector_cosine_ops`) and GIN indexing on generated `tsvector` columns, combining rankings via **Reciprocal Rank Fusion (RRF)** in a single SQL query.

### Alternatives Considered:
1. *Mandatory OpenSearch 2.x*: Powerful for 10M+ chunks, but excessive complexity for initial development, MVP, and deployments under 2M chunks.
2. *Pure Vector Databases (Pinecone, Qdrant, Milvus)*: Excellent vector search, but lack full-text BM25 tokenizers, requiring a dual-database setup and complex sync logic.

### Consequences:
- **Positive**: Single database for relational data, vectors, and full-text search. Eliminates an entire distributed cluster, cuts infrastructure RAM requirements by > 50%, guarantees zero data drift, and enables single-command backups (`pg_dump` / WAL-G).
- **Negative**: HNSW indices must fit in RAM. As corpus grows beyond 2–3 million chunks, vector queries may contend with relational queries for buffer cache.

---

## ADR-002: Direct Reverse-Proxy Routing for Streaming Chat

### Status: Accepted
### Context:
In Onyx, the browser routes chat requests to Next.js (`/api/[...path]`), which acts as an HTTP proxy forwarding requests to FastAPI. During long Server-Sent Events (SSE) streaming turns, Node.js holds open duplex streams, causing high memory usage under concurrent load.

### Decision:
Configure the edge reverse proxy (Traefik / Nginx) to route `/api/*` requests **directly to FastAPI**, while routing static assets and SSR pages to Next.js.

### Alternatives Considered:
1. *Keep Next.js API Proxy*: Simple development setup, but introduces memory bloat and latency hops in production.
2. *WebSockets*: Full duplex, but requires persistent socket connections, stateful load balancing, and is more fragile across enterprise corporate proxies than standard HTTP SSE.

### Consequences:
- **Positive**: SSE streams pipe directly from FastAPI to the browser with zero intermediate Node.js buffering, cutting memory overhead by > 60%.
- **Negative**: Requires reverse proxy configuration in both local development and production.

---

## ADR-003: Choice of LiteLLM Gateway Over LangChain

### Status: Accepted
### Context:
The application must support 100+ LLM providers (OpenAI, Anthropic, Google Gemini, Azure, Bedrock, Groq, Ollama) without locking into any vendor.

### Decision:
Adopt **LiteLLM** as the unified LLM invocation gateway.

### Alternatives Considered:
1. *LangChain*: Heavy abstractions, frequent breaking API changes, high cognitive overhead, and debugging friction.
2. *Direct Provider SDKs*: High engineering burden maintaining separate libraries and schema mappers for 10+ cloud vendors.

### Consequences:
- **Positive**: Lightweight, transparent OpenAI-compatible interface, robust cost calculation tables, and prompt caching.
- **Negative**: Dependent on LiteLLM maintaining timely parameter mappings for newly announced models.

---

## ADR-004: Dual SQLAlchemy Engine (Asyncpg + Psycopg)

### Status: Accepted
### Context:
FastAPI request handlers and streaming chat loops benefit immensely from asynchronous non-blocking database queries (`asyncpg`). Conversely, Celery background workers and Alembic migrations operate synchronously and benefit from standard connection pooling (`psycopg2` / `psycopg3`).

### Decision:
Implement a dual SQLAlchemy 2.0 engine architecture:
- `async_engine` (powered by `asyncpg`) for FastAPI request endpoints.
- `sync_engine` (powered by `psycopg2`) for Celery workers and Alembic migrations.

### Consequences:
- **Positive**: Prevents event loop blocking during chat streaming while preserving thread safety in background workers.
- **Negative**: Requires maintaining async and sync session factory helpers.

Tenant-scoped reads and writes must enforce tenant identity in application queries and must not leak tenant context across pooled connections. The exact RLS policy, transaction-bound context-setting mechanism, and pool reset strategy remain open and must be decided and tested before tenant isolation is implemented.

---

## ADR-005: Context Window Token Budgeting & Chunk Prepending

### Status: Accepted
### Context:
When documents are split into 512-token segments, individual chunks lose surrounding context (e.g., a chunk might contain financial numbers without stating which company or quarter they belong to).

### Decision:
During chunking, automatically prepend document metadata headers (`Title: {title} | Source: {path} | Section: {header}`) to the raw text before embedding and indexing.

### Consequences:
- **Positive**: Dramatically improves embedding similarity scores and keyword BM25 matches for isolated passages.
- **Negative**: Consumes ~20–40 tokens per chunk from the total chunk size.

---

## ADR-006: Partitioned Celery Queues for Asynchronous Workloads

### Status: Accepted
### Context:
A large connector crawl (e.g. 50,000 files from Google Drive) can flood task queues, causing high-priority user actions (document uploads, email invites, password resets) to queue behind hours of batch processing.

### Decision:
Segment Celery tasks into four isolated queues:
- `ingestion`: Batch chunking, embedding, vector writes.
- `connectors`: External API polling with adaptive rate-limiting backoff.
- `pruning`: Document deletion and garbage collection.
- `default`: High-priority user actions and notifications.

### Consequences:
- **Positive**: Heavy background crawls never delay interactive user operations.
- **Negative**: Requires configuring worker concurrency per queue in deployment manifests.

---

## ADR-007: Search Engine Migration Criteria & Rebuildable Vector Strategy

### Status: Accepted
### Context:
While PostgreSQL with `pgvector` is ideal for initial implementation and scales comfortably to 1–3 million chunks, future enterprise growth may eventually justify a dedicated distributed search cluster (e.g., OpenSearch or Qdrant).

### Decision:
1. Treat vector embeddings and `tsvector` columns as **rebuildable derived data**. PostgreSQL remains the single permanent source of truth for raw document text, titles, links, and ACL metadata.
2. Maintain the `SearchProvider` interface contract so the application can swap search providers by updating `SEARCH_PROVIDER=opensearch` or `SEARCH_PROVIDER=qdrant` in configuration, with zero modifications to chat, RAG, or agent code.
3. Establish measurable triggers that justify executing a migration:
   - **Corpus Volume**: Total chunks exceed **3,000,000** on a single node.
   - **Memory Pressure**: HNSW index size exceeds 70% of available RAM, degrading relational query cache hit rates.
   - **Latency & Concurrency**: Sustained search load exceeds **50 QPS** with p95 search latency exceeding **300 ms**.
   - **Linguistic Requirements**: Requirement for specialized language analyzers (e.g. Japanese Kuromoji or CJK n-gram tokenizers) beyond standard PostgreSQL dictionary capabilities.

### Consequences:
- **Positive**: Clear, data-driven migration criteria without premature optimization or unnecessary early infrastructure bloat.
- **Negative**: Requires maintaining bulk-reindexing scripts to export chunks into OpenSearch/Qdrant if migration occurs.
