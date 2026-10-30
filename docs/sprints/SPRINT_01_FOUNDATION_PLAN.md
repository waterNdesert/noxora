# Sprint 1: Application Foundation

**Status:** Planned — not started
**Source of scope:** [Development roadmap](../development/ROADMAP.md), Sprint 1
**Purpose:** Turn the approved foundation scope into a bounded implementation checklist. This file does not start the sprint.

> This is a planning document only. Sprint 1 has not been started by this document; implementation requires a separate explicit start decision.

## Objective

Establish the Nexora repository and minimum working application foundation: local development services, a FastAPI backend, a Next.js web shell, PostgreSQL migrations, and local authentication with a protected current-user endpoint.

## In scope

- Establish the repository structure and local development configuration for the approved stack.
- Start PostgreSQL with the required pgvector extension and Redis using the agreed local setup.
- Create backend configuration, database session lifecycle, health/version endpoints, and Alembic migration scaffolding.
- Implement local account registration/login using secure password hashing and HTTP-only session cookies.
- Provide `/api/users/me` and enforce authentication/authorization server-side.
- Create a minimal Next.js application shell and connect it to the backend using the approved development routing.
- Document environment setup, required secrets, and focused verification commands.

## Out of scope

- Document upload, extraction, chunking, embeddings, or search queries.
- LLM chat, streaming answers, citations, personas, or tool execution.
- Workplace connectors, Celery ingestion workflows, bots, SSO, billing, and advanced analytics.
- Google/GitHub OAuth. It is listed in the MVP scope but is not assigned to a sprint in the roadmap; resolve its delivery sequence before committing to MVP completion.
- Full enterprise tenant isolation or a decided RLS/pool-reset design.
- Any OpenSearch service or dependency.

## Decisions and prerequisites

- Use the stack and MVP boundaries in [Technology stack](../architecture/TECHNOLOGY_STACK.md) and [MVP scope](../architecture/MVP_SCOPE.md).
- PostgreSQL + pgvector + PostgreSQL FTS is the approved search direction. Sprint 1 may provision the PostgreSQL extension, but should not add an embedding column that assumes a dimension.
- The embedding model and vector dimension remain open; resolve them before implementing the embeddings schema in a later sprint.
- The MVP is single-tenant. Tenant-aware design is a future direction, but the exact tenant isolation, RLS policy, transaction context, and pooled-connection reset remain open. Do not claim isolation until decided and tested.
- Validate required authentication and encryption secrets at startup; never add real secrets to the repository.

## Work sequence

1. Confirm repo structure, instructions, package tooling, and local service approach.
2. Add minimal service configuration and verify PostgreSQL/Redis health.
3. Add FastAPI application startup/shutdown, settings, database connection, and health/version endpoints.
4. Add initial Alembic migration(s), including the approved database extension setup.
5. Add user persistence, password hashing, registration, login/logout, cookie settings, and `/api/users/me`.
6. Add the minimal Next.js shell and verify its local connection to the API.
7. Add focused backend and frontend tests for health, authentication, and protected-user behavior; run relevant lint/type/build checks.
8. Document setup and review the final diff against the sprint scope.

## Acceptance criteria

- A new developer can follow the repository setup instructions to start the local foundation.
- FastAPI and Next.js start using the documented development workflow.
- PostgreSQL migrations apply cleanly and the required extension is available.
- Health/version endpoints return successful responses when dependencies are healthy and report dependency failures explicitly.
- Users can register, log in, log out, and fetch `/api/users/me`; protected endpoints reject unauthenticated requests.
- Passwords are never stored in plaintext; session cookies use secure production settings and HTTP-only access.
- Focused tests cover successful and rejected authentication paths.
- No document ingestion, search, LLM, connector, or later-sprint feature is implemented as part of this sprint.

## Completion checklist

- [ ] All acceptance criteria are verified.
- [ ] Database migration and rollback considerations are reviewed.
- [ ] Focused tests and relevant quality checks pass, with commands/results recorded.
- [ ] Setup and architecture docs reflect the implemented foundation.
- [ ] Open embedding and tenant-isolation decisions remain explicit and unresolved unless separately approved.
- [ ] No future-sprint scope or OpenSearch dependency was added.
- [ ] Sprint status is updated only after verification and review.
