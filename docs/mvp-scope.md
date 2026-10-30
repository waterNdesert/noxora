# Minimum Viable Product (MVP) Scope & Boundaries

This document defines the exact scope, boundaries, and trade-offs of the initial Minimum Viable Product (MVP), featuring a lightweight, consolidated architecture powered by **PostgreSQL 16+ with `pgvector` and Full-Text Search (FTS)** with zero OpenSearch dependency.

---

## 1. MVP Vision & Core Value Proposition

The MVP delivers a **fully functional internal AI search and chat assistant** that an organization can immediately deploy, upload proprietary knowledge into, and query with natural language, receiving fast, streaming answers backed by verifiable citations.

### Target User Persona for MVP:
- **Knowledge Worker**: Uploads documents (PDF, Word, Markdown) and asks questions to quickly find internal answers without reading 50-page reports.
- **Team Lead / Admin**: Configures OpenAI or Anthropic API keys, manages team members, and creates tailored assistants with specific prompt instructions.

---

## 2. In-Scope vs. Out-of-Scope Matrix

| Capability | In MVP Scope | Deferred to Later Phases | Rationale for Deferral |
| :--- | :---: | :---: | :--- |
| **Local Auth (Email/Password)** | **Yes** | — | Essential for basic access control |
| **Google / GitHub OAuth2** | **Yes** | — | Frictionless user onboarding |
| **Enterprise SAML 2.0 / OIDC** | No | **Phase 5** | Complex IdP setup; not needed for initial team evaluation |
| **Direct File Uploads (PDF/DOCX)**| **Yes** | — | Core document ingestion mechanism |
| **Workplace Connectors (Google, Slack)**| No | **Phase 2** | High initial API credential configuration overhead |
| **PostgreSQL Hybrid Search (`pgvector` + FTS)** | **Yes** | — | High-precision retrieval with zero distributed database overhead |
| **OpenSearch Cluster** | No | **Optional Post-MVP** | Unnecessary operational burden for < 2M chunks |
| **Cross-Encoder Reranking** | **Yes** | — | Eliminates false-positive hallucinations |
| **Streaming Chat UI (SSE)** | **Yes** | — | Core user experience expectation |
| **Inline Clickable Citations** | **Yes** | — | Critical for verifying AI trust and accuracy |
| **Multi-LLM Gateway (OpenAI/Claude)**| **Yes** | — | Avoids vendor lock-in from Day 1 |
| **Custom AI Assistants (Personas)** | **Yes** | — | Tailors responses for specific departments |
| **Python Code Sandbox** | No | **Phase 3** | Requires container sandboxing infrastructure |
| **FastMCP / OpenAPI Actions** | No | **Phase 3** | Advanced capability; RAG takes priority |
| **Slackbot & Discord Bot** | No | **Phase 4** | Web interface is sufficient for initial testing |
| **Multi-Tenant Schema Isolation** | No | **Phase 5** | Single-tenant database covers internal corporate deployments |
| **Stripe Billing & Whitelabeling** | No | **Phase 5** | Commercialization features; not needed for internal utility |

---

## 3. The End-to-End MVP User Journey

1. **Setup**: Administrator launches the application using `docker compose up -d` and navigates to `http://localhost:3000`.
2. **Registration**: First user creates an account and is automatically designated as an `admin`.
3. **Model Key Configuration**: Admin opens `/admin/models` and inputs an OpenAI or Anthropic API key.
4. **Document Ingestion**: Admin or user uploads 10 company policy PDFs via `/admin/documents`.
   - Backend extracts text, creates 512-token chunks, calculates dense vector embeddings, and writes to PostgreSQL `document_chunks`.
5. **Conversational Query**: User asks "What is our travel reimbursement policy for international flights?"
   - System executes a unified PostgreSQL hybrid search (BM25 `tsquery` + vector cosine similarity `<=>`) with Reciprocal Rank Fusion (RRF).
   - Cross-encoder reranks top 5 passages.
   - LLM streams the answer with inline citation `[[1]]`.
6. **Verification**: User clicks citation `[[1]]`; a side drawer opens showing the exact page and paragraph from the source PDF.

---

## 4. Simplified MVP Infrastructure Topology

By removing OpenSearch and leveraging PostgreSQL for both relational records and vector/keyword search, the MVP topology is exceptionally lean:

```
[ Nginx Reverse Proxy (Ports 80/443) ]
       │
       ├──> [ Next.js Web Frontend (Port 3000) ]
       │
       └──> [ FastAPI Backend (Port 8080) ]
                 │
                 ├──> [ PostgreSQL 16 + pgvector (Port 5432) ]
                 │         ├── Relational Tables (Users, Sessions, Documents)
                 │         └── document_chunks (HNSW Vector + FTS GIN Indexes)
                 │
                 ├──> [ Redis 7 (Port 6379) - Session Cache & Rate Limiting ]
                 └──> [ External LLMs (OpenAI / Anthropic APIs) ]
```

### Revised Hardware Sizing for MVP:
- **2–4 vCPUs**
- **8 GB RAM** *(Reduced from 16 GB; eliminating OpenSearch cuts 4–8 GB JVM heap footprint)*
- **50 GB SSD storage**

---

## 5. Success Metrics for MVP
- **Setup Time**: An engineer can spin up the full stack from repository clone to working chat in **under 10 minutes**.
- **Time to First Token (TTFT)**: Stream begins rendering in the UI in **< 800 ms**.
- **Retrieval Precision**: The correct document is present in the top 3 citations for **> 90%** of direct factual queries.
- **Resource Footprint**: Idle memory consumption of the entire stack is **< 3.5 GB**.
