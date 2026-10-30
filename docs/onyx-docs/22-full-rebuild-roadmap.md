# Full Application Rebuild Roadmap (17 Stages)

This blueprint outlines a step-by-step roadmap for rebuilding an enterprise-grade AI knowledge and search platform with capabilities equivalent to Onyx.

---

## Stage 1: Core Foundation & Microservice Architecture

- **Features to Implement**:
  - FastAPI application skeleton with async lifespan management.
  - Next.js 16 App Router shell with API proxy route (`/api/[...path]`).
  - PostgreSQL dual-engine setup (Sync `psycopg2` + Async `asyncpg`).
  - Redis connection pool for caching and locking.
  - Sentry exception tracking and structured logging.
- **Backend Components**: `backend/onyx/main.py`, `backend/onyx/db/engine/`, `backend/onyx/redis/`
- **Frontend Components**: `web/src/app/layout.tsx`, `web/src/app/api/[...path]/route.ts`, `web/src/proxy.ts`
- **Database Models & Migrations**: Initial Alembic setup with base schema.
- **APIs & Services**: `GET /api/health`, `GET /api/version`
- **Dependencies**: Docker Compose (`postgres`, `redis`).
- **Security Considerations**: CORS origin lockdown, HTTP-only cookie configuration, secure header injection (CSP).
- **Complexity**: **Medium**
- **Definition of Done**: FastAPI and Next.js communicate through the internal reverse proxy; database connection pools initialize and pass health audits.

---

## Stage 2: Authentication, Organizations & RBAC

- **Features to Implement**:
  - Local email/password registration with bcrypt hashing.
  - HTTP-only signed JWT session cookies (`fastapiusersauth`).
  - Role-Based Access Control (`admin`, `curator`, `global_curator`, `basic`).
  - Personal Access Tokens (PAT) and API Keys for developers.
- **Backend Components**: `backend/onyx/auth/users.py`, `backend/onyx/auth/permissions.py`, `backend/onyx/server/api_key/`
- **Frontend Components**: `web/src/app/auth/login/`, `web/src/app/auth/signup/`, `web/src/components/auth/`
- **Database Models**: `User`, `ApiKey`, `OAuthAccount`
- **APIs & Services**: `/api/auth/register`, `/api/auth/jwt/login`, `/api/users/me`, `/api/api-key`
- **Security Considerations**: Rate-limiting login attempts via Redis, brute-force protection, password strength enforcement.
- **Complexity**: **Medium**
- **Definition of Done**: Users can register, log in, receive an HTTP-only JWT cookie, and access role-gated routes.

---

## Stage 3: Document Management & Ingestion Engine

- **Features to Implement**:
  - Asynchronous file extraction for PDFs, DOCX, PPTX, HTML, and Markdown.
  - Semantic token-aware chunker (512 tokens with 48 overlap and prepended title metadata).
  - OpenSearch cluster client and schema setup (`danswer_chunk` index).
  - Local PyTorch model server or cloud embedding engine.
- **Backend Components**: `backend/onyx/file_processing/`, `backend/onyx/indexing/chunker.py`, `backend/onyx/indexing/embedder.py`, `backend/onyx/document_index/opensearch/`
- **Frontend Components**: `web/src/components/admin/FileUpload.tsx`
- **Database Models**: `Document`, `IndexAttempt`
- **APIs & Services**: `/api/manage/document/upload`, `/api/manage/document/indexing-status`
- **Security Considerations**: File upload virus scanning, file extension allowlists, size limits (max 50 MB).
- **Complexity**: **High**
- **Definition of Done**: Uploaded PDF is extracted, chunked, embedded with float vectors, and stored in OpenSearch within 5 seconds.

---

## Stage 4: Connectors & Asynchronous Synchronization

- **Features to Implement**:
  - Connector framework (`BaseConnector`, `PollConnector`, `LoadConnector`).
  - Celery background worker queues (`indexing`, `docfetching`, `pruning`).
  - AES-GCM 256-bit encrypted credential store.
  - Top 5 foundational connectors: Google Drive, Slack, GitHub, Confluence, and Web Crawler.
  - Celery Beat periodic synchronization schedule.
- **Backend Components**: `backend/onyx/connectors/`, `backend/onyx/db/credentials.py`, `backend/onyx/background/celery/`
- **Frontend Components**: `web/src/app/admin/connectors/`
- **Database Models**: `Connector`, `Credential`, `ConnectorCredentialPair` (`cc_pair`)
- **APIs & Services**: `/api/manage/connector`, `/api/manage/credential`, `/api/manage/connector-credential-pair`
- **Security Considerations**: Zero plaintext credential storage; OAuth token automatic refresh cycles.
- **Complexity**: **Very High**
- **Definition of Done**: Admin configures Google Drive; background worker crawls folders incrementally and updates OpenSearch automatically.

---

## Stage 5: Hybrid Search & RAG Retrieval Pipeline

