# Minimum Viable Product (MVP) Scope & Boundaries

This document defines the exact scope, boundaries, and trade-offs of the initial Minimum Viable Product (MVP), featuring a lightweight, consolidated architecture powered by **PostgreSQL 16+ with `pgvector` and Full-Text Search (FTS)** with zero OpenSearch dependency.

---

## 1. MVP Vision & Core Value Proposition

The MVP delivers a **fully functional internal AI search and chat assistant** that an organization can immediately deploy, upload proprietary knowledge into, and query with natural language, receiving fast, streaming answers backed by verifiable citations.

### Target User for MVP:
- **Knowledge Worker**: Uploads documents (PDF, Word, Markdown) and asks questions to quickly find internal answers without reading 50-page reports.
- **Team Lead / Admin**: Configures access to an approved LLM provider and manages the initial knowledge collection. Provider-key configuration and storage details remain unresolved; do not persist provider keys until the configuration and secure-storage approach is approved. Custom personas are deferred.

---

## 2. In-Scope vs. Out-of-Scope Matrix

| Capability | In MVP Scope | Deferred to Later Phases | Rationale for Deferral |
| :--- | :---: | :---: | :--- |
| **Local Auth (Email/Password)** | **Yes** | — | Essential for basic access control |
| **Google / GitHub OAuth2** | **Yes** | **Sprint 5 (Phase 1)** | Frictionless user onboarding; dedicated sprint after local session foundation |
| **Enterprise SAML 2.0 / OIDC** | No | **Phase 5** | Complex IdP setup; not needed for initial team evaluation |
| **Direct File Uploads (PDF/DOCX)**| **Yes** | — | Core document ingestion mechanism |
| **Workplace Connectors (Google, Slack)**| No | **Phase 2** | High initial API credential configuration overhead |
| **PostgreSQL Hybrid Search (`pgvector` + FTS)** | **Yes** | — | High-precision retrieval with zero distributed database overhead |
| **OpenSearch Cluster** | No | **Optional future evaluation** | Not an initial dependency; consider only after measured requirements justify a provider change |
| **Cross-Encoder Reranking** | No | **Evaluate after MVP hybrid-search baseline** | Add only if retrieval evaluation demonstrates value or it is explicitly scheduled |
| **Streaming Chat UI (SSE)** | **Yes** | — | Core user experience expectation |
| **Inline Clickable Citations** | **Yes** | — | Critical for verifying AI trust and accuracy |
| **Multi-LLM Gateway (OpenAI/Claude)**| **Yes** | — | Avoids vendor lock-in from Day 1 |
| **Custom AI Assistants (Personas)** | No | **Phase 3: Sprint 10** | Defer customization; MVP can use a default assistant |
| **Python Code Sandbox** | No | **Phase 3** | Requires container sandboxing infrastructure |
| **FastMCP / OpenAPI Actions** | No | **Phase 3** | Advanced capability; RAG takes priority |
| **Slackbot & Discord Bot** | No | **Phase 4** | Web interface is sufficient for initial testing |
| **Enterprise Multi-Tenant Isolation / RLS** | No | **Phase 5: Sprint 18** | The MVP is one tenant per deployment; tenant IDs alone do not provide isolation |
| **Stripe Billing & Whitelabeling** | No | **Phase 5** | Commercialization features; not needed for internal utility |

---

## 3. The End-to-End MVP User Journey

1. **Setup**: Administrator starts the PostgreSQL service and the local API, web, and Nginx processes using the documented development workflow, then navigates to `http://localhost:8080`.
2. **Initial administrator**: An operator creates the first administrator using the one-time setup command. The subsequent account-provisioning policy remains to be decided; public registration is not implied.
3. **Model provider configuration**: The MVP must have approved LLM-provider access. Whether provider credentials are supplied through deployment configuration or an administrative workflow remains unresolved. Do not persist provider keys until secure storage is approved.
4. **Document ingestion**: An authorized user uploads company policy documents.
   - The API creates an ingestion job and stores the original in the selected object store. Celery/Redis workers extract and clean text, chunk it, generate embeddings using the model/dimension selected before schema implementation, store searchable data in PostgreSQL, and report status, failures, and retry outcomes.
5. **Conversational Query**: User asks "What is our travel reimbursement policy for international flights?"
   - System executes PostgreSQL hybrid search (PostgreSQL FTS ranking + vector similarity) with Reciprocal Rank Fusion (RRF), behind `SearchProvider`.
   - A cross-encoder is not part of the initial pipeline; retain an extension point and evaluate reranking after establishing the baseline.
   - LLM streams the answer with inline citation `[[1]]`.
6. **Verification**: User clicks citation `[[1]]`; a side drawer opens showing the exact page and paragraph from the source PDF.

---

## 4. Simplified MVP Infrastructure Topology

By removing OpenSearch and leveraging PostgreSQL for both relational records and vector/keyword search, the MVP topology is exceptionally lean:

```
[ Same-Origin Reverse Proxy (Nginx) ]
       │
       ├──> [ Next.js Web Frontend (Port 3000) ]
       │
       └──> [ FastAPI Backend (Port 8000) ]
                 │
                 ├──> [ PostgreSQL 16 + pgvector (Port 5432) ]
                 │         ├── Relational metadata and server-side auth sessions
                 │         └── FTS and vector search (after embedding decisions)
                 │
                 ├──> [ S3-compatible Object Storage - Original Documents ]
                 ├──> [ Celery Worker + Redis Broker - Async Ingestion ]
                 └──> [ External LLMs (OpenAI / Anthropic APIs) ]
```

The reverse proxy routes same-origin `/api/*` requests directly to FastAPI and other application routes to Next.js. Cookie-authenticated state-changing requests require CSRF protections and Origin validation. Redis is introduced with upload/ingestion, not Sprint 1; it is not the session store or a general cache in this scope.

### Provisional Hardware Planning Assumptions
- **2–4 vCPUs**
- **8 GB RAM**
- **50 GB SSD storage**

These are planning estimates, not validated minimum requirements. Measure the final workload and deployment before using them as sizing commitments.

---

## 5. Success Metrics for MVP
- The existing setup-time, TTFT, retrieval-precision, and resource-footprint figures are provisional goals, not guaranteed acceptance criteria. Define a benchmark corpus, hardware profile, and measurement method before using them to accept the MVP.
