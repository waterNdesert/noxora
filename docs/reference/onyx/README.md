# Onyx Architectural Blueprint & Complete Rebuild Documentation

This repository contains the definitive technical documentation, codebase investigation, and implementation blueprint for **Onyx** (formerly *Danswer*), an enterprise-grade Gen-AI search and autonomous agent platform.

All documentation is maintained independently outside the Onyx source repository across 25 structured markdown guides.

---

## Part 1: Deep Codebase Investigation & Architecture

| File | Subject & Scope |
| :--- | :--- |
| **[01-project-overview.md](file:///home/water/Downloads/onyx-docs/01-project-overview.md)** | Core mission, value proposition, dual-licensing (CE vs EE), technology stack, and architectural pillars. |
| **[02-repository-structure.md](file:///home/water/Downloads/onyx-docs/02-repository-structure.md)** | Monorepo layout, subproject directories (`backend`, `web`, `cli`, `deployment`, `desktop`, `mobile`), and entry points. |
| **[03-system-architecture.md](file:///home/water/Downloads/onyx-docs/03-system-architecture.md)** | Tiered architecture diagram, inter-service communication protocols, data flows, and dynamic CE/EE code splitting. |
| **[04-backend-and-api.md](file:///home/water/Downloads/onyx-docs/04-backend-and-api.md)** | FastAPI backend, lifespan hooks, middleware pipeline, REST endpoint catalog, and standardized exception handling. |
| **[05-database-architecture.md](file:///home/water/Downloads/onyx-docs/05-database-architecture.md)** | PostgreSQL schema, SQLAlchemy models, ERD diagram, connection pooling, and multi-tenant schema isolation. |
| **[06-document-ingestion-pipeline.md](file:///home/water/Downloads/onyx-docs/06-document-ingestion-pipeline.md)** | Crawling, file extraction, token chunking, embedding generation, OpenSearch indexing, and index pruning. |
| **[07-connectors-and-integrations.md](file:///home/water/Downloads/onyx-docs/07-connectors-and-integrations.md)** | 40+ supported data sources, connector base classes, AES-GCM credential encryption, and custom connector implementation guide. |
| **[08-search-and-rag-pipeline.md](file:///home/water/Downloads/onyx-docs/08-search-and-rag-pipeline.md)** | Hybrid search (vector k-NN + BM25), query intent, ACL filter enforcement, cross-encoder reranking, and citation engine. |
| **[09-ai-and-llm-integrations.md](file:///home/water/Downloads/onyx-docs/09-ai-and-llm-integrations.md)** | LiteLLM gateway, supported providers, dynamic model catalog, streaming tool calling, token cost tracking, and tracing. |
| **[10-authentication-and-security.md](file:///home/water/Downloads/onyx-docs/10-authentication-and-security.md)** | Auth backends (OAuth2, SAML, OIDC, local), RBAC roles, inherited document ACLs, CSP headers, and defense-in-depth. |
| **[11-frontend-architecture.md](file:///home/water/Downloads/onyx-docs/11-frontend-architecture.md)** | Next.js 16 App Router, `/app` chat layout, API reverse proxy (`web/src/app/api/[...path]`), and SSE streaming decoder. |
| **[12-background-jobs-and-infrastructure.md](file:///home/water/Downloads/onyx-docs/12-background-jobs-and-infrastructure.md)** | Celery task queues (`indexing`, `docfetching`, `pruning`), Celery Beat schedule, Redis locks, and deployment topologies. |
| **[13-feature-by-feature-breakdown.md](file:///home/water/Downloads/onyx-docs/13-feature-by-feature-breakdown.md)** | Traces 6 major user features from frontend trigger through API handlers, database modifications, and responses. |
| **[14-known-issues-and-weaknesses.md](file:///home/water/Downloads/onyx-docs/14-known-issues-and-weaknesses.md)** | Operational failure modes (OOM crashes, OpenSearch circuit breakers, rate limits) and technical debt analysis. |
| **[15-developer-guide.md](file:///home/water/Downloads/onyx-docs/15-developer-guide.md)** | Local setup using `uv` and `bun`, running backend/frontend services, running tests, and pre-commit standards. |
| **[16-configuration-and-deployment.md](file:///home/water/Downloads/onyx-docs/16-configuration-and-deployment.md)** | Environment variable reference, Docker Compose production setup, Kubernetes Helm deployments, and backup routines. |
| **[17-glossary.md](file:///home/water/Downloads/onyx-docs/17-glossary.md)** | Definitions of project terms (CC-Pair, Persona, Turn, Chunk, Document Set, Permission Sync, LiteLLM). |

---

## Part 2: Product Blueprint & Complete Rebuild Roadmap

| File | Subject & Scope |
| :--- | :--- |
| **[18-complete-feature-inventory.md](file:///home/water/Downloads/onyx-docs/18-complete-feature-inventory.md)** | Comprehensive verified catalog of all Onyx features across AI, Knowledge, Security, and Enterprise tiers. |
| **[19-feature-implementation-analysis.md](file:///home/water/Downloads/onyx-docs/19-feature-implementation-analysis.md)** | Technical deep-dive for each feature: frontend components, backend modules, database models, and source traces. |
| **[20-user-journeys.md](file:///home/water/Downloads/onyx-docs/20-user-journeys.md)** | Sequence diagrams and code traces for six core user journeys from signup to administrative auditing. |
| **[21-feature-dependency-map.md](file:///home/water/Downloads/onyx-docs/21-feature-dependency-map.md)** | 5-layer dependency hierarchy map, shared cross-cutting components, and prerequisites for independent implementation. |
| **[22-full-rebuild-roadmap.md](file:///home/water/Downloads/onyx-docs/22-full-rebuild-roadmap.md)** | 17-stage implementation blueprint specifying features, backend/frontend files, DB models, complexity, and definitions of done. |
| **[23-technical-requirements.md](file:///home/water/Downloads/onyx-docs/23-technical-requirements.md)** | Hardware sizing, runtime dependencies, network egress rules, SLA latency benchmarks, and compliance standards. |
| **[24-implementation-priorities.md](file:///home/water/Downloads/onyx-docs/24-implementation-priorities.md)** | Phased delivery plan: MVP (Months 1–2), Connectors (Months 2–3), Agents (Months 3–4), Enterprise (Months 4–5). |
| **[25-rebuild-risk-and-complexity.md](file:///home/water/Downloads/onyx-docs/25-rebuild-risk-and-complexity.md)** | Risk matrix covering OpenSearch memory limits, model migration downtime, OAuth drift, app store reviews, and mitigations. |

---

## Verification & Status

All 25 guides were compiled through direct inspection of the Onyx repository code, configuration files, and database schemas without modifying the source tree or running destructive operations.
