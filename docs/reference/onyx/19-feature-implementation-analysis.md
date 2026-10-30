# Feature Implementation Analysis & Code Traces

This document details the internal technical implementation of Onyx's primary features, citing exact frontend components, backend modules, database models, and execution functions.

---

## 1. Core Chat & Streaming RAG

### Overview
The heart of Onyx is its conversational search and reasoning loop. Users submit questions and receive streamed markdown responses with embedded citations, tool status cards, and thought processes.

### Component Trace:
- **Frontend Components**:
  - Main Page: `web/src/app/app/page.tsx`
  - Chat Container: `web/src/components/chat/ChatLayout.tsx`
  - Input Box: `web/src/components/chat/ChatInputBar.tsx`
  - Message Renderer: `web/src/components/chat/ChatMessage.tsx`
  - Streaming Hook: `web/src/hooks/useChatStream.ts`
- **Backend Modules**:
  - API Router: `backend/onyx/server/query_and_chat/chat_backend.py` (`@router.post("/send-message")`)
  - Orchestrator: `backend/onyx/chat/process_message.py` (`process_chat_message()`)
  - Execution Loop: `backend/onyx/chat/llm_loop.py` (`run_llm_loop()`)
  - Step Runner: `backend/onyx/chat/llm_step.py` (`execute_llm_step()`)
  - Citations: `backend/onyx/chat/citation_processor.py` (`CitationProcessor`)
  - Buffer & Emitter: `backend/onyx/chat/stream_buffer.py`, `backend/onyx/chat/emitter.py`
- **Database Models & Tables**:
  - `ChatSession` (`chat_session` table)
  - `ChatMessage` (`chat_message` table)
  - `ToolCall` (`tool_call` table)
  - `Persona` (`persona` table)
- **External Dependencies**:
  - OpenSearch (document retrieval)
  - External LLM API or local model server
  - Redis (pub/sub & session cache)
- **Tier & Status**: Community Edition (CE) | **Fully Implemented**

---

## 2. Multi-LLM Gateway & Provider Dispatcher

### Overview
Enables Onyx to route prompts to diverse model providers (OpenAI, Anthropic, Google Gemini, Bedrock, Azure, Cohere, Ollama) while maintaining token budgets, prompt caching, and cost accounting.

### Component Trace:
- **Frontend Components**:
  - Provider Selector: `web/src/components/chat/ModelSelector.tsx`
  - Admin LLM Configuration: `web/src/app/admin/models/page.tsx`
- **Backend Modules**:
  - Factory: `backend/onyx/llm/factory.py` (`get_default_llm()`, `get_llm_for_persona()`)
  - Dispatcher: `backend/onyx/llm/multi_llm.py` (`MultiLLM` class)
  - Capabilities & Context: `backend/onyx/llm/model_catalog.py`, `backend/onyx/llm/model_capabilities.py`
  - Cost Calculator: `backend/onyx/llm/cost.py` (`calculate_llm_cost()`)
  - Price Table: `backend/onyx/llm/price_table/`
- **Database Models & Tables**:
  - `LLMProvider` (`llm_provider` table)
  - `LLMUsage` (`llm_usage` table)
- **External Dependencies**:
  - `litellm` Python package
  - Provider HTTP APIs
- **Tier & Status**: Community Edition (CE) | **Fully Implemented**

---

## 3. Custom AI Personas & Assistants

### Overview
Allows creating specialized agents equipped with specific system prompts, attached document sets, specialized models, and tool access.

### Component Trace:
- **Frontend Components**:
  - Persona List: `web/src/app/admin/personas/page.tsx`
  - Persona Editor: `web/src/app/admin/personas/PersonaEditor.tsx`
  - Persona Selector: `web/src/components/chat/PersonaSelector.tsx`
- **Backend Modules**:
  - REST Endpoints: `backend/onyx/server/features/persona/api.py` (`@router.post("/persona")`, `@router.get("/persona")`)
  - CRUD Logic: `backend/onyx/db/persona.py` (`create_update_persona()`, `get_persona_by_id()`)
  - Context Resolver: `backend/onyx/context/persona_context.py`
- **Database Models & Tables**:
  - `Persona` (`persona` table)
  - `PersonaPrompt` (`prompt` table)
  - `PersonaTool` (`persona__tool` junction table)
  - `PersonaDocumentSet` (`persona__document_set` junction table)
