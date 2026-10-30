# Actionable Development Roadmap & Sprint Plan

This document converts the architectural blueprint into an actionable engineering delivery plan across 5 execution phases, reflecting the **PostgreSQL 16+ with `pgvector` and Full-Text Search (FTS)** search architecture.

---

## 1. Master Delivery Timeline

```mermaid
gantt
    title Actionable Rebuild Engineering Plan
    dateFormat  YYYY-MM-DD
    section Phase 1: MVP (Postgres + pgvector)
    Sprint 1: Base Arch, DB & Auth        :p1_1, 2026-11-01, 14d
    Sprint 2: File Ingestion & pgvector   :p1_2, after p1_1, 14d
    Sprint 3: LiteLLM & Chat SSE Engine   :p1_3, after p1_2, 14d
    Sprint 4: Chat UI & Inline Citations  :p1_4, after p1_3, 14d

    section Phase 2: Connectors
    Sprint 5: Celery & Credential Security:p2_1, after p1_4, 14d
    Sprint 6: Google Drive & Confluence   :p2_2, after p2_1, 14d
    Sprint 7: Slack & GitHub Connectors   :p2_3, after p2_2, 14d
    Sprint 8: Document Sets & Pruning     :p2_4, after p2_3, 14d

    section Phase 3: Agents & Tools
    Sprint 9: Custom Personas Engine      :p3_1, after p2_4, 14d
    Sprint 10: FastMCP & OpenAPI Actions  :p3_2, after p3_1, 14d
    Sprint 11: Python Code Interpreter    :p3_3, after p3_2, 14d
    Sprint 12: Web Search & Deep Research :p3_4, after p3_3, 14d

    section Phase 4: Workplace Bots
    Sprint 13: Slackbot & Discord Bot     :p4_1, after p3_4, 14d
    Sprint 14: Usage Dashboards & Auditing:p4_2, after p4_1, 14d

    section Phase 5: Enterprise
    Sprint 15: SAML 2.0 & OIDC SSO        :p5_1, after p4_2, 14d
    Sprint 16: Upstream Permission Sync   :p5_2, after p5_1, 14d
    Sprint 17: Multi-Tenant Schema Engine :p5_3, after p5_2, 14d
    Sprint 18: Whitelabeling & Billing    :p5_4, after p5_3, 14d
```

---

## 2. Phase 1: The Minimum Viable Product (MVP) (Sprints 1–4)

### Sprint 1: Base Architecture, Database & Authentication
- **Objectives**: Set up core monorepo, PostgreSQL models, Alembic migrations with `vector` extension, and local JWT authentication.
- **Components to Build**:
  - Backend: `main.py`, `core/database.py`, `api/routers/auth.py`, `models/user.py`
  - Frontend: `web/src/app/(auth)/login/`, `web/src/app/(auth)/signup/`
- **Dependencies**: Docker Compose (`postgres:16-pgvector`, `redis`).
- **Deliverables**: Working login/signup flow issuing secure HTTP-only cookies; health audit endpoints.
- **Acceptance Criteria**:
  - User can register, log in, and fetch `/api/users/me`.
  - Database schema applies cleanly via `alembic upgrade head`, enabling `pgvector`.
- **Risks**: JWT secret misconfiguration; mitigated by mandatory startup env validation.

---

### Sprint 2: Document Ingestion, Chunking & PostgreSQL Hybrid Retrieval
- **Objectives**: Extract text from uploaded PDFs/DOCX, split into semantic chunks, generate embeddings, and store them directly in PostgreSQL `document_chunks` with `tsv_content` and `embedding` HNSW indexes. Implement the `SearchProvider` interface with `PgVectorSearchProvider`.
- **Components to Build**:
  - Backend: `indexing/extractor.py`, `indexing/chunker.py`, `indexing/embedder.py`, `retrieval/interface.py`, `retrieval/postgres/provider.py`
- **Dependencies**: Sprint 1 authentication.
- **Deliverables**: `POST /api/manage/document/upload` parses files, saves chunks, and creates vector embeddings in PostgreSQL.
- **Acceptance Criteria**:
  - Uploading a 50-page PDF yields ~200 chunks stored in `document_chunks` within 3 seconds.
  - Hybrid query executes in a single SQL CTE with RRF scoring in < 50 ms.
- **Risks**: HNSW index build memory; mitigated by configuring appropriate PostgreSQL `maintenance_work_mem`.

---

### Sprint 3: LiteLLM Gateway & Streaming Chat Engine
- **Objectives**: Connect external LLMs (OpenAI, Anthropic) and build the Server-Sent Events (SSE) streaming engine.
- **Components to Build**:
  - Backend: `services/llm_service.py`, `services/chat_service.py`, `retrieval/citations.py`, `api/routers/chat.py`
