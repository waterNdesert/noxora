# Known Issues, Failure Modes & Technical Debt

This document outlines potential bottlenecks, operational risks, failure recovery strategies, and architectural technical debt identified in the Onyx codebase.

---

## 1. Operational Failure Modes & Mitigation

### A. Celery Worker Out-Of-Memory (OOM) Crashes
- **Root Cause**: Ingesting massive PDFs, spreadsheets, or bulk text files can exhaust worker memory during OCR or PyPDF parsing.
- **Symptom**: Celery worker is silently terminated by the Linux OOM killer (`SIGKILL`). The active `IndexAttempt` remains indefinitely stuck in `IN_PROGRESS`, holding the Redis connector lock.
- **Mitigation & Recovery**:
  - The `prune-stale-index-attempts` periodic task detects jobs with no heartbeat for > 15 minutes, marks them `FAILED`, and releases the Redis lock.
  - Production deployments should set Celery worker concurrency limits (`--concurrency=2` or `--concurrency=4`) and max tasks per child (`--max-tasks-per-child=100`) to prevent memory leaks from accumulating.

### B. OpenSearch Circuit Breaker Trips
- **Root Cause**: Concurrent dense vector k-NN queries combined with large text aggregations can exceed OpenSearch JVM heap limits (defaulting to 50% of container memory).
- **Symptom**: HTTP 429 errors from OpenSearch: `circuit_breaking_exception: [parent] Data too large`.
- **Mitigation**:
  - Allocate at least 8 GB of RAM to OpenSearch with `ES_JAVA_OPTS="-Xms4g -Xmx4g"`.
  - Ensure vector indices use `hnsw` with quantized vector formats if dataset size exceeds available RAM.

### C. Upstream Connector API Rate Limits (HTTP 429)
- **Root Cause**: Ingesting workspaces with hundreds of thousands of files (e.g., enterprise Google Drive or Slack) triggers upstream rate limits.
- **Symptom**: Ingestion stalls or fails with exponential backoff delays.
- **Mitigation**:
  - Connectors implement adaptive jittered backoff (`backend/onyx/connectors/`).
  - Batching mechanisms reduce API round trips. Admins should schedule large initial syncs during off-peak hours.

---

## 2. Architectural Bottlenecks & Technical Debt

### A. Double-Proxying Through Next.js
- **Observation**: Browser requests route to Next.js (`web/src/app/api/[...path]/route.ts`), which acts as an HTTP proxy forwarding to the FastAPI backend.
- **Impact**: For streaming chat responses (SSE), Node.js must keep open duplex stream handles. At high concurrency (thousands of active chat streams), the Node process experiences elevated memory consumption.
- **Recommendation**: In large production environments, let Nginx or a cloud load balancer (e.g., AWS ALB) route `/api/*` directly to FastAPI, bypassing the Node.js process entirely.

### B. Embedding Model Migration Overhead
- **Observation**: Vectors in OpenSearch are tightly coupled to the specific embedding model dimensionality (e.g., 1024 dimensions for BGE-large, 1536 for OpenAI).
- **Impact**: Changing the embedding model requires re-embedding every chunk across the entire document corpus. While `backend/onyx/db/swap_index.py` supports background dual-indexing without downtime, it demands double the OpenSearch storage and significant compute during the transition.

### C. Dynamic Code Splitting Parity (CE vs EE)
- **Observation**: Feature gating relies on `fetch_versioned_implementation` and dynamic imports.
- **Impact**: If an interface in `backend/onyx/` changes its parameter signature, the corresponding file in `backend/ee/onyx/` must be updated in lockstep. Without comprehensive integration tests across both editions, runtime `AttributeError` or `TypeError` can occur.

### D. PostgreSQL JSONB Query Complexity
- **Observation**: Connector configurations, metadata filters, and tool arguments are stored extensively in PostgreSQL `JSONB` columns.
- **Impact**: While flexible, complex queries filtering across deep JSON keys can cause sequential table scans if appropriate GIN (Generalized Inverted Index) indices are not maintained.

