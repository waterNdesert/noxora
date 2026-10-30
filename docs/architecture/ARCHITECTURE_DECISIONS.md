# Architecture Decision Records (ADRs)

This document records the foundational architectural decisions, rationale, alternatives considered, and trade-offs for the enterprise knowledge intelligence platform, featuring a **unified PostgreSQL 16+ hybrid search engine with `pgvector`**.

---

## ADR-001: Choice of PostgreSQL 16+ with `pgvector` & FTS for Unified Hybrid Retrieval

### Status: Accepted (Supersedes OpenSearch-mandatory design)
### Context:
Enterprise workplace search requires retrieving documents through both semantic intent (conceptual synonyms) and exact keyword matches (acronyms, code identifiers, employee names, exact error codes), while enforcing user access controls. Requiring OpenSearch for initial deployment adds operational overhead and a separate search data store.

### Decision:
**Approved initial search architecture:** PostgreSQL 16+ with `pgvector` and PostgreSQL Full-Text Search (FTS), accessed through the `SearchProvider` contract. OpenSearch and Qdrant are possible future providers only; they are not part of the approved implementation.

1. Deploy **PostgreSQL 16+ with the `pgvector` extension and Full-Text Search (FTS)** as the unified data store for both relational metadata and hybrid search.
2. Abstract all search, indexing, and deletion operations behind an abstract **`SearchProvider`** interface, with **`PgVectorSearchProvider`** as the default implementation.
3. Use PostgreSQL full-text ranking and pgvector ranking, combining result ranks with **Reciprocal Rank Fusion (RRF)**. HNSW and GIN are the intended index types; production settings remain subject to retrieval evaluation.

### Alternatives Considered:
1. *Mandatory OpenSearch 2.x*: Powerful for large-scale search, but excessive complexity for initial development and the MVP.
2. *Pure Vector Databases (Pinecone, Qdrant, Milvus)*: Excellent vector search, but require a separate keyword-search path and data synchronization.

### Consequences:
- **Positive**: One database can hold relational data and search data; updates can be atomic when source records and derived search data are committed in the same transaction.
- **Negative**: Vector indexes and relational workloads compete for resources. Performance and scale limits require measurement; no corpus threshold is guaranteed by this decision.

---

## ADR-002: Same-Origin Reverse-Proxy Routing and Browser Sessions

### Status: Accepted
### Context:
The browser application uses cookie-based authentication. Routing API requests through a different origin complicates cookie and CSRF handling; routing streaming requests through Next.js also adds a proxy hop.

### Decision:
Use **opaque server-side sessions** for the first-party browser application. Route browser `/api/*` requests through the same-origin **Nginx** reverse proxy directly to FastAPI, and route frontend pages and assets to Next.js. Protect state-changing cookie-authenticated requests with CSRF protections and Origin validation. Use HTTP-only, production Secure, SameSite=Lax, Path=/, host-only session cookies.

Sessions have a **30-minute sliding idle timeout** and a **12-hour absolute lifetime**. Activity may extend the idle expiry but never the absolute expiry. Expired sessions are invalidated server-side and require reauthentication; logout immediately invalidates the session.

### Alternatives Considered:
1. *JWT access and refresh tokens*: Viable when explicitly designed, but require refresh rotation, revocation, key rotation, and browser storage policies not needed for this first-party session model.
2. *Cross-origin API*: Possible, but requires more complex credentialed CORS and cookie security configuration.

### Consequences:
- **Positive**: One browser origin simplifies cookie handling; SSE streams go directly from FastAPI without a Next.js proxy.
- **Negative**: Requires the same-origin reverse-proxy route in local development and production, plus CSRF and Origin protections.

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
Use SQLAlchemy 2.0 with:
- `async_engine` (powered by `asyncpg`) for FastAPI request endpoints.
- A synchronous PostgreSQL driver (`psycopg3`) for Alembic migrations. Add a synchronous worker engine only when background workers are introduced.

### Consequences:
- **Positive**: Prevents event loop blocking during chat streaming while preserving thread safety in background workers.
- **Negative**: Requires maintaining async and sync session factory helpers.

The MVP has one server-selected tenant. Tenant IDs do not provide isolation, and RLS is not part of the MVP. The exact RLS policy, transaction-bound context-setting mechanism, and pool reset strategy remain open and must be decided and tested before future tenant isolation is implemented.

---

## ADR-005: Context Window Token Budgeting & Chunk Prepending

### Status: Proposed; evaluate during retrieval implementation
### Context:
When documents are split into token-bounded segments, individual chunks can lose surrounding context (e.g., a chunk might contain financial numbers without stating which company or quarter they belong to).

