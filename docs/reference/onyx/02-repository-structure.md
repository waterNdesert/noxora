# Repository Structure & Subprojects

The Onyx repository is organized as a monorepo containing the backend API, the background task worker, the Next.js frontend web app, deployment scripts, client applications, and developer tools.

```
onyx-main/
├── backend/                  # Python FastAPI API server, Celery workers, models
│   ├── alembic/              # Database migration versions (public schema)
│   ├── alembic_tenants/      # Multi-tenant schema database migrations
│   ├── ee/                   # Enterprise Edition backend code (mirrors onyx structure)
│   ├── model_server/         # Dedicated embedding & cross-encoder inference server
│   ├── onyx/                 # Community Edition core application logic
│   │   ├── access/           # Document access control & permissions logic
│   │   ├── agents/           # Persona agent definitions and execution logic
│   │   ├── auth/             # User authentication, JWT, OAuth, OIDC, SAML, CAPTCHA
│   │   ├── background/       # Celery configuration, beat schedules, workers
│   │   ├── cache/            # Caching interfaces and Redis cache layers
│   │   ├── chat/             # Chat processing, message streaming, LLM prompt loop
│   │   ├── configs/          # Environment variable loaders and constant defaults
│   │   ├── connectors/       # 40+ external application connectors (Google, Slack, etc.)
│   │   ├── db/               # SQLAlchemy models, CRUD operations, engine pools
│   │   ├── document_index/   # OpenSearch index client, mapping schemas, interfaces
│   │   ├── error_handling/   # Structured exceptions, error codes, HTTP handlers
│   │   ├── file_processing/  # Document extraction, PDF parsing, text extraction
│   │   ├── file_store/       # File storage abstractions (S3, MinIO, local disk)
│   │   ├── indexing/         # Chunking, tokenization, embedding, pipeline coordination
│   │   ├── llm/              # LLM providers, LiteLLM gateway, model catalog, cost tables
│   │   ├── mcp_server/       # Model Context Protocol stdio/HTTP server implementation
│   │   ├── redis/            # Redis connection pooling, distributed locks
│   │   ├── server/           # FastAPI REST endpoints categorized by feature
│   │   ├── tools/            # Tool definitions (Search, Web search, Python interpreter)
│   │   ├── tracing/          # OpenTelemetry / Langfuse / Arize Phoenix observability
│   │   └── utils/            # General utilities, logging, dynamic EE gating helpers
│   ├── requirements/         # Exported dependency lockfiles
│   └── tests/                # Unit, integration, and dependency tests
│
├── web/                      # Next.js 16 + React 19 Frontend Application
│   ├── src/
│   │   ├── app/              # Next.js App Router (pages and API proxy routes)
│   │   │   ├── admin/        # Admin console routes (connectors, LLM, users, tools)
│   │   │   ├── api/          # Internal Next.js API proxy routes forwarding to backend
│   │   │   ├── app/          # Core chat interface (`/app`)
│   │   │   ├── auth/         # Login, signup, password reset, SSO callbacks
│   │   │   └── craft/        # Craft workbench & live code execution UI
│   │   ├── components/       # Shared UI components (Radix primitives, forms, dialogs)
│   │   ├── ee/               # Enterprise UI components (whitelabeling, RBAC, billing)
│   │   ├── hooks/            # Custom React hooks (chat streaming, state listeners)
│   │   ├── lib/              # API clients, auth helpers, cookie management, constants
│   │   ├── proxy.ts          # Edge proxy middleware and Content Security Policy (CSP)
│   │   └── sections/         # Specialized UI sections (sidebar, chat header, settings)
│   └── tests/                # Jest component tests and Playwright E2E suites
│
├── cli/                      # Command-line interface tool (`onyx-cli`)
├── deployment/               # Production and developer deployment infrastructure
│   ├── docker_compose/       # Docker Compose manifests (dev, prod, airgap, multitenant)
│   ├── helm/                 # Kubernetes Helm charts
│   ├── terraform/            # Cloud infrastructure modules (AWS, GCP, Azure)
│   └── aws_ecs_fargate/      # AWS ECS deployment configurations
│
├── desktop/                  # Tauri-based cross-platform desktop wrapper
├── mobile/                   # React Native + Expo cross-platform mobile app
├── widget/                   # Embeddable standalone chat widget (script tag integration)
├── extensions/               # Chrome and Firefox browser extensions
├── terraform-provider-onyx/  # Terraform provider for programmatic Onyx management
└── .agents/                  # Agent tooling, custom skills, and feature map documentation
    ├── feature-map/          # Detailed documentation for 50+ subsystems
    └── skills/               # Reusable agent skills
```

---

## Key Top-Level Entry Points

### 1. Backend API Server (`backend/onyx/main.py`)
- Starts the FastAPI application.
- Configures middleware: CORS, Sentry error tracking, request ID injection, latency logging, rate limiting, and client IP extraction.
- Registers route handlers for authentication, chat, search, document management, connectors, tools, LLMs, and administrative settings.
- Wires up the lifecycle manager (`@asynccontextmanager def lifespan`) to initialize database connection pools, warm up models, start background telemetry, and seed default roles and settings.

### 2. Celery Background Worker (`backend/onyx/background/celery/apps/app_base.py`)
- Defines the Celery application instance configured with Redis as broker.
- Dispatches queued background jobs across distinct queues (e.g., `celery`, `indexing`, `pruning`, `docfetching`).
- Houses the Celery Beat scheduler (`beat_schedule.py`) for recurring tasks such as connector syncs, document index health checks, and permission sync passes.

### 3. Model Server (`backend/model_server/main.py`)
- Standalone FastAPI microservice optimized for local deep learning inference.
- Houses PyTorch / HuggingFace pipelines for dense sentence embedding (`SentenceTransformer`) and cross-encoder reranking (`CrossEncoder`).
- Separates GPU/heavy compute dependencies from the main lightweight API server.

### 4. Next.js Web Frontend (`web/src/proxy.ts` & `web/src/app/layout.tsx`)
- `web/src/proxy.ts`: Intercepts inbound HTTP requests at the edge to validate authentication cookies, enforce route protection rules, and attach Content Security Policy (CSP) headers.
- `web/src/app/api/[...path]/route.ts`: Proxies client-side API requests to the internal backend FastAPI service, preserving user authentication cookies and forwarding headers.
- `web/src/app/app/page.tsx`: Main chat and knowledge retrieval workspace.

