# Developer Setup & Contribution Guide

This guide explains how to set up a local development environment, run the backend and frontend services, execute migrations, and adhere to Onyx coding standards.

---

## 1. Prerequisites & Environment Setup

Onyx requires:
- **Python**: 3.13+ (managed via `uv` or `pyenv`)
- **Node.js**: 22.x or 24.x (managed via `nvm`)
- **Package Managers**: `uv` (Python), `bun` or `npm` (Node)
- **Docker & Docker Compose**: For PostgreSQL, OpenSearch, and Redis

### Step 1: Clone and Configure Environment Files
```bash
cd onyx-main
cp deployment/docker_compose/env.template deployment/docker_compose/.env
```

### Step 2: Start Supporting Infrastructure Services
Start PostgreSQL, OpenSearch, and Redis in Docker:
```bash
docker compose -f deployment/docker_compose/docker-compose.dev.yml up -d relational_db opensearch cache minio
```

### Step 3: Setup Python Virtual Environment (`uv`)
```bash
# Sync frozen dependencies from uv.lock
uv sync --frozen
source .venv/bin/activate
```

### Step 4: Run Database Migrations
```bash
cd backend
alembic upgrade head
```

### Step 5: Install Frontend Dependencies
```bash
cd web
bun install # or npm install
```

---

## 2. Running Services Locally

### Terminal 1: FastAPI API Server
```bash
cd backend
source ../.venv/bin/activate
uvicorn onyx.main:app --reload --port 8080
```

### Terminal 2: Celery Background Worker & Beat
```bash
cd backend
source ../.venv/bin/activate
celery -A onyx.background.celery.apps.app_base:celery_app worker -B -l INFO -Q celery,indexing,pruning,docfetching
```

### Terminal 3: Model Inference Server (Optional for local embeddings)
```bash
cd backend
source ../.venv/bin/activate
uvicorn model_server.main:app --port 9000
```

### Terminal 4: Next.js Frontend
```bash
cd web
bun run dev # or npm run dev
# Accessible at http://localhost:3000
```

---

## 3. Testing Conventions

Onyx employs four testing categories (detailed in `backend/AGENTS.md` and `web/tests/`):

1. **Integration Tests** (Preferred):
   - Located in `backend/tests/integration/`.
   - Tests complete API and database flows against live test containers.
   ```bash
   pytest backend/tests/integration
   ```
2. **Unit Tests**:
   - Located in `backend/tests/unit/`.
   - Fast, in-memory validation of individual helper functions.
3. **Playwright E2E Tests**:
   - Located in `web/tests/e2e/`.
   - Runs full browser automated workflows.
   - Default Playwright credentials: `admin_user@example.com` / `TestPassword123!`.
   ```bash
   cd web
   bun run test:e2e
   ```

---

## 4. Code Standards & Pre-Commit Hooks

All contributions must pass strict formatting and type checking:

```bash
# Install git pre-commit hooks
pre-commit install

# Run checks across all files
pre-commit run --all-files

# Or run checks only on modified files
pre-commit run --files path/to/file.py
```

### Guidelines:
- **Strict Typing**: All Python functions must include complete type annotations (`typing` and Pydantic models). All TypeScript files must pass strict `tsc` checks.
- **Documentation**: Keep comments concise, accurate, and focused on non-obvious business logic.
- **No Mock Secrets**: Never commit API keys or plain passwords. Use `.vscode/.env` or test secrets providers (`backend/tests/utils/aws_secrets.py`).

