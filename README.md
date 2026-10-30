# Nexora

Nexora is an independent enterprise AI knowledge assistant. Sprint 1 is establishing the FastAPI, Next.js, PostgreSQL, and session-authentication foundation.

Start with the [documentation index](docs/README.md) for the approved architecture, roadmap, sprint plan, and preserved Onyx reference research.

## Sprint 1 local setup

Prerequisites: Python 3.13, [uv](https://docs.astral.sh/uv/), Node.js 22 or later, npm, and Docker Compose. Docker is also used to run the local Nginx reverse proxy.

1. Copy `.env.example` to `.env` and change the local PostgreSQL password if needed.
2. Start PostgreSQL with `docker compose up -d postgres`.
3. In `backend/`, run `uv sync --group dev` and `uv run alembic upgrade head`.
4. Create the initial administrator with `uv run python -m src.commands.create_initial_admin`.
5. Start FastAPI in `backend/` with `uv run uvicorn src.main:app --host 0.0.0.0 --port 8000`.
6. In `web/`, run `npm ci` and `npm run dev`.
7. From the repository root, start the local Nginx proxy in a separate terminal:

   ```sh
   docker run --rm --name nexora-nginx \
     --add-host=host.docker.internal:host-gateway \
     -p 127.0.0.1:8080:8080 \
     -v "$(pwd)/deployment/nginx/local.conf:/etc/nginx/conf.d/default.conf:ro" \
     nginx:1.28-alpine
   ```

Open `http://localhost:8080`. FastAPI exposes liveness, readiness, and version endpoints at `/api/health/live`, `/api/health/ready`, and `/api/version`. The Compose file contains PostgreSQL only; Redis and Celery are introduced with document ingestion, not Sprint 1.

Run backend checks from `backend/` with `uv run pytest` and `uv run ruff check .`. Run frontend checks from `web/` with `npm test`, `npm run lint`, `npm run typecheck`, and `npm run build`.
