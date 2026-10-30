# Sprint 1: Application Foundation

**Status:** Complete
**Source of scope:** [Development roadmap](../development/ROADMAP.md), Sprint 1
**Purpose:** Bound the approved foundation implementation and its acceptance criteria.

## Objective

Establish the Nexora application foundation: FastAPI and Next.js shells, PostgreSQL/Alembic setup, a one-time initial-administrator provisioning command, opaque server-side local sessions, and a protected current-user endpoint.

## In scope

- Establish the repository structure and local development configuration for the approved stack.
- Start PostgreSQL 16+ with pgvector available. Redis is not a Sprint 1 dependency.
- Create backend configuration, database session lifecycle, health/version endpoints, and Alembic migration scaffolding.
- Implement Argon2id password hashing, the one-time initial-administrator setup command, local login/logout, opaque server-side sessions, and HTTP-only cookies.
- Provide `/api/users/me` and enforce authentication/authorization server-side.
- Create a minimal Next.js application shell and connect it to FastAPI through a same-origin reverse-proxy route.
- Document environment setup, required secrets, and focused verification commands.

## Out of scope

- Document upload, object storage, extraction, chunking, embeddings, or search queries.
- Celery/Redis ingestion workers, LLM chat, streaming answers, citations, personas, or tool execution.
- Model-provider key persistence.
- Google/GitHub OAuth; these are scheduled for the dedicated Sprint 5.
- Public registration and account provisioning after the initial administrator; decide policy before implementing those flows.
- Full enterprise tenant isolation or RLS. The MVP has one server-selected tenant; tenant identifiers alone are not isolation.
- Workplace connectors, bots, enterprise SSO, billing, custom personas, and advanced analytics.
- Any OpenSearch service or dependency.

## Decisions and prerequisites

- Follow [Technology stack](../architecture/TECHNOLOGY_STACK.md), [MVP scope](../architecture/MVP_SCOPE.md), and [Architecture decisions](../architecture/ARCHITECTURE_DECISIONS.md).
- PostgreSQL 16+ with pgvector and PostgreSQL FTS is the approved search direction. Enable the vector extension if needed, but do not add an embedding column or HNSW index in Sprint 1.
- Select the embedding provider, model, dimension, and versioning strategy before Sprint 2 implements the embedding schema.
- The deployment is single-tenant with server-controlled context. Do not add or claim RLS or enterprise tenant isolation.
- Session cookies are HTTP-only, production Secure, SameSite=Lax, Path=/, and host-only. Apply CSRF protections and Origin validation to state-changing cookie-authenticated requests.
- Use a 30-minute sliding idle timeout and a 12-hour absolute session lifetime. Activity must never extend the absolute expiry; expired sessions are invalidated server-side and require reauthentication.
- Validate only settings required by Sprint 1 at startup; do not require future connector-encryption or provider-key secrets.
- Apply Alembic migrations through controlled commands. Verify a fresh-database upgrade; document downgrade limitations and backup/forward-fix recovery for destructive changes.

## Work sequence

1. Confirm repo structure, instructions, package tooling, and local service approach.
2. Add minimal configuration and verify PostgreSQL health; do not start Redis.
3. Add FastAPI application startup/shutdown, settings, database connection, and health/version endpoints.
4. Add initial Alembic migration(s), including pgvector extension setup if needed. Do not create an embedding column or choose a vector dimension.
5. Add local user/session persistence, Argon2id password hashing, one-time initial-administrator provisioning, login/logout, cookie and CSRF protections, and `/api/users/me`.
6. Add the minimal Next.js shell and verify same-origin API routing to FastAPI.
7. Add focused backend and frontend tests for health, authentication, and protected-user behavior; run relevant lint/type/build checks.
8. Document setup and review the final diff against the sprint scope.

## Acceptance criteria

- A new developer can follow the repository setup instructions to start the local foundation without requiring unused future-sprint services or secrets.
- FastAPI and Next.js start using the documented development workflow.
- PostgreSQL migrations apply cleanly and the required extension is available.
- Health/version endpoints return successful responses when dependencies are healthy and report dependency failures explicitly.
- The initial administrator can be created through the one-time command, log in, log out, and fetch `/api/users/me`; protected endpoints reject unauthenticated requests. Public registration is not implemented without an approved policy.
- Passwords use Argon2id; session credentials are stored only as hashes. Logout invalidates the session, and inactive users have their sessions revoked on the next authenticated request. Any future password-change or reset flow must invalidate affected sessions.
- Cookie attributes, CSRF defenses, Origin validation, and same-origin routing match the approved policy.
- Focused tests cover successful and rejected authentication paths.
- No document ingestion, search, LLM, connector, or later-sprint feature is implemented as part of this sprint.

## Completion checklist

- [x] All acceptance criteria are verified.
- [x] Database migration and rollback considerations are reviewed.
- [x] Focused tests and relevant quality checks pass, with commands/results recorded.
- [x] Setup and architecture docs reflect the implemented foundation.
- [x] Embedding provider/model/dimension/versioning, OAuth account-linking behavior, account provisioning after bootstrap, and enterprise tenant isolation remain explicit until their implementation sprint.
- [x] No future-sprint scope or OpenSearch dependency was added.
- [x] Sprint status is updated only after verification and review.

## Verification record

- Backend: `uv run pytest -q` (10 passed) and `uv run ruff check .` (passed).
- Frontend: `npm test` (2 passed), `npm run lint`, `npm run typecheck`, and `npm run build` (all passed).
- Database: fresh Alembic upgrade applied; `alembic current` reports `0001_foundation (head)`, `alembic check` reports no model drift, and PostgreSQL reports pgvector 0.8.7.
- Local proxy smoke test: `/api/health/live` and `/api/health/ready` returned 200, unauthenticated `/api/users/me` returned 401, and `/login` returned 200. Nginx configuration syntax was validated.
- Documentation: all 64 local Markdown links across 39 documents resolve; `git diff --check` passes.
