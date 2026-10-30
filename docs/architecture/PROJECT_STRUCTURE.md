# Target Project Directory Structure

This document outlines the organized monorepo directory layout for the application, featuring a decoupled **Search Provider** interface powered initially by **PostgreSQL + `pgvector`**.

---

## 1. Monorepo Root Layout

```
knowledge-platform/
├── backend/                  # Python FastAPI Backend, Celery Workers, Models
├── web/                      # Next.js 16 (React 19) Web Application
├── services/                 # Auxiliary Microservices (Model Server, Sandbox)
├── shared/                   # Cross-cutting types and API contracts
├── deployment/               # Docker, Kubernetes Helm, Reverse Proxy configs
├── scripts/                  # Developer utilities and database seeding tools
├── .github/                  # CI/CD Workflows (Lint, Test, Docker Build)
├── docker-compose.yml        # Local development manifest (Postgres+pgvector, Redis, Web, API)
├── Makefile                  # Developer CLI commands (build, run, test, migrate)
├── pyproject.toml            # Python dependencies (managed via uv)
└── package.json              # Monorepo and frontend tooling scripts
```

---

## 2. Backend Package Architecture (`backend/`)

```
backend/
├── alembic/                  # Database migration scripts
│   ├── versions/             # Timestamped migration versions (includes pgvector extension)
│   └── env.py                # Alembic environment runner
│
├── src/
│   ├── main.py               # FastAPI application entry point & lifespan manager
│   │
│   ├── api/                  # Presentation Layer: HTTP Routers & Middleware
│   │   ├── dependencies/     # FastAPI Depends: db session, current_user, tenant_context
│   │   ├── middleware/       # Latency logging, rate limiting, request ID, CORS
│   │   ├── routers/          # REST Endpoint Controllers
│   │   │   ├── auth.py       # Login, register, logout, OAuth2, SAML ACS
│   │   │   ├── chat.py       # Conversations, message history, SSE stream endpoint
│   │   │   ├── search.py     # Hybrid search query, intent evaluation, document sets
│   │   │   ├── connectors.py # Connector definitions, credential pairing, sync triggers
│   │   │   ├── personas.py   # AI Assistant creation, prompt editing, tool binding
│   │   │   ├── tools.py      # MCP server registration, OpenAPI custom tools
│   │   │   ├── admin.py      # User management, RBAC assignments, audit exports
│   │   │   └── usage.py      # Token analytics, cost breakdowns, quota monitoring
│   │   └── schemas/          # Pydantic v2 Inbound/Outbound request validation models
│   │
│   ├── core/                 # Foundation: Settings, Security, Database Engines
│   │   ├── config.py         # Pydantic Settings (loads environment variables)
│   │   ├── database.py       # SQLAlchemy engine, connection pools (psycopg2 & asyncpg)
│   │   ├── redis.py          # Redis connection pool, distributed locks, rate limiters
│   │   └── security.py       # JWT creation/verification, password hashing, AES-GCM 256
│   │
│   ├── domain/               # Domain Entities, Interfaces & Core Business Rules
│   │   ├── exceptions.py     # Standardized domain error classes and error codes
│   │   ├── entities/         # Domain models (User, Document, Chunk, Persona, Session)
│   │   └── interfaces/       # Abstract repository and external gateway contracts
│   │
│   ├── services/             # Application Services: Orchestrates Business Workflows
│   │   ├── auth_service.py   # User verification, token refreshing, invite workflows
│   │   ├── chat_service.py   # Prompt assembly, conversational state, SSE event dispatch
│   │   ├── search_service.py # Hybrid search coordination, RRF fusion, reranking
│   │   ├── indexing_service.py # Ingestion coordination, document state tracking
│   │   ├── llm_service.py    # LiteLLM invocation, fallback routing, cost calculation
│   │   └── tool_service.py   # FastMCP discovery, OpenAPI translation, execution runner
│   │
│   ├── connectors/           # Pluggable Workplace Data Source Connectors
│   │   ├── base.py           # Abstract BaseConnector, PollConnector, LoadConnector
│   │   ├── registry.py       # Factory pattern mapping connector type strings to classes
│   │   ├── google_drive/     # Google Drive folder crawler and incremental sync
│   │   ├── slack/            # Slack channels, threads, and user message poller
│   │   ├── confluence/       # Confluence space and page crawler
│   │   ├── github/           # GitHub repository issues, PRs, and documentation
│   │   └── web_crawler/      # Recursive HTML spider and single URL scraper
│   │
│   ├── indexing/             # Ingestion Data Pipeline Components
│   │   ├── extractor.py      # Multi-format text parsing (PDF, DOCX, HTML, Markdown)
│   │   ├── chunker.py        # Token-aware sliding window semantic chunker
│   │   └── embedder.py       # Batch vector generation client (local model or cloud)
│   │
│   ├── retrieval/            # Search & Retrieval Engine (Pluggable Provider Pattern)
│   │   ├── interface.py      # Abstract SearchProvider interface definition
│   │   ├── factory.py        # Resolves active SearchProvider based on environment config
│   │   ├── postgres/         # Default Initial Search Implementation
│   │   │   ├── provider.py   # PgVectorSearchProvider (implements SearchProvider)
│   │   │   ├── fts_builder.py# tsvector full-text query builder & ts_rank_cd scoring
│   │   │   └── rrf.py        # SQL Common Table Expression (CTE) Reciprocal Rank Fusion
│   │   ├── opensearch/       # Future OpenSearch Provider (implements SearchProvider)
│   │   │   └── provider.py   # OpenSearchSearchProvider
│   │   ├── qdrant/           # Future Qdrant Provider (implements SearchProvider)
│   │   │   └── provider.py   # QdrantSearchProvider
│   │   ├── reranker.py       # Cross-encoder rescoring client
│   │   └── citations.py      # Inline citation matching and excerpt extraction
│   │
│   ├── agents/               # Autonomous Agent & Tool Runtime
│   │   ├── llm_loop.py       # Multi-step reasoning loop (Thought -> Action -> Observation)
│   │   ├── mcp_client.py     # FastMCP client over stdio / HTTP/SSE
│   │   └── deep_research.py  # Iterative multi-turn research coordinator
│   │
│   ├── workers/              # Celery Asynchronous Execution
│   │   ├── celery_app.py     # Celery app initialization with Redis broker
│   │   ├── beat_schedule.py  # Periodic cron schedules (connector polls, health audits)
│   │   └── tasks/            # Task implementations partitioned by queue
│   │       ├── ingestion.py  # Batch chunking, embedding, and vector insertion
│   │       ├── fetching.py   # External connector polling runs
│   │       ├── pruning.py    # Deletion synchronization and index cleaning
│   │       └── general.py    # Email sending, export generation, usage aggregation
│   │
│   └── models/               # SQLAlchemy ORM Relational Models
│       ├── base.py           # DeclarativeBase, UUIDPrimaryKey, TimestampMixin, TenantMixin
│       ├── user.py           # User, UserGroup, UserGroupMember, ApiKey
│       ├── tenant.py         # Tenant, TenantSettings, License
│       ├── connector.py      # Connector, Credential, ConnectorCredentialPair, IndexAttempt
│       ├── document.py       # Document, DocumentChunk (pgvector + tsvector), DocumentSet
│       ├── chat.py           # ChatSession, ChatMessage, ChatFolder, ChatFeedback
│       ├── persona.py        # Persona, Prompt, Tool, MCPServer
│       └── usage.py          # LLMUsage, AuditLog
│
└── tests/                    # Backend Test Suites
    ├── unit/                 # Fast, in-memory unit tests
    └── integration/          # Live API, database, and pgvector hybrid retrieval tests
```

