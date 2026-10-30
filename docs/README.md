# Nexora Documentation

Nexora is an independent AI knowledge assistant project. Its approved product and architecture documents are authoritative; Onyx material is retained only as historical reference research.

## Documentation map

- [`architecture/`](architecture/) — Nexora product architecture, approved stack and decisions, database proposal, MVP scope, and architecture validation.
- [`development/`](development/) — development guidelines and the single current roadmap.
- [`sprints/`](sprints/) — sprint-specific plans. The Sprint 1 plan is not a declaration that implementation has started.
- [`archive/onyx-reference/`](archive/onyx-reference/) — preserved research about the separate Onyx product. These documents describe Onyx and are not Nexora requirements.

## Authoritative Nexora documents

- [Architecture](architecture/ARCHITECTURE.md)
- [Technology stack](architecture/TECHNOLOGY_STACK.md)
- [Architecture decisions](architecture/ARCHITECTURE_DECISIONS.md)
- [Database design](architecture/DATABASE_DESIGN.md)
- [MVP scope](architecture/MVP_SCOPE.md)
- [Architecture validation and open questions](architecture/ARCHITECTURE_VALIDATION.md)
- [Development guidelines](development/DEVELOPMENT_GUIDELINES.md)
- [Development roadmap](development/ROADMAP.md)
- [Sprint 1 foundation plan](sprints/SPRINT_01_FOUNDATION_PLAN.md)
- [Copilot instructions](../.github/copilot-instructions.md)

`ARCHITECTURE_DECISIONS.md` records approved decisions. `ARCHITECTURE_VALIDATION.md` records constraints, caveats, and unresolved questions. If a detail is unresolved, do not infer an implementation choice.

## Read first

AI coding assistants should read, in order:

1. This index and the repository [README](../README.md).
2. [Development guidelines](development/DEVELOPMENT_GUIDELINES.md) and [Copilot instructions](../.github/copilot-instructions.md).
3. [MVP scope](architecture/MVP_SCOPE.md), [architecture](architecture/ARCHITECTURE.md), [stack](architecture/TECHNOLOGY_STACK.md), and [architecture decisions](architecture/ARCHITECTURE_DECISIONS.md).
4. [Database design](architecture/DATABASE_DESIGN.md) and [architecture validation](architecture/ARCHITECTURE_VALIDATION.md) before database or tenancy work.
5. [Roadmap](development/ROADMAP.md) and the specific sprint plan before implementing sprint work.
6. Onyx reference material only when it answers a specific research question.

## Link and authority conventions

Internal links should be relative to the containing Markdown file and resolve within this repository. Open questions must be labeled explicitly. The approved initial search design is PostgreSQL + pgvector + PostgreSQL FTS; OpenSearch appears only in Onyx research or as a possible future provider, not as a current Nexora dependency.
