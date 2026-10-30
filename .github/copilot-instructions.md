# Nexora Instructions for GitHub Copilot

## Project

Nexora is an independent enterprise AI knowledge assistant. Onyx is a research reference only; do not copy its implementation assumptions into Nexora.

## Approved direction

- Stack: Next.js 16, React 19, TypeScript, Python 3.13, FastAPI, PostgreSQL 16+, pgvector, PostgreSQL full-text search, and LiteLLM. Celery and Redis are introduced with document ingestion, not Sprint 1.
- Initial hybrid search uses PostgreSQL with pgvector and PostgreSQL FTS behind the `SearchProvider` contract. Do not add OpenSearch as a Nexora dependency.
- The browser uses opaque server-side sessions, Argon2id password hashing, and a one-time initial-administrator setup command. Sessions have a 30-minute sliding idle timeout and a 12-hour absolute lifetime; the absolute expiry never extends. Use Nginx for same-origin reverse-proxy routing, CSRF protections, and Origin validation.
- The MVP is one tenant per deployment with server-controlled context. Tenant IDs alone do not provide isolation; do not implement or claim RLS before its complete security design is approved.
- Google and GitHub OAuth are MVP requirements scheduled for Sprint 5. Custom personas are deferred; evaluate cross-encoder reranking after establishing hybrid retrieval baseline.
- Do not persist provider API keys until configuration and secure storage are approved. Decide the embedding provider, model, dimension, and versioning strategy before implementing the embeddings schema.

## Working rules

- Before significant work, read [`docs/README.md`](../docs/README.md), [`DEVELOPMENT_GUIDELINES.md`](../docs/development/DEVELOPMENT_GUIDELINES.md), the relevant architecture docs, the roadmap, and the applicable sprint plan.
- Inspect the current repository, existing patterns, and applicable instructions before editing. Do not assume a proposed file structure already exists in code.
- Implement only the smallest complete change in the current sprint. Do not build future-sprint features early.
- Prefer simple, maintainable implementations. Avoid needless abstractions, microservices, configuration, and premature optimization; never trade away security, reliability, or data integrity.
- Validate inputs, enforce authorization at the data boundary, protect secrets, and preserve tenant boundaries. Surface errors clearly.
- Run focused tests for changed behavior and relevant checks before completion. Never claim tests passed unless they were run.
- Update directly related docs and record decisions or unresolved questions. Do not silently decide open architecture questions.
- Do not mark a sprint complete until its acceptance criteria are met and verification results are reported.