- **Features to Implement**:
  - OpenSearch hybrid query executor (BM25 keyword search + k-NN dense vector cosine similarity).
  - Reciprocal Rank Fusion (RRF) score normalization.
  - Mandatory user/group access control list (ACL) filter injection.
  - Cross-encoder reranking microservice (`inference_model_server`).
  - Curated Document Sets for scoped searching.
- **Backend Components**: `backend/onyx/document_index/opensearch/opensearch_client.py`, `backend/onyx/natural_language_processing/`
- **Frontend Components**: `web/src/app/app/search/`, `web/src/components/search/`
- **Database Models**: `DocumentSet`, `DocumentSetConnectorCredentialPair`
- **APIs & Services**: `/api/search/hybrid-search`, `/api/document-set`
- **Security Considerations**: Strict enforcement of ACL filter clauses preventing cross-tenant or unauthorized chunk exposure.
- **Complexity**: **High**
- **Definition of Done**: Natural language query returns top 5 relevant passages scored by the cross-encoder, respecting user permissions.

---

## Stage 6: Chat Interface & Conversation Management

- **Features to Implement**:
  - Full-featured chat UI with real-time SSE streaming.
  - Server-Sent Events line decoder handling `text`, `citation`, `tool_call`, and `metadata` packets.
  - Inline citation processor mapping `[[1]]` markers to document highlights.
  - Conversation persistence, branching tree forks, thread renaming, and folder organization.
- **Backend Components**: `backend/onyx/server/query_and_chat/chat_backend.py`, `backend/onyx/chat/process_message.py`, `backend/onyx/chat/citation_processor.py`
- **Frontend Components**: `web/src/app/app/page.tsx`, `web/src/components/chat/`, `web/src/hooks/useChatStream.ts`
- **Database Models**: `ChatSession`, `ChatMessage`, `ChatFolder`, `ChatFeedback`
- **APIs & Services**: `/api/chat/send-message`, `/api/chat/create-chat-session`, `/api/chat/get-chat-session/{id}`
- **Complexity**: **High**
- **Definition of Done**: User types a question, watches answer stream with live typing effect, and clicks citation pills to view source docs.

---

## Stage 7: LLM Provider Integrations & Cost Tracking

- **Features to Implement**:
  - LiteLLM multi-provider gateway.
  - Dynamic model catalog with context limits and capability discovery.
  - Prompt caching support (Anthropic / OpenAI).
  - Token consumption and dollar cost accounting ledger.
- **Backend Components**: `backend/onyx/llm/multi_llm.py`, `backend/onyx/llm/cost.py`, `backend/onyx/llm/model_catalog.py`
- **Frontend Components**: `web/src/app/admin/models/`, `web/src/components/chat/ModelSelector.tsx`
- **Database Models**: `LLMProvider`, `LLMUsage`
- **APIs & Services**: `/api/admin/llm/provider`, `/api/llm/models`
- **Complexity**: **Medium**
- **Definition of Done**: Admin configures OpenAI and Anthropic API keys; users switch models in chat; costs log to database.

---

## Stage 8: AI Agents (Personas) & Tool Execution Framework

- **Features to Implement**:
  - Custom AI Persona creator (system instructions, tool attachments, document sets).
  - Tool execution runner with JSON Schema translation.
  - Streamed tool argument feedback to UI ("Searching documents...").
- **Backend Components**: `backend/onyx/server/features/persona/`, `backend/onyx/tools/tool_runner.py`, `backend/onyx/tools/tool_constructor.py`
- **Frontend Components**: `web/src/app/admin/personas/`, `web/src/components/chat/PersonaSelector.tsx`
- **Database Models**: `Persona`, `Prompt`, `Tool`
- **APIs & Services**: `/api/persona`, `/api/admin/persona`, `/api/tool`
- **Complexity**: **High**
- **Definition of Done**: Custom assistant executes search tool, inspects results, and generates tailored answers.

---

## Stage 9: MCP (Model Context Protocol) & OpenAPI Tools

- **Features to Implement**:
  - FastMCP client connector (stdio and SSE transports).
  - Dynamic tool schema ingestion from external MCP servers.
  - OpenAPI 3.0 / Swagger JSON parser generating typed tool schemas.
- **Backend Components**: `backend/onyx/tools/tool_implementations/mcp/`, `backend/onyx/tools/tool_implementations/custom/`
- **Frontend Components**: `web/src/app/admin/mcp/`, `web/src/app/admin/tools/`
- **Database Models**: `MCPServer`, `Tool`
- **APIs & Services**: `/api/admin/mcp`, `/api/admin/tool/custom`
- **Complexity**: **High**
- **Definition of Done**: External FastMCP server connects to Onyx; LLM invokes MCP tools during chat conversations.

---

## Stage 10: Live Web Search & Deep Research

