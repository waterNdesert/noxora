# Actionable Development Roadmap & Sprint Plan

The roadmap lists 19 sequential 14-day sprints (approximately 38 weeks of sprint time, excluding gaps). This is a sequence estimate, not a delivery commitment. Re-estimate dates and staffing before treating it as one.

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

    Sprint 5: Google & GitHub OAuth       :p1_5, after p1_4, 14d

    section Phase 2: Connectors
    Sprint 6: Connector Credential Security:p2_1, after p1_5, 14d
    Sprint 7: Google Drive & Confluence   :p2_2, after p2_1, 14d
    Sprint 8: Slack & GitHub Connectors   :p2_3, after p2_2, 14d
    Sprint 9: Document Sets & Pruning     :p2_4, after p2_3, 14d

    section Phase 3: Agents & Tools
    Sprint 10: Custom Personas Engine     :p3_1, after p2_4, 14d
    Sprint 11: FastMCP & OpenAPI Actions  :p3_2, after p3_1, 14d
    Sprint 12: Python Code Interpreter    :p3_3, after p3_2, 14d
    Sprint 13: Web Search & Deep Research:p3_4, after p3_3, 14d

    section Phase 4: Workplace Bots
    Sprint 14: Slackbot & Discord Bot     :p4_1, after p3_4, 14d
    Sprint 15: Usage Dashboards & Auditing:p4_2, after p4_1, 14d

    section Phase 5: Enterprise
    Sprint 16: SAML 2.0 & OIDC SSO        :p5_1, after p4_2, 14d
    Sprint 17: Upstream Permission Sync   :p5_2, after p5_1, 14d
    Sprint 18: Multi-Tenant Isolation     :p5_3, after p5_2, 14d
    Sprint 19: Whitelabeling & Billing    :p5_4, after p5_3, 14d
