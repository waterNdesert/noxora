# Final Technical Architecture Validation & Readiness Assessment

This document records the validation of Nexora's foundational architecture and planning documents.

The architecture was evaluated across five rigorous engineering dimensions: **completeness**, **consistency**, **security**, **scalability**, and **implementation feasibility**.

---

## 1. Overall Architecture Assessment

### Executive Summary
**Approved initial search architecture:** PostgreSQL 16+ with `pgvector` and PostgreSQL Full-Text Search (FTS), accessed through the `SearchProvider` contract. OpenSearch and Qdrant are possible future providers only; they are not part of the approved implementation.

**Assessment: APPROVED FOUNDATION DIRECTION; implementation details remain staged**, including:
1. **Infrastructure**: PostgreSQL consolidates relational and initial search storage; actual resource requirements remain to be measured.
2. **Browser/API boundary**: Same-origin reverse-proxy routing sends API and SSE requests directly to FastAPI, avoiding a Next.js API-proxy hop.
3. **Pluggable Architecture**: The `SearchProvider` contract provides a boundary for evaluating future providers. Switching engines still requires migration, reindexing, operational planning, and security review.

Several technical choices regarding **pgvector HNSW tuning, the canonical document ACL model, and multilingual FTS** remain open and must be resolved before implementing retrieval. RLS and tenant connection-pool handling remain open for future enterprise isolation, not MVP implementation.

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
- **Confirmed Strength**: The proposed SQL Common Table Expression (CTE) combines vector and PostgreSQL full-text result ranks using $1 / (60 + \text{rank})$, avoiding the need to normalize incompatible distance and ranking scores. The candidate limits and settings require retrieval evaluation.
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

### 2.4. Single-Tenant MVP and Future Multi-Tenant Isolation
- The MVP is one tenant per deployment. Tenant context is selected and enforced server-side; clients cannot choose it.
- Tenant identifiers in the proposed schema support future evolution but do not provide isolation.
- RLS is not part of the MVP. Its policy, transaction-bound context, pooled-connection reset, and security tests require a separately approved design before implementation.

---

### 2.5. Permission Hierarchy (Tenant, Workspace, Document & Chunk)
- **Proposed concepts, not an approved enforcement model**:
  - Tenant Level: Tenant identifiers are present in the proposed data model; they are not, on their own, an isolation guarantee.
  - Group Level: `user_groups` and `user_group_members`.
  - Document Level: `document_access` junction table.
  - Chunk Level: `access_control_list TEXT[]` array on `document_chunks`.
- **Open questions**:
  - The canonical representation and enforcement path for document permissions is unresolved. Do not combine the proposed ACL array and `document_access` table as if their semantics were already consistent.
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
  - Because search data resides in PostgreSQL, a delete-and-replace can be atomic when performed in one transaction. Implementation must preserve this consistency; zero downtime is not assumed without measurement.

---

### 2.7. Background Processing (Celery & Redis)
- **Approved timing and purpose**: Introduce Celery and Redis when document upload/ingestion is implemented, currently Sprint 2. Neither is required in Sprint 1.
- The ingestion workflow must expose processing status, report failures, and retry according to a defined policy.
- Broker persistence, recovery, idempotency, and retry configuration must be decided before ingestion deployment; proposed settings are not approved requirements.

---

### 2.8. Secret Encryption & Key Management
- The current credential-encryption proposal applies to connector credentials, not browser sessions or provider API keys.
- Provider API keys must not be persisted until their configuration and secure-storage approach are approved.
- Encryption key derivation and nonce handling must be reviewed before connector-credential storage is implemented; the existing AES-GCM notes are security guidance, not a Sprint 1 requirement.

---

## 3. Open Questions and Validation Follow-Ups

The following items were identified during validation. They are not silently treated as resolved decisions:

1. **Workspace entity and scope**:
   - Open question: confirm whether workspace-level permissions belong in the MVP before adding a workspace table and related foreign keys.
2. **HNSW and FTS query settings**:
   - Candidate settings include `SET LOCAL hnsw.ef_search = 100` and an unstemmed `'simple'` text search path for code and technical acronyms.
   - Open question: benchmark and approve search settings when implementing retrieval; do not assume these values are accepted production settings.