- **Dependencies**: Sprint 2 hybrid retrieval.
- **Deliverables**: `POST /api/chat/send-message` streams real-time tokens and emits structured citation packets.
- **Acceptance Criteria**:
  - First token latency is < 800 ms.
  - Queries retrieve top chunks from PostgreSQL and cite them with verifiable document IDs.
- **Risks**: Token streaming timeouts; mitigated by keep-alive SSE comment pulses.

---

### Sprint 4: Chat UI & Citation Display (MVP Completion)
- **Objectives**: Complete the React 19 chat interface with markdown rendering, live token streaming, and clickable citation badges.
- **Components to Build**:
  - Frontend: `web/src/app/(chat)/app/page.tsx`, `components/chat/ChatMessage.tsx`, `hooks/useChatStream.ts`
- **Dependencies**: Sprint 3 streaming API.
- **Deliverables**: End-to-end working MVP chat workbench with zero external OpenSearch dependency.
- **Acceptance Criteria**:
  - User uploads a company PDF, asks a question, watches the answer stream in real time, and clicks citations to view the exact excerpt.
- **Risks**: Hydration mismatch in React 19; mitigated by strict client component boundaries.

---

## 3. Phase 2: Live Workplace Connectors (Sprints 5–8)

### Sprint 5: Celery Workers & Credential Security
- **Objectives**: Configure Celery distributed task queues and AES-GCM 256 credential encryption.
- **Deliverables**: Background worker consuming `ingestion` and `connectors` queues; encrypted credential store.

### Sprint 6: Google Drive & Confluence Connectors
- **Objectives**: Implement automated polling for Google Drive files and Confluence wiki spaces.
- **Deliverables**: Incremental synchronization updating PostgreSQL `document_chunks` every 15 minutes.

### Sprint 7: Slack & GitHub Connectors
- **Objectives**: Index Slack channels/threads and GitHub repository code/issues.
- **Deliverables**: Full text and vector search across real-time workplace conversations.

### Sprint 8: Document Sets & Background Pruning
- **Objectives**: Allow admins to curate document sets; Celery task removes deleted documents transactionally from PostgreSQL.
- **Deliverables**: Scoped search filters and zero orphaned chunks.

---

## 4. Phase 3: Autonomous Agents & Tool Calling (Sprints 9–12)

### Sprint 9: Custom AI Personas
- **Objectives**: Assistant creation UI with system prompt editor, attached document sets, and model selection.
- **Deliverables**: Assistant switcher in chat header.

### Sprint 10: FastMCP & OpenAPI Tool Actions
- **Objectives**: FastMCP client discovering external tools; OpenAPI JSON upload generating dynamic tools.
- **Deliverables**: LLM invokes external tools during reasoning turns.

### Sprint 11: Python Code Interpreter Sandbox
- **Objectives**: Isolated container runner executing Python scripts, capturing stdout, and displaying charts.
- **Deliverables**: Inline matplotlib chart rendering in chat messages.

### Sprint 12: Live Web Search & Deep Research
- **Objectives**: SearXNG / Tavily web search integration and multi-turn autonomous deep research loop.
- **Deliverables**: Structured, multi-page deep research reports with web sources.

---

## 5. Phase 4: Workplace Bots & Dashboards (Sprints 13–14)

### Sprint 13: Slackbot & Discord Bot
- **Objectives**: Auto-responding bots in team channels and threads with citation blocks.
- **Deliverables**: Verified workplace bot integration.

### Sprint 14: Administration & Cost Analytics
- **Objectives**: Token spend dashboard, model usage breakdown, and user query satisfaction ratings.
- **Deliverables**: Admin analytics console with interactive charts.

---

## 6. Phase 5: Enterprise Hardening & Scale (Sprints 15–18)

### Sprint 15: SAML 2.0 & OIDC Enterprise SSO
- **Objectives**: Okta, OneLogin, and Microsoft Entra ID SSO integration.
- **Deliverables**: Seamless enterprise single sign-on with automatic group mapping.

### Sprint 16: Upstream Permission Sync
- **Objectives**: Background synchronization of Google Drive and Confluence ACLs into `document_chunks.access_control_list`.
- **Deliverables**: Strict inherited document permission filtering.

### Sprint 17: Multi-Tenant Schema Engine & Search Scale Audit
- **Objectives**: Audit PostgreSQL + pgvector latency and evaluate migration triggers (chunk volume > 2M).
- **Deliverables**: Validated schema isolation; optional OpenSearch provider ready if volume exceeds thresholds.

### Sprint 18: Whitelabeling & Commercial Billing
- **Objectives**: Custom tenant branding (logo, colors, domains) and Stripe subscription billing.
- **Deliverables**: Turnkey enterprise SaaS deployment.