- **Tier & Status**: Community Edition (CE) / Enterprise Edition (sharing & groups) | **Fully Implemented**

---

## 4. MCP (Model Context Protocol) & OpenAPI Custom Tools

### Overview
Connects external tools and REST APIs to the agent runtime via Anthropic's FastMCP protocol or raw OpenAPI 3.0 specifications.

### Component Trace:
- **Frontend Components**:
  - MCP Admin: `web/src/app/admin/mcp/page.tsx`
  - Custom Tool Editor: `web/src/app/admin/tools/CustomToolEditor.tsx`
- **Backend Modules**:
  - Admin Endpoints: `backend/onyx/server/features/mcp/api.py`, `backend/onyx/server/features/tool/api.py`
  - Schema Constructor: `backend/onyx/tools/tool_constructor.py` (`construct_tools()`)
  - MCP Client Implementation: `backend/onyx/tools/tool_implementations/mcp/mcp_tool.py`
  - Tool Invoker: `backend/onyx/tools/tool_runner.py` (`execute_tool_call()`)
- **Database Models & Tables**:
  - `MCPServer` (`mcp_server` table)
  - `Tool` (`tool` table)
- **External Dependencies**:
  - `mcp` SDK / FastMCP transport
- **Tier & Status**: Community Edition (CE) | **Fully Implemented**

---

## 5. Search Engine & Hybrid Retrieval

### Overview
Queries the `danswer_chunk` OpenSearch index using a combination of dense vector k-NN search and sparse BM25 keyword matching, followed by cross-encoder reranking.

### Component Trace:
- **Frontend Components**:
  - Search View: `web/src/app/app/search/page.tsx`
  - Document Preview Modal: `web/src/components/search/DocumentDisplay.tsx`
- **Backend Modules**:
  - Search Tool: `backend/onyx/tools/tool_implementations/search/search_tool.py` (`SearchTool.run()`)
  - OpenSearch Client: `backend/onyx/document_index/opensearch/opensearch_client.py`
  - Score Combiner: `backend/onyx/document_index/opensearch/hybrid_search.py` (Reciprocal Rank Fusion)
  - Reranker: `backend/onyx/natural_language_processing/search_nlp_helpers.py` (`cross_encoder_rerank()`)
- **Database Models & Tables**:
  - `Document` (`document` table)
  - `DocumentSet` (`document_set` table)
- **External Dependencies**:
  - OpenSearch 2.x
  - Model Server (Cross-encoder reranking)
- **Tier & Status**: Community Edition (CE) | **Fully Implemented**

---

## 6. Python Code Interpreter Sandbox

### Overview
Runs LLM-generated Python scripts in an isolated execution container to perform mathematical calculations, tabular data queries, and chart visualizations.

### Component Trace:
- **Frontend Components**:
  - Code Block Renderer: `web/src/components/chat/CodeBlock.tsx`
  - Visual Chart Viewer: `web/src/components/chat/ChartRenderer.tsx`
- **Backend Modules**:
  - Tool Implementation: `backend/onyx/tools/tool_implementations/python/python_tool.py`
  - Sandbox Proxy: `backend/onyx/sandbox_proxy/client.py`
- **External Dependencies**:
  - `code-interpreter` container (`deployment/docker_compose/docker-compose.yml`)
- **Tier & Status**: Community Edition (CE) | **Fully Implemented**

---

## 7. Web Search & Deep Research

### Overview
Provides live internet search integration and autonomous multi-turn deep research that iteratively queries, reads, refines, and generates reports.

### Component Trace:
- **Backend Modules**:
  - Web Search Tool: `backend/onyx/tools/tool_implementations/web_search/web_search_tool.py`
  - Provider Adapters: `backend/onyx/tools/tool_implementations/web_search/providers/` (SearXNG, Tavily, Bing)
  - Deep Research Agent: `backend/onyx/deep_research/deep_research_runner.py`
- **Tier & Status**: Community Edition (CE) | **Fully Implemented**

---

## 8. Document Ingestion Pipeline

### Overview
Asynchronously processes files from connectors: file extraction, cleaning, token chunking, dense vector embedding, and storage in OpenSearch and PostgreSQL.

