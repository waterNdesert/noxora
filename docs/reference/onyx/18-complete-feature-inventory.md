# Complete Onyx Feature Inventory

This document provides a comprehensive, verified inventory of all capabilities, features, and modules present in the Onyx platform. Each entry identifies what the feature does, how it is surfaced to users, its underlying technical mechanism, and its availability tier.

---

## 1. Summary Matrix

| Category | Feature Name | CE vs. EE | Codebase Status | Key Entry Modules |
| :--- | :--- | :--- | :--- | :--- |
| **Core AI** | Chat & Search UI | CE | Fully Implemented | `web/src/app/app/`, `backend/onyx/chat/` |
| **Core AI** | Multi-LLM Provider Gateway | CE | Fully Implemented | `backend/onyx/llm/multi_llm.py` |
| **Core AI** | Custom AI Agents (Personas) | CE / EE | Fully Implemented | `backend/onyx/server/features/persona/` |
| **Core AI** | MCP Actions (Model Context Protocol) | CE | Fully Implemented | `backend/onyx/tools/tool_implementations/mcp/` |
| **Core AI** | OpenAPI Custom Tool Actions | CE | Fully Implemented | `backend/onyx/tools/tool_implementations/custom/` |
| **Core AI** | Web Search (SearXNG / Tavily / Bing) | CE | Fully Implemented | `backend/onyx/tools/tool_implementations/web_search/` |
| **Core AI** | Deep Research Multi-Turn Search | CE | Fully Implemented | `backend/onyx/deep_research/` |
| **Core AI** | Python Code Interpreter Sandbox | CE | Fully Implemented | `backend/onyx/tools/tool_implementations/python/` |
| **Core AI** | Image Generation (DALL-E / Imagen) | CE | Fully Implemented | `backend/onyx/image_gen/` |
| **Core AI** | Developer APIs & OpenAPI Schema | CE | Fully Implemented | `backend/onyx/server/onyx_api/` |
| **Core AI** | Query History, Tree Branching & Folders | CE | Fully Implemented | `backend/onyx/db/chat.py` |
| **Core AI** | Token & Financial Usage Dashboards | CE / EE | Fully Implemented | `backend/onyx/server/features/usage/` |
| **Knowledge**| 40+ Application Connectors | CE | Fully Implemented | `backend/onyx/connectors/` |
| **Knowledge**| Document Processing & Text Extraction | CE | Fully Implemented | `backend/onyx/file_processing/` |
| **Knowledge**| Semantic Chunking & Token Windowing | CE | Fully Implemented | `backend/onyx/indexing/chunker.py` |
| **Knowledge**| Hybrid Search (Vector k-NN + BM25) | CE | Fully Implemented | `backend/onyx/document_index/opensearch/` |
| **Knowledge**| RAG Context Compression & Packing | CE | Fully Implemented | `backend/onyx/chat/compression.py` |
| **Knowledge**| Verifiable Citations & Footnotes | CE | Fully Implemented | `backend/onyx/chat/citation_processor.py` |
| **Knowledge**| Upstream Permission Sync | EE | Fully Implemented | `backend/ee/onyx/external_permissions/` |
| **Knowledge**| Slackbot & Discord Bot | CE | Fully Implemented | `backend/onyx/onyxbot/` |
| **Knowledge**| Event Hook Extensions | CE | Fully Implemented | `backend/onyx/hooks/` |
| **Security** | Basic Auth (Email/Password) | CE | Fully Implemented | `backend/onyx/auth/users.py` |
| **Security** | OAuth2 (Google, GitHub, Microsoft) | CE | Fully Implemented | `backend/onyx/auth/users.py` |
| **Security** | SAML 2.0 & OIDC Enterprise SSO | EE | Fully Implemented | `backend/onyx/server/saml_multi.py` |
| **Security** | Role-Based Access Control (RBAC) | CE / EE | Fully Implemented | `backend/onyx/auth/permissions.py` |
| **Security** | Document-Level ACL Filtering | CE / EE | Fully Implemented | `backend/onyx/access/` |
| **Security** | AES-GCM 256 Secret Encryption | CE | Fully Implemented | `backend/onyx/db/credentials.py` |
| **Security** | Multi-Tenancy (Schema Isolation) | EE | Fully Implemented | `backend/alembic_tenants/` |
| **Enterprise**| Whitelabeling & Custom Theming | EE | Fully Implemented | `backend/ee/onyx/server/whitelabeling/` |
| **Enterprise**| Data Audit Exports & Analytics | EE | Fully Implemented | `backend/ee/onyx/server/analytics/` |
| **Enterprise**| Stripe Invoice Billing & Tiers | EE | Fully Implemented | `backend/ee/onyx/server/billing/` |
| **Enterprise**| Dedicated SLA / Commercial Support | Commercial| Business Only | Non-code contractual service |

