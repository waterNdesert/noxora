# Development Guidelines

## Philosophy

Build simple, maintainable and functional implementations. Avoid unnecessary complexity, premature optimisation, unnecessary microservices and excessive abstraction. Do not sacrifice security, reliability or data integrity for simplicity.

## Before changing code

1. Read the applicable repository instructions and inspect the existing implementation, tests, and current project structure.
2. Read the relevant Nexora architecture and database documents, the [roadmap](ROADMAP.md), and the applicable sprint plan.
3. Confirm that the work belongs to the current sprint. Record a blocker rather than pulling future-sprint scope forward.
4. Identify expected behavior, failure cases, access boundaries, and a focused verification command before editing.

## Architecture and implementation

- Follow the approved stack and decisions in [`../architecture/`](../architecture/).
- PostgreSQL + pgvector + PostgreSQL FTS is the approved initial search architecture; do not introduce OpenSearch.
- The browser uses opaque server-side sessions, Argon2id password hashing, and a one-time initial-administrator setup command. Do not substitute JWT authentication without an approved decision.
- Route same-origin browser `/api/*` requests directly to FastAPI through the reverse proxy. Protect cookie-authenticated state-changing requests with CSRF protections and Origin validation.
- The MVP is one tenant per deployment with server-controlled tenant context. Tenant IDs alone do not provide isolation; do not implement or claim RLS until its complete security design is approved.
- Introduce Celery and Redis with asynchronous document ingestion, not Sprint 1. Do not add a generic Redis cache/session/lock role without an approved requirement.
- Do not persist provider API keys until their configuration and secure-storage approach are approved. Decide embedding provider/model/dimension/versioning before creating the embedding schema.
- Google and GitHub OAuth are MVP requirements scheduled for Sprint 5. Custom personas are deferred; evaluate cross-encoder reranking after establishing hybrid-search baseline.
- Keep HTTP handlers, business workflows, persistence, and external integrations appropriately separated without adding abstraction layers without a concrete need.
- Preserve existing behavior unless a documented requirement intentionally changes it.
- Keep APIs, migrations, tests, and documentation consistent. Avoid hidden fallbacks and swallowed errors.
- Do not implement unresolved design choices by assumption. Raise them and update the decision record after approval.

## Security and reliability

- Enforce authentication and authorization on the server, including at the data access boundary.
- Treat user content, files, connector data, and model output as untrusted input.
- Store secrets outside source control; use approved encryption and secret-management mechanisms.
- Store browser session secrets only as hashes; invalidate sessions on logout and relevant password/account security changes.
- Browser sessions use a 30-minute sliding idle timeout and a 12-hour absolute lifetime. Activity must never extend absolute expiry; expired sessions are invalidated server-side and require reauthentication.
- Scope database access correctly and preserve transaction integrity. Do not claim tenant isolation is guaranteed until its policy and pooled-connection behavior are decided and tested.
- Bound file sizes, background work, external calls, and retries; report failures explicitly.
- Do not expose private documents or citations outside the user's authorized scope.

## Testing

- Add or update tests for behavior changed; prefer focused unit tests and add integration coverage for API/database/security boundaries.
- Run the smallest relevant test command, then applicable type checks, lint, or build checks.
- Verify failure cases as well as successful behavior. Never delete or skip failing tests to produce a green run.
- Report exact commands and outcomes; distinguish unrun checks from passing checks.

## Dependencies and migrations

- Reuse existing dependencies and patterns. Add a dependency only when a requirement cannot reasonably be met with the current stack, and explain why.
- Use the repository's package manager and lockfile when dependency changes are approved.
- Make database schema changes through versioned migrations. Review generated SQL, constraints, indexes, data backfills, rollback implications, and transaction behavior before applying.
- Verify migrations from an empty database. Treat destructive/data migration rollback as a recovery decision requiring backup/restore or a forward-fix plan; do not assume every downgrade is lossless.
- Never select an embedding dimension or tenant-isolation mechanism by inference; resolve the relevant open questions first.

## Documentation

- Treat [`../README.md`](../README.md) as the documentation map and [`../architecture/ARCHITECTURE_DECISIONS.md`](../architecture/ARCHITECTURE_DECISIONS.md) as the record of approved decisions.
- Update the relevant documentation when behavior, API contracts, setup, architecture, or operational expectations change.
- Use repository-relative links. Label approved decisions, proposals, and open questions clearly.
- Keep Onyx material in [`../archive/onyx-reference/`](../archive/onyx-reference/); it is research, not a Nexora specification.

## AI coding assistant workflow

1. Summarize the requested behavior and identify the applicable sprint scope.
2. Inspect code, tests, and instructions before planning a change.
3. Make the smallest complete implementation and tests.
4. Run focused verification and review the diff for unrelated changes, security issues, and accidental future scope. Report checks that were not run; a plan alone does not mean work has started or passed verification.
5. Update relevant docs and report what changed, test commands/results, and any unresolved questions.

## Sprint completion

A sprint is complete only when all in-scope acceptance criteria are met, migrations and docs are included where needed, relevant verification passes, known failures are reported, and no future-sprint scope was silently added. A plan alone does not mean work has started or completed.
