# Enterprise AI Knowledge Platform — Development Foundation

This directory contains the production-ready architecture design, technology evaluation, directory structure, database schemas, development roadmap, MVP scope, architecture decision records (ADRs), and final validation report for building an enterprise-grade AI knowledge intelligence and autonomous agent platform.

The architecture features a unified **PostgreSQL 16+ data store utilizing `pgvector` and Full-Text Search (FTS)** for hybrid retrieval, shielded behind an abstract `SearchProvider` interface for seamless future scalability.

---

## Planning Documents Index

| Document | Description |
| :--- | :--- |
| **[application-architecture.md](file:///home/water/Downloads/onyx-app-plan/application-architecture.md)** | Production-ready architecture design, unified PostgreSQL hybrid search, pluggable `SearchProvider` interface, and performance limits. |
| **[technology-stack.md](file:///home/water/Downloads/onyx-app-plan/technology-stack.md)** | Technology recommendations, evaluation of PostgreSQL + `pgvector` vs. OpenSearch/Qdrant, operational complexity, and fit. |
| **[project-directory-structure.md](file:///home/water/Downloads/onyx-app-plan/project-directory-structure.md)** | Complete monorepo layout for `backend/`, `web/`, `services/`, and `deployment/` with the pluggable retrieval provider structure. |
| **[initial-database-design.md](file:///home/water/Downloads/onyx-app-plan/initial-database-design.md)** | PostgreSQL 16+ schema with `pgvector` HNSW index, FTS GIN index, `document_chunks` table, RRF CTE SQL query, and indexes. |
| **[development-roadmap.md](file:///home/water/Downloads/onyx-app-plan/development-roadmap.md)** | Actionable 5-phase, 18-sprint development roadmap updated for PostgreSQL + `pgvector` hybrid search delivery. |
| **[mvp-scope.md](file:///home/water/Downloads/onyx-app-plan/mvp-scope.md)** | Boundaries of the Minimum Viable Product (MVP), user journey, lean 8 GB RAM topology, and success metrics. |
| **[architecture-decisions.md](file:///home/water/Downloads/onyx-app-plan/architecture-decisions.md)** | Architecture Decision Records (ADRs 001–007) detailing the unified Postgres search choice and data-driven migration triggers. |
| **[09-final-architecture-validation.md](file:///home/water/Downloads/onyx-app-plan/09-final-architecture-validation.md)** | **Final Architecture Validation & Readiness Assessment**: Technical review across security, consistency, pgvector HNSW limits, and Sprint 1 go/no-go recommendation. |

---

## Verification & Status

All documents reflect the updated PostgreSQL + `pgvector` hybrid retrieval architecture, eliminating OpenSearch as a mandatory dependency while preserving full RAG, citation, ACL filtering, and ranking capabilities.