```

---

## 2. Phase 1: The Minimum Viable Product (MVP) (Sprints 1–5)

### Sprint 1: Base Architecture, Database & Authentication
- **Objectives**: Set up the core application, PostgreSQL/Alembic foundation, and opaque server-side local authentication.
- **Components to Build**:
  - Backend: `backend/src/main.py`, `backend/src/core/database.py`, `backend/src/api/routers/auth.py`, `backend/src/models/user.py`
  - Frontend: `web/src/app/(auth)/login/`
- **Dependencies**: PostgreSQL 16+ with pgvector available. Redis is not a Sprint 1 dependency.
- **Deliverables**: One-time initial-administrator setup command, local login/logout, an authenticated `/api/users/me` endpoint, and health/readiness endpoints. Browser API routes use the same-origin reverse proxy.
- **Acceptance Criteria**:
  - Initial administrator can be provisioned once, log in, log out, and fetch `/api/users/me`; subsequent account-provisioning policy remains open.
  - Database schema applies cleanly via `alembic upgrade head`, enabling `pgvector`.
- **Risks**: Missing or insecure session configuration; validate only required settings at startup. Passwords use Argon2id; session secrets are stored only as hashes.

---

### Sprint 2: Asynchronous Document Ingestion & PostgreSQL Hybrid Retrieval
- **Objectives**: Implement upload and job creation, store original files in the selected object store, and use Celery/Redis for background extraction, cleaning, chunking, embedding, and persistence. Provide processing status, failure reporting, and retries. Implement the `SearchProvider` interface with `PgVectorSearchProvider`.
- **Components to Build**:
  - Backend: upload/job handling, object-storage integration, ingestion worker, extraction/cleaning, chunking, embedding, processing status, `retrieval/interface.py`, and `retrieval/postgres/provider.py`
- **Dependencies**: Sprint 1 authentication. Choose and document the embedding provider, model, dimension, and versioning strategy before creating the embedding schema.
- **Deliverables**: An authorized upload creates a processing job; worker results and failures are visible; searchable content is stored in PostgreSQL.
- **Acceptance Criteria**:
  - Upload processing completes asynchronously and reports status, errors, and retry outcomes.
  - Hybrid retrieval has a measured baseline using a defined corpus and workload; no unbenchmarked latency guarantee is assumed.
- **Risks**: HNSW index build memory; evaluate resource settings against the selected model, corpus, and deployment before adopting them.

---

### Sprint 3: LiteLLM Gateway & Streaming Chat Engine
- **Objectives**: Connect external LLMs (OpenAI, Anthropic) and build the Server-Sent Events (SSE) streaming engine.
- **Components to Build**:
  - Backend: `services/llm_service.py`, `services/chat_service.py`, `retrieval/citations.py`, `api/routers/chat.py`
- **Dependencies**: Sprint 2 hybrid retrieval.
- **Deliverables**: `POST /api/chat/send-message` streams real-time tokens and emits structured citation packets.
- **Acceptance Criteria**:
  - Measure first-token latency under a documented workload; the existing < 800 ms figure is a provisional goal, not a guaranteed acceptance threshold.
  - Queries retrieve top chunks from PostgreSQL and cite them with verifiable document IDs.
- **Risks**: Token streaming timeouts; mitigated by keep-alive SSE comment pulses.

---

### Sprint 4: Chat UI & Citation Display
- **Objectives**: Complete the React 19 chat interface with markdown rendering, live token streaming, and clickable citation badges.
- **Components to Build**:
  - Frontend: `web/src/app/(chat)/app/page.tsx`, `components/chat/ChatMessage.tsx`, `hooks/useChatStream.ts`
- **Dependencies**: Sprint 3 streaming API.
- **Deliverables**: End-to-end working chat workbench with zero external OpenSearch dependency.
- **Acceptance Criteria**:
  - User uploads a company PDF, asks a question, watches the answer stream in real time, and clicks citations to view the exact excerpt.
- **Risks**: Hydration mismatch in React 19; mitigated by strict client component boundaries.

---

### Sprint 5: Google and GitHub OAuth
- **Planning rationale**: Keep OAuth in the MVP but give it a dedicated sprint after the first-party session foundation and chat UI/citations. Adding provider callbacks, identity resolution, and account-linking behavior to the UI/citations sprint would combine separate objectives.
- **Objectives**: Add Google and GitHub OAuth sign-in to the existing first-party opaque-session model.
- **Dependencies**: Sprint 1 session authentication and account-provisioning policy.
- **Deliverables**: OAuth authentication flows for both providers that establish the same server-side session used by local authentication and follow the approved account-creation/linking policy.
- **Acceptance Criteria**:
  - Both providers complete the approved authentication flow and resolve the corresponding Nexora account according to the policy decided before implementation.
  - OAuth state/callback validation and account-creation/linking behavior are explicitly specified and tested.
- **Open prerequisite**: Decide whether OAuth may create accounts, how account linking and verified-email handling work, and what happens when an OAuth identity has no usable email.

## 3. Phase 2: Live Workplace Connectors (Sprints 6–9)

### Sprint 6: Connector Credential Security
- **Objectives**: Extend the existing Celery/Redis ingestion worker foundation for connector workloads and implement approved AES-GCM 256 connector-credential encryption.
- **Deliverables**: Connector task workload and encrypted connector credential storage. This sprint does not introduce provider API-key persistence.

### Sprint 7: Google Drive & Confluence Connectors
- **Objectives**: Implement automated polling for Google Drive files and Confluence wiki spaces.
- **Deliverables**: Incremental synchronization updating PostgreSQL `document_chunks` every 15 minutes.

### Sprint 8: Slack & GitHub Connectors
- **Objectives**: Index Slack channels/threads and GitHub repository code/issues.
- **Deliverables**: Full text and vector search across real-time workplace conversations.

### Sprint 9: Document Sets & Background Pruning
- **Objectives**: Allow admins to curate document sets; Celery task removes deleted documents transactionally from PostgreSQL.
- **Deliverables**: Scoped search filters and zero orphaned chunks.

---

## 4. Phase 3: Autonomous Agents & Tool Calling (Sprints 10–13)

### Sprint 10: Custom AI Personas
- **Objectives**: Assistant creation UI with system prompt editor, attached document sets, and model selection.
- **Deliverables**: Assistant switcher in chat header.

### Sprint 11: FastMCP & OpenAPI Tool Actions
- **Objectives**: FastMCP client discovering external tools; OpenAPI JSON upload generating dynamic tools.
- **Deliverables**: LLM invokes external tools during reasoning turns.

### Sprint 12: Python Code Interpreter Sandbox
- **Objectives**: Isolated container runner executing Python scripts, capturing stdout, and displaying charts.
- **Deliverables**: Inline matplotlib chart rendering in chat messages.

### Sprint 13: Live Web Search & Deep Research
- **Objectives**: SearXNG / Tavily web search integration and multi-turn autonomous deep research loop.
- **Deliverables**: Structured, multi-page deep research reports with web sources.

---

## 5. Phase 4: Workplace Bots & Dashboards (Sprints 14–15)

### Sprint 14: Slackbot & Discord Bot
- **Objectives**: Auto-responding bots in team channels and threads with citation blocks.
- **Deliverables**: Verified workplace bot integration.

### Sprint 15: Administration & Cost Analytics
- **Objectives**: Token spend dashboard, model usage breakdown, and user query satisfaction ratings.
- **Deliverables**: Admin analytics console with interactive charts.

---

## 6. Phase 5: Enterprise Hardening & Scale (Sprints 16–19)

### Sprint 16: SAML 2.0 & OIDC Enterprise SSO
- **Objectives**: Okta, OneLogin, and Microsoft Entra ID SSO integration.
- **Deliverables**: Seamless enterprise single sign-on with automatic group mapping.

### Sprint 17: Upstream Permission Sync
- **Objectives**: Background synchronization of Google Drive and Confluence ACLs into `document_chunks.access_control_list`.
- **Deliverables**: Strict inherited document permission filtering.

### Sprint 18: Multi-Tenant Isolation & Search Scale Audit
- **Objectives**: Design and validate the approved enterprise tenant-isolation model; measure PostgreSQL + pgvector behavior and evaluate whether the proposed search-provider migration triggers are met.
- **Deliverables**: Tenant isolation is implemented and security-tested only after its full RLS/context/pool design is approved; search migration remains a separately approved decision.

### Sprint 19: Whitelabeling & Commercial Billing
- **Objectives**: Custom tenant branding (logo, colors, domains) and Stripe subscription billing.
- **Deliverables**: Turnkey enterprise SaaS deployment.
