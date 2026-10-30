# Final Technical Architecture Validation & Readiness Assessment

This document records the validation of Nexora's foundational architecture and planning documents.

The architecture was evaluated across five rigorous engineering dimensions: **completeness**, **consistency**, **security**, **scalability**, and **implementation feasibility**.

---

## 1. Overall Architecture Assessment

### Executive Summary
**Approved initial search architecture:** PostgreSQL 16+ with `pgvector` and PostgreSQL Full-Text Search (FTS), accessed through the `SearchProvider` contract. OpenSearch and Qdrant are possible future providers only; they are not part of the approved implementation.

**Assessment: ARCHITECTURE IS SOUND AND VIABLE**, with marked improvements over Onyx in:
1. **Infrastructure Footprint**: Removing OpenSearch cuts baseline idle memory from 16 GB to < 4 GB RAM, eliminating a separate JVM cluster and eliminating eventual consistency sync lag.
2. **Streaming Latency**: Direct reverse proxy routing from Traefik/Nginx to FastAPI bypasses the Node.js duplex streaming bottleneck identified in Onyx.
3. **Pluggable Architecture**: The `SearchProvider` contract ensures that if chunk volumes exceed PostgreSQL thresholds (e.g., > 3M chunks), switching to OpenSearch or Qdrant requires zero changes to RAG, chat, or agent modules.

Several technical choices regarding **pgvector HNSW tuning, RLS connection pooling, and multilingual FTS** remain open and must be resolved before implementing retrieval or tenant isolation.

---

## 2. Deep-Dive Technical Evaluations

### 2.1. PostgreSQL Hybrid Search (`pgvector` + FTS)
- **Confirmed Strength**: Combining `pgvector` HNSW vector distance with PostgreSQL's built-in `tsvector` / `tsquery` in a single database guarantees atomic updates, ACID transactionality on document deletions, and zero cross-system data drift.
- **Identified Gap / Assumption**:
  - In the proposed [database design](DATABASE_DESIGN.md), the generated `tsv_content` column uses `'english'`:
    ```sql
    tsv_content TSVECTOR GENERATED ALWAYS AS (
        to_tsvector('english', coalesce(title, '') || ' ' || coalesce(content, ''))
    ) STORED
    ```
  - *Risk*: Code snippets, stack traces, URLs, acronyms, and non-English documents (German, French, Spanish, Japanese) will be incorrectly stemmed by the English Snowball dictionary.
  - *Open follow-up for retrieval work*: Evaluate an unstemmed `'simple'` analyzer alongside `'english'` for code, acronyms, and non-English content. The final analyzer strategy remains undecided.

---

### 2.2. Reciprocal Rank Fusion (RRF) Implementation
- **Confirmed Strength**: The SQL Common Table Expression (CTE) combining top-100 vector matches and top-100 keyword matches using $1 / (60 + \text{rank})$ avoids normalizing incompatible cosine distances and BM25 scores.
- **Identified Gap / Assumption**:
  - The default `hnsw.ef_search` parameter in `pgvector` is `40`. If the CTE requests `LIMIT 100`, HNSW will only explore 40 candidates by default, returning fewer than 100 items or truncating recall.
  - *Candidate setting to benchmark*: The search implementation may need to set `hnsw.ef_search` in a transaction before querying, for example:
    ```sql
    SET LOCAL hnsw.ef_search = 100;
    ```

---

### 2.3. Candidate HNSW Configuration & Memory Sizing
- **Proposed schema values, not benchmark-validated**: `m = 16, ef_construction = 64` on `embedding vector_cosine_ops`.
- **Benchmarking Need**:
  - Vector dimensionality matters: a 1024-dimensional vector (for example, one possible BGE model configuration) uses about 4 KB per vector before index overhead. The selected model/dimension is unresolved.
  - `ef_construction = 128` is a candidate to benchmark if high recall is required; it is not an approved value.
  - PostgreSQL's `maintenance_work_mem` must be sized to at least `1 GB` to prevent HNSW index creation from swapping to disk during initial ingestion.

---

### 2.4. Row-Level Security (RLS) & Multi-Tenant Isolation
- **Schema-supporting measure, not an isolation guarantee**: Mandatory `tenant_id` fields on operational tables support tenant scoping but do not by themselves ensure strict data isolation.
- Tenant-scoped reads and writes must enforce tenant identity in application queries and must not leak tenant context across pooled connections. The exact RLS policy, transaction-bound context-setting mechanism, and pool reset strategy remain open and must be decided and tested before tenant isolation is implemented.

---

### 2.5. Permission Hierarchy (Tenant, Workspace, Document & Chunk)
- **Confirmed Architecture**:
  - Tenant Level: Tenant identifiers are present in the proposed data model; they are not, on their own, an isolation guarantee.
  - Group Level: `user_groups` and `user_group_members`.
  - Document Level: `document_access` junction table.
  - Chunk Level: `access_control_list TEXT[]` array on `document_chunks`.
- **Open question**:
  - The concept of "Workspace" (a collaborative project sub-boundary within a tenant) was cited in requirements but omitted from the initial DDL.
  - A workspace table and related foreign keys are one possible design. Confirm whether workspace-level permissions are an MVP requirement before adding them.

---

