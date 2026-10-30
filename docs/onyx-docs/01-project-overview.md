# Onyx Codebase Overview

## 1. What is Onyx?

**Onyx** (formerly known as *Danswer*) is an open-source, enterprise-grade AI chat and unified knowledge search platform. It connects directly to internal workplace applications and knowledge repositories (Google Drive, Confluence, Slack, GitHub, Jira, Notion, Salesforce, web crawls, and 40+ other data sources), continuously indexes their content, and enables users to query that knowledge using natural language.

Beyond standard question-answering and search, Onyx serves as an **agentic AI workbench**:
- **Enterprise Search**: Hybrid keyword (BM25) and vector (dense semantic embedding) retrieval across all company documents with granular access control lists (ACLs).
- **RAG & Agent Execution**: Retrieval-Augmented Generation that injects relevant chunks into state-of-the-art LLMs, while supporting tool calling, multi-step sub-agents, live web search, Python code execution, and Model Context Protocol (MCP) tool invocation.
- **Bot Integrations**: First-class Slackbot and Discord bot support for answering questions directly in channels, threads, or direct messages.
- **Extensible Connector Architecture**: Plug-and-play connectors that handle pagination, rate limiting, incremental syncs, and document permission inheritance.

---

## 2. Editions & Licensing

Onyx operates under a dual-tier codebase structure:

```
┌────────────────────────────────────────────────────────┐
│                   Onyx Platform                        │
├────────────────────────────┬───────────────────────────┤
│  Community Edition (CE)    │  Enterprise Edition (EE)  │
│  License: MIT              │  License: Proprietary     │
│  Location: `backend/onyx/` │  Location: `backend/ee/`  │
│            `web/src/`      │            `web/src/ee/`  │
└────────────────────────────┴───────────────────────────┘
```

1. **Community Edition (CE)**:
   - Licensed under MIT.
   - Core search, indexing, standard chat, RAG, open-source connectors, basic OAuth/local authentication, and single-tenant deployments.
   - Resides in `backend/onyx/` and standard frontend components in `web/src/`.
2. **Enterprise Edition (EE)**:
   - Licensed under proprietary commercial terms.
   - Multi-tenancy, enterprise SSO (SAML 2.0, multi-tenant OIDC), automated Document Access Permission Synchronization from upstream providers (e.g., Google Drive / Confluence ACLs), user groups, audit logging, analytics, rate and token quotas, custom whitelabeling, and advanced billing integration.
   - Resides in `backend/ee/onyx/` and `web/src/ee/`.
   - **Dynamic Feature Gating**: Managed via `backend/onyx/utils/variable_functionality.py` through `fetch_versioned_implementation` and `fetch_ee_implementation_or_noop`. When an enterprise license is present, the application dynamically resolves enterprise implementations; otherwise, it falls back gracefully to CE behavior or no-ops without crashing.

---

## 3. Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend API** | Python 3.13, FastAPI, Pydantic v2, Uvicorn, Starlette |
| **Database & ORM** | PostgreSQL 15+, SQLAlchemy 2.0 (Sync & Async with `asyncpg` / `psycopg2`), Alembic migrations |
| **Background Processing** | Celery 5.x, Celery Beat, Redis (broker & result backend) |
| **Caching & Locks** | Redis 7+ (distributed locks, session tokens, rate limiting) |
| **Search & Retrieval** | OpenSearch 2.x (BM25 keyword search + k-NN dense vector embeddings) |
| **File Storage** | MinIO (S3-compatible object store) or AWS S3 / local filesystem |
| **Inference & Embeddings**| Local Model Server (FastAPI + HuggingFace PyTorch) or Cloud APIs (OpenAI, Cohere, Voyage) |
| **LLM Gateway** | LiteLLM wrapper, multi-provider load balancing, streaming token accounting |
| **Frontend** | Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS, Radix UI, Lucide icons |
| **Protocols** | Server-Sent Events (SSE) for streaming chat, REST API, FastMCP (Model Context Protocol) |
| **Deployment** | Docker Compose, Kubernetes (Helm / Kind), AWS ECS Fargate, Terraform |

---

## 4. Key Architectural Pillars

1. **Stateless API Services**:
   The web server and API servers maintain no in-memory conversational state between requests. Chat sessions, user profiles, document metadata, and tool execution state are committed transactionally to PostgreSQL and cached in Redis.
2. **Dual-Store Architecture (Postgres + OpenSearch)**:
   - **PostgreSQL**: Source of truth for relational data—users, credentials, connectors, chat sessions, message histories, persona definitions, tools, and access control tokens.
   - **OpenSearch**: Search-optimized data plane—stores chunked text, keyword inverted indexes, dense vector embeddings, document set tags, and ACL filter lists.
3. **Decoupled Asynchronous Ingestion**:
   Connecting an external workspace and ingesting hundreds of thousands of documents does not block the user-facing web app. Tasks are partitioned into Celery jobs (`docfetching`, `docprocessing`, `indexing`), run in isolated worker processes, and coordinate status via Redis and PostgreSQL.
4. **Streaming First Chat Loop**:
   Chat responses stream incrementally via Server-Sent Events (SSE) using a standardized JSON packet envelope. This delivers instant token feedback, citations, thought process indicators, and intermediate tool call status to the frontend.

