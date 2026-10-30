# Nexora Documentation Organization Design

## Goal

Organize the existing documentation so that future coding assistants can distinguish Nexora's approved product and architecture from historical Onyx research, find current development guidance, and identify unresolved decisions without inferring answers.

This is a documentation-only change. It does not implement application features, start Sprint 1, change the approved stack, or introduce OpenSearch into Nexora.

## Information Architecture

- `docs/architecture/` contains Nexora's approved architecture, technology stack, architecture decisions, database design, MVP scope, and architecture validation.
- `docs/development/` contains practical development guidelines and the single authoritative Nexora roadmap.
- `docs/sprints/` contains active sprint plans. Add a Sprint 1 Foundation Plan based on the current roadmap and approved Nexora decisions; it must not claim implementation has begun.
- `docs/reference/onyx/` preserves all existing Onyx research as reference material, not Nexora implementation requirements.
- `docs/README.md` is the documentation index and tells human and AI readers which sources are authoritative and what to read first.
- `.github/copilot-instructions.md` provides concise agent guidance and points to detailed docs.
- Root `README.md` links to the docs index.

All existing research remains available. Existing documents are moved rather than duplicated. Internal Markdown links are changed to repository-relative links and validated after moves.

## Authority and Architecture Rules

The Nexora architecture decision records approve PostgreSQL 16+ with pgvector and PostgreSQL full-text search as the initial unified retrieval store. The `SearchProvider` abstraction permits future alternatives but does not authorize implementing OpenSearch now. Onyx documents describe the reference product and its architecture; their OpenSearch descriptions remain historically accurate for Onyx and are not rewritten as Nexora decisions.

The stack and architecture docs are authoritative for Nexora. The final validation document is retained but its identified gaps are represented as unresolved questions where the repository does not contain an approved answer.

## Inconsistency Handling

- Preserve the approved PostgreSQL + pgvector decision and clearly label Onyx's OpenSearch architecture as reference-only.
- Document the mismatch between `VECTOR(1024)` and other mentioned embedding dimensions as an open configuration/schema decision; do not choose a dimension.
- Document tenant isolation requirements and the unresolved transaction/pool/RLS reset mechanism; do not invent a policy.
- Treat the Nexora roadmap's 18 sequential 14-day sprints as approximately 36 weeks. Keep Onyx's historical five-month estimates within the Onyx reference, clearly labeled as historical.
- Correct the Onyx user-journey index to match the six journeys actually present.
- Replace broken absolute `file:///home/...` references with valid repository-relative links.
- Mark the standalone Sprint 1 Foundation Plan as newly created documentation. It summarizes work and gates only; it does not authorize or start implementation.

## Development Guidance

The consolidated guidelines and Copilot instructions emphasize simple, maintainable, secure and reliable implementations; inspecting existing code before changing it; incremental scope aligned to the active sprint; focused tests; migrations for schema changes; and documentation updates. They prohibit premature future-sprint features and unnecessary abstractions or services.

## Verification

After organizing the docs:

1. Confirm all existing Onyx research files are preserved.
2. Check local Markdown links and index targets.
3. Check that authority boundaries and known open questions are explicit.
4. Review the changed-file list and confirm no application implementation files changed.