---

## 3. Frontend Package Architecture (`web/`)

```
web/
├── public/                   # Static assets (favicons, logos, illustrations)
├── src/
│   ├── app/                  # Next.js App Router Pages & Layouts
│   │   ├── layout.tsx        # Root HTML layout with providers (Theme, Auth, Query)
│   │   ├── page.tsx          # Marketing landing page or redirect to /app
│   │   ├── (auth)/           # Authentication Route Group (login, signup, sso)
│   │   ├── (chat)/           # Core Conversational Experience (/app, /search)
│   │   └── (admin)/          # Administration & Settings Console
│   ├── components/           # Reusable UI Component Library (Radix primitives, chat, search)
│   ├── hooks/                # Custom React Hooks (useChatStream, useAuth, useDebounce)
│   ├── lib/                  # Frontend Core Utilities (api wrapper, SSE decoder, constants)
│   ├── stores/               # Zustand Client State Stores (chatStore, uiStore)
│   └── types/                # TypeScript Interfaces & API Response Contracts
└── tailwind.config.js        # Design tokens and theme styling
```

---

## 4. Auxiliary Services (`services/`)

```
services/
├── model-server/             # Dedicated Python Inference Microservice
│   ├── main.py               # Lightweight FastAPI app (/encoder, /rerank)
│   ├── Dockerfile            # PyTorch + CUDA GPU-accelerated base image
│   └── models/               # SentenceTransformer and CrossEncoder pipelines
│
└── code-sandbox/             # Secure Python Interpreter Environment
    ├── runner.py             # Script execution wrapper (captures stdout/stderr/plots)
    └── Dockerfile            # Minimal hardened Alpine container with gVisor sandbox
```
