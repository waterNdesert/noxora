# Nexora Instructions for GitHub Copilot

## Project

Nexora is an independent enterprise AI knowledge assistant. Onyx is a research reference only; do not copy its implementation assumptions into Nexora.

## Approved direction

- Stack: Next.js 16, React 19, TypeScript, Python 3.13, FastAPI, PostgreSQL 16+, pgvector, PostgreSQL full-text search, LiteLLM, Redis, and Celery.
- Initial hybrid search uses PostgreSQL with pgvector and PostgreSQL FTS behind the `SearchProvider` contract. Do not add OpenSearch as a Nexora dependency.
- The MVP is single-tenant. Tenant-aware data design and later enterprise tenant isolation are planned, but the exact isolation/RLS/pool strategy remains unresolved.
- The embedding model and vector dimension must be decided before implementing the embeddings schema.

## Working rules

- Before significant work, read [`docs/README.md`](../docs/README.md), [`DEVELOPMENT_GUIDELINES.md`](../docs/development/DEVELOPMENT_GUIDELINES.md), the relevant architecture docs, the roadmap, and the applicable sprint plan.
- Inspect the current repository, existing patterns, and applicable instructions before editing. Do not assume a proposed file structure already exists in code.
- Implement only the smallest complete change in the current sprint. Do not build future-sprint features early.
- Prefer simple, maintainable implementations. Avoid needless abstractions, microservices, configuration, and premature optimization; never trade away security, reliability, or data integrity.
- Validate inputs, enforce authorization at the data boundary, protect secrets, and preserve tenant boundaries. Surface errors clearly.
- Run focused tests for changed behavior and relevant checks before completion. Never claim tests passed unless they were run.
- Update directly related docs and record decisions or unresolved questions. Do not silently decide open architecture questions.
- Do not mark a sprint complete until its acceptance criteria are met and verification results are reported.