### Component Trace:
- **Backend Modules**:
  - Orchestrator: `backend/onyx/indexing/indexing_pipeline.py` (`build_indexing_pipeline()`)
  - Chunker: `backend/onyx/indexing/chunker.py` (`ChunkyChunker`)
  - Embedder: `backend/onyx/indexing/embedder.py` (`DefaultEmbeddingEngine`)
  - File Processing: `backend/onyx/file_processing/extract_from_file.py`
  - OpenSearch Writer: `backend/onyx/document_index/opensearch/vector_db_insertion.py`
- **Database Models & Tables**:
  - `Document` (`document` table)
  - `IndexAttempt` (`index_attempt` table)
  - `ConnectorCredentialPair` (`connector_credential_pair` table)
- **Tier & Status**: Community Edition (CE) | **Fully Implemented**

---

## 9. Connectors & Credential Management

### Overview
Coordinates authentication and scheduled data synchronization across 40+ workplace platforms.

### Component Trace:
- **Backend Modules**:
  - Interfaces: `backend/onyx/connectors/interfaces.py` (`BaseConnector`, `PollConnector`, `LoadConnector`)
  - Factory & Registry: `backend/onyx/connectors/factory.py`, `backend/onyx/connectors/registry.py`
  - Credential Store: `backend/onyx/db/credentials.py` (`create_credential()`, `encrypt_credential()`)
  - Token Refresher: `backend/onyx/auth/oauth_refresher.py`
- **Database Models & Tables**:
  - `Connector` (`connector` table)
  - `Credential` (`credential` table)
  - `ConnectorCredentialPair` (`connector_credential_pair` table)
- **Tier & Status**: Community Edition (CE) | **Fully Implemented**

---

## 10. Slackbot & Discord Bot

### Overview
Interactive workplace bots that answer queries in channels, threads, or DMs with rich blocks and feedback buttons.

### Component Trace:
- **Backend Modules**:
  - Webhook Handlers: `backend/onyx/server/manage/slack_bot.py`, `backend/onyx/server/manage/discord_bot/`
  - Slack Core: `backend/onyx/onyxbot/slack/` (`process_slack_message()`, `tokens.py`)
  - Discord Core: `backend/onyx/onyxbot/discord/`
- **Database Models & Tables**:
  - `SlackBotConfig` (`slack_bot_config` table)
  - `SlackChannelConfig` (`slack_channel_config` table)
- **Tier & Status**: Community Edition (CE) | **Fully Implemented**

---

## 11. Authentication, SSO & RBAC

### Overview
Multi-provider identity verification supporting local accounts, social OAuth2, enterprise SAML 2.0, OIDC, and fine-grained roles.

### Component Trace:
- **Backend Modules**:
  - Identity Manager: `backend/onyx/auth/users.py` (`UserManager`, `fastapi_users`)
  - SAML Multi: `backend/onyx/server/saml_multi.py`
  - OIDC Multi: `backend/onyx/server/oidc_multi.py`
  - Permission Evaluator: `backend/onyx/auth/permissions.py` (`check_user_role()`)
- **Database Models & Tables**:
  - `User` (`user` table)
  - `OAuthAccount` (`oauth_account` table)
  - `SamlProvider` (`saml_provider` table)
  - `UserGroup` (`user_group` table)
- **Tier & Status**: Community Edition (Local/OAuth) / Enterprise Edition (SAML/OIDC/Groups) | **Fully Implemented**

---

## 12. Permission Synchronization & Multi-Tenancy

### Overview
Enterprise capabilities that mirror upstream access control lists into OpenSearch and provide tenant schema separation.

### Component Trace:
- **Backend Modules**:
  - Permission Sync Task: `backend/ee/onyx/external_permissions/` (`sync_permissions_for_cc_pair()`)
  - Multi-Tenancy Engine: `backend/alembic_tenants/`, `backend/ee/onyx/multi_tenancy/`
  - Context Routing: `shared_configs/contextvars.py` (`CURRENT_TENANT_ID_CONTEXTVAR`)
- **Database Models & Tables**:
  - `DocumentAccess` (`document_access` table)
  - `Tenant` (in public schema)
- **Tier & Status**: Enterprise Edition (EE) | **Fully Implemented**