3. **Future tenant isolation**:
   - Decide and test the RLS policy, transaction-bound context-setting mechanism, and pool reset strategy before enterprise tenant isolation is implemented. These are not MVP requirements.
4. **Account provisioning and password recovery**:
   - Decide whether accounts after the one-time administrator bootstrap are created through public registration or administrator-managed provisioning, and define password reset behavior before implementing those flows.
   - **Approved session lifecycle**: 30-minute sliding idle timeout and 12-hour absolute lifetime; the absolute expiry never extends. Expired sessions are invalidated server-side, and logout immediately invalidates the session.
5. **OAuth details**:
   - Google and GitHub OAuth are MVP requirements, scheduled for Sprint 5. Decide account-linking and verified-email behavior before implementing provider flows.
6. **Provider-key configuration**:
   - Decide whether MVP LLM provider access comes from deployment configuration or an administrative workflow. Do not persist provider keys until secure storage is approved.
7. **Document access-control model**:
   - The proposed architecture and database schema use inconsistent ACL representations. Resolve the canonical model before search implementation.
8. **Object storage and ingestion reliability**:
   - Select the local and production object-storage provider and define deletion/retention behavior before upload implementation. Define Celery/Redis broker persistence, idempotency, and retry behavior before deploying ingestion workers.

---

## 4. Issues Safely Deferred to Later Sprints

| Issue | Resolution Target | Why It Can Wait |
| :--- | :--- | :--- |
| **OpenSearch / Qdrant Adapter Code** | Future evaluation / Post-MVP | No dedicated search dependency is approved; evaluate alternatives only against measured requirements. |
| **SAML 2.0 XML Certificate Validation** | Sprint 16 (Phase 5) | Local sessions and MVP OAuth cover the initial application; enterprise SSO is later scope. |
| **Python Code Sandbox gVisor Hardening** | Sprint 12 (Phase 3) | Code execution is not part of the MVP. |
| **Stripe Billing & Seat Webhooks** | Sprint 19 (Phase 5) | Commercial licensing is not needed for internal product development. |
| **Scalar Vector Quantization (SQ)** | Post-MVP, if required | Embedding dimensions and workload are not yet selected; consider quantization only if measured memory requirements justify it. |

---

## 5. Security & Infrastructure Summary

### Security Baseline:
- **Transport and browser auth**: Same-origin reverse-proxy routing; opaque server-side sessions; HTTP-only, production Secure, `SameSite=Lax`, `Path=/`, host-only cookies; CSRF protections and Origin validation.
- **Passwords and sessions**: Argon2id password hashing; store session secrets only as hashes; invalidate sessions on logout and relevant account/password security changes.
- **Provider and connector secrets**: Do not persist provider API keys until configuration and secure storage are approved. Evaluate connector-secret encryption before connector implementation.
- **Authorization**: Enforce user/document access policy before search results leave PostgreSQL. Tenant IDs alone do not provide isolation; MVP is single-tenant and does not implement RLS.
- **CORS & CSP**: Restrict origins and frame embedding according to deployment requirements.

### Infrastructure Baseline for Sprint 1:
- **PostgreSQL 16+ with pgvector available**. Confirm the image and extension compatibility when implementation begins; do not assume resource settings from the earlier proposal are validated requirements.
- **Redis and Celery are excluded from Sprint 1** and introduced with asynchronous document ingestion.
- **Python Backend**: Python 3.13 on Debian slim.
- **Web Frontend**: Node.js 22 LTS / Next.js 16.

---

## 6. Final Recommendation

### **VERDICT: APPROVED FOUNDATION DIRECTION; IMPLEMENT IN STAGES**

The approved initial search direction uses PostgreSQL + pgvector and PostgreSQL FTS, with no OpenSearch dependency. Sprint 1 is in progress. Follow the [roadmap](../development/ROADMAP.md) and [Sprint 1 foundation plan](../sprints/SPRINT_01_FOUNDATION_PLAN.md); resolve open questions before implementing the feature or schema work that depends on them.