### 2.6. Ingestion Atomicity & Deletion Consistency
- **Problem**: When an updated file is re-ingested (e.g. an edited Google Doc), chunk boundaries shift. If the new version yields 12 chunks while the previous had 15, chunks 13–15 would remain orphaned if not cleanly purged.
- **Resolution**:
  - Ingestion runs must execute inside a PostgreSQL transaction:
    ```sql
    DELETE FROM document_chunks WHERE tenant_id = :t AND document_id = :d;
    INSERT INTO document_chunks (...) VALUES (...);
    ```
  - Because all chunks reside in PostgreSQL (unlike the dual Postgres/OpenSearch setup in Onyx), this atomic delete-and-replace executes in a single transaction with zero downtime.

---

### 2.7. Background Processing (Celery & Redis)
- **Confirmed Architecture**: Partitioned queues (`ingestion`, `connectors`, `pruning`, `default`).
- **Resilience Requirement**:
  - Redis broker must be configured with append-only file persistence (`appendonly yes`) so enqueued tasks survive Redis container restarts.
  - Celery workers must specify `--max-tasks-per-child=100` to prevent memory leaks during heavy PDF parsing with `pypdf`/`pdfminer`.

---

### 2.8. Secret Encryption & Key Management
- **Confirmed Architecture**: AES-GCM 256-bit encryption for stored credentials.
- **Security Requirement**:
  - The 32-byte encryption key must be derived from `ENCRYPTION_KEY_SECRET` using a standard Key Derivation Function (HKDF or PBKDF2 with SHA-256) rather than raw string truncation.
  - Nonces (Initialization Vectors / IVs) must be generated uniquely using `os.urandom(12)` for every single encryption operation and stored alongside the ciphertext.

---

## 3. Open Questions and Validation Follow-Ups

The following items were identified during validation. They are not silently treated as resolved decisions:

1. **Workspace entity and scope**:
   - Open question: confirm whether workspace-level permissions belong in the MVP before adding a workspace table and related foreign keys.
2. **HNSW and FTS query settings**:
   - Candidate settings include `SET LOCAL hnsw.ef_search = 100` and an unstemmed `'simple'` text search path for code and technical acronyms.
   - Open question: benchmark and approve search settings when implementing retrieval; do not assume these values are accepted production settings.
3. **Tenant context handling for connection pools**:
   - Decide and test the RLS policy, transaction-bound context-setting mechanism, and pool reset strategy before tenant isolation is implemented.
4. **OAuth delivery sequence**:
   - The MVP scope includes Google/GitHub OAuth, while the roadmap's Sprint 1 describes local authentication and does not assign OAuth to a later sprint. Confirm the OAuth scope and sprint before making an MVP delivery commitment.

---

## 4. Issues Safely Deferred to Later Sprints

| Issue | Resolution Target | Why It Can Wait |
| :--- | :--- | :--- |
| **OpenSearch / Qdrant Adapter Code** | Phase 5 / Post-MVP | `SearchProvider` interface is defined; Postgres handles < 3M chunks easily. |
| **SAML 2.0 XML Certificate Validation** | Sprint 15 (Phase 5) | Local JWT and OAuth2 cover all MVP and early testing needs. |
| **Python Code Sandbox gVisor Hardening** | Sprint 11 (Phase 3) | Basic Docker container with dropped capabilities suffices for initial tool testing. |
| **Stripe Billing & Seat Webhooks** | Sprint 18 (Phase 5) | Commercial licensing is not needed for internal product development. |
| **Scalar Vector Quantization (SQ)** | Post-MVP (> 1M chunks) | Uncompressed 1024-dim vectors fit easily in RAM for datasets under 500,000 chunks. |

---

## 5. Security & Infrastructure Summary

### Security Baseline:
- **Transport**: TLS 1.3 at edge; HTTP-only, `SameSite=Lax`, signed JWT cookies.
- **Storage**: AES-GCM 256 credential encryption with unique 12-byte IVs.
- **Authorization**: Mandatory tenant ID and ACL array overlap (`&&`) filtering in SQL before results leave PostgreSQL.
- **CORS & CSP**: Strict frame-ancestors preventing clickjacking; locked CORS origin headers.

### Infrastructure Baseline for Sprint 1 (Docker Compose):
- **PostgreSQL 16**: Using `pgvector/pgvector:pg16` image.
  - Recommended memory: 4 GB RAM assigned to container.
  - Postgres configs: `shared_buffers = 1GB`, `work_mem = 64MB`, `maintenance_work_mem = 512MB`.
- **Redis 7**: Using `redis:7-alpine` with AOF persistence.
- **Python Backend**: Python 3.13 on Debian slim.
- **Web Frontend**: Node.js 22 LTS / Next.js 16.

---

## 6. Final Recommendation

### **VERDICT: APPROVED FOUNDATION DIRECTION; IMPLEMENT IN STAGES**

The approved foundation direction uses PostgreSQL + pgvector and PostgreSQL FTS, with no OpenSearch dependency. Sprint 1 foundation work can proceed within its roadmap scope. See the [roadmap](../development/ROADMAP.md) and [Sprint 1 foundation plan](../sprints/SPRINT_01_FOUNDATION_PLAN.md). Resolve each open question before implementing the feature or schema work that depends on it.