---

## 2. Detailed Category Inventory

### Section A: Core AI and Productivity

#### 1. Chat and Search UI
- **Description**: Next.js single-page application providing a ChatGPT-style conversational workbench, supporting streaming responses, markdown rendering, code syntax highlighting, copy-to-clipboard, image previews, and message editing.
- **User Experience**: Users type in an expanding prompt box, select assistants, upload attachments, view real-time tool progress badges, and receive verified answers with expandable citations.
- **Internal Mechanics**: Connects via Server-Sent Events (`/api/chat/send-message`). Receives chunked packets, appending markdown tokens in real time.
- **Key Modules**:
  - Frontend: `web/src/app/app/page.tsx`, `web/src/components/chat/ChatLayout.tsx`, `web/src/hooks/useChatStream.ts`
  - Backend: `backend/onyx/server/query_and_chat/chat_backend.py`, `backend/onyx/chat/process_message.py`

#### 2. Access to Major LLM Providers and Models
- **Description**: Unified gateway to 100+ language models with runtime switching, custom temperature/max_tokens parameters, and load balancing.
- **Supported Providers**: OpenAI, Azure OpenAI, Anthropic, Google Gemini / Vertex AI, AWS Bedrock, Cohere, Groq, Together AI, Mistral, Ollama, and self-hosted vLLM.
- **Key Modules**: `backend/onyx/llm/multi_llm.py`, `backend/onyx/llm/factory.py`, `backend/onyx/llm/model_catalog.py`

#### 3. Custom AI Agents (Personas)
- **Description**: Configurable AI assistants tailored for specific organizational roles.
- **Configuration Attributes**: System prompt, attached tools, assigned document sets, temperature, context token budget, and model overrides.
- **Key Modules**: `backend/onyx/server/features/persona/api.py`, `backend/onyx/db/persona.py`, `web/src/app/admin/personas/`

#### 4. Actions Through MCP (Model Context Protocol)
- **Description**: FastMCP client integration enabling the agent to dynamically discover and execute tools exposed by external servers over stdio or HTTP/SSE.
- **Key Modules**: `backend/onyx/tools/tool_implementations/mcp/`, `backend/onyx/server/features/mcp/api.py`

#### 5. OpenAPI Tool Actions
- **Description**: Custom tool definition where administrators upload OpenAPI 3.0 / Swagger JSON specifications; Onyx generates typed tool call schemas and executes HTTP API requests.
- **Key Modules**: `backend/onyx/tools/tool_implementations/custom/`

#### 6. Live Web Search
- **Description**: Web retrieval tool for questions requiring live public data.
- **Supported Providers**: SearXNG (self-hosted), Tavily, Bing Search API, Google Programmable Search.
- **Key Modules**: `backend/onyx/tools/tool_implementations/web_search/`, `backend/onyx/server/features/web_search/api.py`

#### 7. Deep Research
- **Description**: Autonomous multi-step research agent that executes iterative query generation, evaluates retrieved content, plans follow-up queries, and synthesizes long-form structured reports.
- **Key Modules**: `backend/onyx/deep_research/`, `backend/onyx/agents/agent_runtime.py`

#### 8. Python Code Interpreter Sandbox
- **Description**: Secure, isolated sandbox container for executing Python scripts generated by the agent, returning stdout/stderr and matplotlib visual charts.
- **Key Modules**: `backend/onyx/tools/tool_implementations/python/`, `backend/onyx/sandbox_proxy/`

#### 9. Image Generation
- **Description**: Generates images directly within chat conversations using DALL-E 3 or Google Imagen.
- **Key Modules**: `backend/onyx/image_gen/`, `backend/onyx/server/features/image_generation/api.py`

#### 10. Developer APIs
- **Description**: Comprehensive REST API with Swagger / OpenAPI documentation (`/docs`), personal access tokens (PAT), and API keys for external application integration.
- **Key Modules**: `backend/onyx/server/onyx_api/`, `backend/onyx/server/api_key/api.py`

#### 11. Query History, Tree Branching & Folders
- **Description**: Full conversation persistence allowing users to browse past chats, organize threads into folders, edit past turns to spawn alternative branch trees, and export transcripts.
- **Key Modules**: `backend/onyx/db/chat.py`, `backend/onyx/chat/save_chat.py`

#### 12. Usage Dashboards & Analytics
- **Description**: Auditing console displaying prompt/completion token consumption, API cost breakdown per model, active user queries, and search click-through telemetry.
- **Key Modules**: `backend/onyx/server/features/usage/api.py`, `backend/ee/onyx/server/analytics/`