- **Features to Implement**:
  - Web search tool integrating SearXNG, Tavily, and Bing Search.
  - Deep Research autonomous agent executing iterative query loops, evaluating content, and generating structured reports.
- **Backend Components**: `backend/onyx/tools/tool_implementations/web_search/`, `backend/onyx/deep_research/`
- **Frontend Components**: `web/src/components/chat/DeepResearchIndicator.tsx`
- **APIs & Services**: `/api/web-search/test`, `/api/deep-research/start`
- **Complexity**: **High**
- **Definition of Done**: User triggers Deep Research; agent executes 4 sub-queries across web and internal docs, compiling a verified brief.

---

## Stage 11: Python Code Interpreter & Image Generation

- **Features to Implement**:
  - Sandboxed Python code runner container.
  - Standard output, error, and chart image (PNG/SVG) capture.
  - DALL-E 3 and Google Imagen tool integrations.
- **Backend Components**: `backend/onyx/tools/tool_implementations/python/`, `backend/onyx/image_gen/`
- **Frontend Components**: `web/src/components/chat/ChartRenderer.tsx`
- **Complexity**: **Medium**
- **Definition of Done**: Agent writes Python script to plot quarterly data; chat renders the resulting PNG chart inline.

---

## Stage 12: Slack & Discord Bots

- **Features to Implement**:
  - Webhook listener verifying Slack and Discord request signatures.
  - Background Celery task processing mentions and generating replies with citations.
  - Slack block kit formatting with feedback buttons.
- **Backend Components**: `backend/onyx/onyxbot/slack/`, `backend/onyx/onyxbot/discord/`
- **Frontend Components**: `web/src/app/admin/bot/`
- **Database Models**: `SlackBotConfig`, `SlackChannelConfig`
- **Complexity**: **Medium**
- **Definition of Done**: User @mentions bot in Slack channel; bot replies in thread with cited answer within 8 seconds.

---

## Stage 13: Administration & Usage Analytics

- **Features to Implement**:
  - Admin dashboard displaying token volume, active users, and latency.
  - Search quality metrics (click-through rates, upvote/downvote ratios).
  - User and group management with curator delegations.
- **Backend Components**: `backend/onyx/server/features/usage/`, `backend/onyx/server/manage/`
- **Frontend Components**: `web/src/app/admin/analytics/`, `web/src/app/admin/users/`
- **Complexity**: **Medium**
- **Definition of Done**: Admins inspect 30-day token spend charts and view query satisfaction metrics.

---

## Stage 14: Enterprise Security, SAML 2.0 & OIDC SSO

- **Features to Implement**:
  - SAML 2.0 Identity Provider integration (Okta, OneLogin, PingIdentity).
  - Multi-tenant OIDC discovery.
  - Automated IdP group-to-Onyx-group attribute mapping.
- **Backend Components**: `backend/onyx/server/saml_multi.py`, `backend/onyx/server/oidc_multi.py`
- **Frontend Components**: `web/src/app/auth/sso/`
- **Database Models**: `SamlProvider`, `UserGroup`
- **Complexity**: **High**
- **Definition of Done**: Enterprise employee logs in via Okta SAML; user account is provisioned with appropriate group roles.

---

## Stage 15: Upstream Permission Sync & Multi-Tenancy

- **Features to Implement**:
  - Automated background sync of file permissions from Google Drive and Confluence.
  - PostgreSQL multi-tenant schema isolation (`tenant_<uuid>`) via `alembic_tenants`.
- **Backend Components**: `backend/ee/onyx/external_permissions/`, `backend/alembic_tenants/`
- **Database Models**: `DocumentAccess`, `Tenant`
- **Complexity**: **Very High**
- **Definition of Done**: Restricting a file in Google Drive automatically removes it from unauthorized employees' Onyx search results within 10 minutes.

---

## Stage 16: Whitelabeling, Custom Themes & Billing

- **Features to Implement**:
  - Admin panel custom branding (logo, application title, primary color tokens).
  - Stripe subscription checkout and seat-based licensing enforcement.
- **Backend Components**: `backend/ee/onyx/server/whitelabeling/`, `backend/ee/onyx/server/billing/`
- **Frontend Components**: `web/src/ee/admin/whitelabeling/`, `web/src/ee/admin/billing/`
- **Complexity**: **Medium**
- **Definition of Done**: Admin uploads company logo; web UI theme updates instantly across all user sessions.

---

## Stage 17: Production Deployment, Monitoring & Scaling

- **Features to Implement**:
  - Automated Docker Compose production manifests with Let's Encrypt SSL.
  - Kubernetes Helm chart with Horizontal Pod Autoscalers (HPA).
  - OpenTelemetry and Prometheus metrics export.
- **Backend Components**: `backend/onyx/server/metrics/`, `deployment/helm/`, `deployment/docker_compose/`
- **Complexity**: **High**
- **Definition of Done**: Full multi-node stack deploys via Helm on AWS EKS with auto-scaling API pods.