### Decision:
During chunking, evaluate whether document metadata headers should be prepended to the text before embedding and indexing. This is a proposed retrieval behavior, not an MVP prerequisite.

### Consequences:
- **Positive**: May improve retrieval context for isolated passages.
- **Negative**: Consumes tokens per chunk. Validate the benefit during retrieval evaluation.

---

## ADR-006: Asynchronous Document Ingestion

### Status: Accepted for the upload/ingestion implementation; not a Sprint 1 dependency
### Context:
Document extraction and embedding can exceed a request's useful processing window and need visible status, failure reporting, and retries.

### Decision:
Use Celery with Redis for the document-ingestion background workload when document upload is implemented. The pipeline must support upload and job creation, extraction and cleaning, chunking, embedding generation, storage, processing status, failure reporting, and retries. Introduce the worker and broker with that implementation, not in Sprint 1. Additional queue partitioning is deferred until workloads require it.

### Consequences:
- **Positive**: Long-running ingestion is decoupled from HTTP requests and can report progress and failures.
- **Negative**: Adds broker, worker, retry, and operational responsibilities when upload is implemented.

---

## ADR-007: Search Engine Migration Criteria & Rebuildable Vector Strategy

### Status: Accepted
### Context:
PostgreSQL with `pgvector` is the approved initial search provider. Future workload or language requirements may justify evaluating a dedicated search system (e.g., OpenSearch or Qdrant).

### Decision:
1. Treat vector embeddings and `tsvector` columns as **rebuildable derived data**. PostgreSQL remains the single permanent source of truth for raw document text, titles, links, and ACL metadata.
2. Maintain the `SearchProvider` interface as a boundary for future search-provider evaluation. A provider migration will still require data export/reindexing, operational work, and security review; it is not a one-setting change.
3. Use the previously listed corpus, memory, latency, and language thresholds only as evaluation prompts, not approved migration triggers or guarantees. Validate thresholds against measured workloads before making a migration decision.

### Consequences:
- **Positive**: Avoids premature infrastructure while retaining a review point for measured future needs.
- **Negative**: Requires maintaining bulk-reindexing scripts to export chunks into OpenSearch/Qdrant if migration occurs.

---

## ADR-008: Local Account Security and Initial Administrator

### Status: Accepted

### Decision:
- Hash local passwords with Argon2id using library-managed salts and parameters.
- Store opaque session credentials only as hashes in persistent server-side session records.
- Use a 30-minute sliding idle timeout and a 12-hour absolute lifetime; the absolute expiry never extends. Expired sessions are invalidated server-side and require reauthentication.
- Invalidate a session immediately on logout and invalidate affected sessions after password changes/resets or account disablement.
- Create the initial administrator through a one-time setup command, not a public first-signup race.

The public-registration versus administrator-managed account-provisioning policy and password reset flow remain open and must be decided before implementing those behaviors.

---

## ADR-009: Single-Tenant MVP and Future Tenant-Aware Data Model

### Status: Accepted

### Decision:
The initial deployment is single-tenant. Tenant context is selected and enforced server-side; clients cannot choose or override it. The data model may retain tenant identifiers to support future evolution, but tenant IDs alone are not an isolation boundary. Do not implement or claim Row-Level Security (RLS) until the full policy, transaction-bound context, connection-pool reset, and security tests are approved.

### Consequences:
- **Positive**: Keeps the MVP deployment model simple while preserving a tenant-aware data shape.
- **Negative**: Future multi-tenant enforcement requires a separately reviewed design and migration; the current model does not provide enterprise isolation.

---

## ADR-010: Google and GitHub OAuth in the MVP

### Status: Accepted

### Decision:
Google and GitHub OAuth remain MVP requirements and are assigned to a dedicated Sprint 5 after the local session foundation. Both flows establish the same opaque server-side session used by local authentication.

Account linking, verified-email handling, and provider identities without a usable email must be decided before implementing OAuth.

---

## ADR-011: Provider API-Key Storage

### Status: Accepted

### Decision:
Do not persist LLM provider API keys until the configuration path and secure-storage approach are defined and approved. Existing connector-credential encryption proposals do not authorize provider-key persistence.

---

## ADR-012: Embedding Model and Schema

### Status: Accepted

### Decision:
Select the embedding provider, model, dimension, and versioning strategy before implementing the embedding schema. Any sample dimension or index parameter in research and design material is illustrative, not approved.

---

## ADR-013: Optional Search Reranking

### Status: Accepted

### Decision:
Keep the retrieval pipeline extensible for a reranking stage. Establish and evaluate the initial PostgreSQL hybrid-retrieval baseline before implementing cross-encoder reranking, unless it is explicitly scheduled based on that evaluation.