---

### Section B: Knowledge and Integrations

#### 1. 40+ Application Connectors
- Connects directly to Google Drive, Confluence, Slack, GitHub, Jira, Notion, SharePoint, OneDrive, Salesforce, Zendesk, Hubspot, Box, Dropbox, S3, Web crawlers, and local files.
- Supports incremental polling, cursor pagination, rate-limit backoff, and full sync schedules.
- **Key Modules**: `backend/onyx/connectors/`, `backend/onyx/server/documents/connector.py`

#### 2. Document Processing & Extraction
- Multi-format text extractor handling PDFs, DOCX, PPTX, HTML, Markdown, CSV, and code files.
- Preserves document hierarchy, titles, section headers, and tabular structures.
- **Key Modules**: `backend/onyx/file_processing/`

#### 3. Semantic Chunking & Ingestion Pipeline
- Breaks documents into ~512 token segments with ~48 token overlap at natural paragraph and sentence boundaries.
- Prepend document title and path headers to every chunk to retain context.
- **Key Modules**: `backend/onyx/indexing/chunker.py`, `backend/onyx/indexing/indexing_pipeline.py`

#### 4. Hybrid Search Engine
- OpenSearch dual retrieval combining dense vector similarity (k-NN) and BM25 sparse keyword scoring with Reciprocal Rank Fusion (RRF).
- Pre-filters candidates by document sets and user access control lists (ACLs).
- **Key Modules**: `backend/onyx/document_index/opensearch/`

#### 5. RAG Context Packing & Compression
- Token budget management that greedily packs the highest-scoring passages into the prompt context window while enforcing reserved token ceilings for system prompts and history.
- **Key Modules**: `backend/onyx/chat/compression.py`, `backend/onyx/context/`

#### 6. Citations & Source Highlights
- Inline citation engine (`[[1]]`, `[[2]]`) matching generated claims against retrieved passage texts, providing direct links and highlight snippets.
- **Key Modules**: `backend/onyx/chat/citation_processor.py`

#### 7. Permission Synchronization (Enterprise)
- Periodically crawls upstream permission trees (e.g., Google Shared Drives, Confluence Space permissions) and mirrors them into OpenSearch `access_control_list` attributes.
- **Key Modules**: `backend/ee/onyx/external_permissions/`

#### 8. Slack & Discord Bots
- Workspace bots that respond to channel mentions, direct messages, or auto-answer specific channel questions using configured personas.
- **Key Modules**: `backend/onyx/onyxbot/slack/`, `backend/onyx/onyxbot/discord/`

#### 9. Event Hooks & Extensions
- Lifecycle hooks triggering custom callbacks on message creation, user signup, or document indexing.
- **Key Modules**: `backend/onyx/hooks/registry.py`

---

### Section C: Authentication and Security

#### 1. Authentication Options
- Local username/password (bcrypt), Google OAuth2, GitHub OAuth2, Microsoft Entra ID OAuth2, SAML 2.0 (Okta, OneLogin), and OIDC.
- **Key Modules**: `backend/onyx/auth/users.py`, `backend/onyx/server/saml_multi.py`

#### 2. Role-Based Access Control (RBAC)
- Built-in roles: `admin`, `global_curator`, `curator`, and `basic`.
- Scoped permissions governing connector configuration, document set curation, and persona creation.
- **Key Modules**: `backend/onyx/auth/permissions.py`, `backend/onyx/auth/scoped_permissions.py`

#### 3. Document-Level Access Control & Encryption
- Every indexed chunk carries an `access_control_list` array in OpenSearch.
- Connector credentials and API keys encrypted at rest using AES-GCM 256.
- **Key Modules**: `backend/onyx/access/`, `backend/onyx/db/credentials.py`

#### 4. Multi-Tenancy (Enterprise)
- Supports isolated PostgreSQL schemas (`tenant_<uuid>`) per enterprise customer with shared application binary execution.
- **Key Modules**: `backend/alembic_tenants/`, `backend/ee/onyx/multi_tenancy/`

---

### Section D: Enterprise and Administration

#### 1. Whitelabeling & Custom Theming
- Custom logo, application name, navigation links, and theme colors configurable through the admin panel.
- **Key Modules**: `backend/ee/onyx/server/whitelabeling/`, `web/src/ee/`

#### 2. Data Audit Exports
- Automated daily/weekly exports of chat logs, feedback ratings, user queries, and system events for compliance auditing.
- **Key Modules**: `backend/ee/onyx/server/analytics/`

#### 3. Stripe Invoice Billing & Subscription Tiers
- Tiered license verification, user seat counting, and automated Stripe checkout integration.
- **Key Modules**: `backend/ee/onyx/server/billing/`

