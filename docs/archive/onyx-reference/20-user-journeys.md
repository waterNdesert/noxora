# Major User Journeys & End-to-End Code Traces

This document traces six core user journeys through Onyx, following execution flow across the frontend, Next.js proxy, FastAPI API server, Celery background workers, PostgreSQL, and OpenSearch.

---

## Journey 1: User Registration & Authentication

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Browser as Next.js Web App
    participant Edge as Edge Proxy (web/src/proxy.ts)
    participant NextAPI as Next.js API Proxy
    participant Backend as FastAPI (backend/onyx/main.py)
    participant Auth as UserManager (backend/onyx/auth/users.py)
    participant DB as PostgreSQL (user table)

    User->>Browser: Enters email and password on /auth/register
    Browser->>NextAPI: POST /api/auth/register
    NextAPI->>Backend: Forward POST /api/auth/register
    Backend->>Auth: on_after_register() -> validate password & hash via bcrypt
    Auth->>DB: INSERT INTO "user" (email, hashed_password, role, is_active)
    DB-->>Auth: User record created (first user automatically becomes 'admin')
    Backend-->>NextAPI: 201 Created
    NextAPI-->>Browser: Registration Success

    User->>Browser: Enters credentials on /auth/login
    Browser->>NextAPI: POST /api/auth/jwt/login
    NextAPI->>Backend: Forward POST /api/auth/jwt/login
    Backend->>Auth: authenticate() -> verify bcrypt hash
    Auth->>Backend: Generate JWT token signed with USER_AUTH_SECRET
    Backend-->>NextAPI: Set-Cookie: fastapiusersauth=<JWT>; HttpOnly; SameSite=Lax
    NextAPI-->>Browser: 200 OK + Set-Cookie
    Browser->>Edge: Navigate to /app (with auth cookie)
    Edge->>Edge: Validate cookie presence -> Allow access
    Browser->>User: Display Chat Workbench
```

---

## Journey 2: Administrator Connects Google Drive

```mermaid
sequenceDiagram
    autonumber
    actor Admin
    participant UI as Admin Dashboard (/admin/connectors)
    participant API as FastAPI Connector Router
    participant CredStore as Credential Store (credentials.py)
    participant DB as PostgreSQL
    participant Celery as Celery Worker (indexing queue)
    participant Redis as Redis Queue

    Admin->>UI: Selects "Google Drive" connector & uploads Service Account JSON
    UI->>API: POST /api/manage/credential (JSON payload)
    API->>CredStore: encrypt_credential() using AES-GCM 256
    CredStore->>DB: INSERT INTO credential (credential_json_encrypted)
    DB-->>API: credential_id = 42

    Admin->>UI: Configures sync frequency (e.g., every 10 min) & folders
    UI->>API: POST /api/manage/connector
    API->>DB: INSERT INTO connector (source="google_drive", config={...})
    DB-->>API: connector_id = 15

    UI->>API: POST /api/manage/connector-credential-pair
    API->>DB: INSERT INTO connector_credential_pair (connector_id=15, credential_id=42)
    DB-->>API: cc_pair_id = 7
    API->>Redis: Enqueue initial sync job (task: "run_connector_indexing")
    API-->>UI: 200 OK (Connector Active)
```

---

## Journey 3: Ingestion, Chunking, Embedding & Indexing

```mermaid
sequenceDiagram
    autonumber
    participant Celery as Celery Indexing Worker
    participant Connector as GoogleDriveConnector
    participant Parser as File Extractor (extract_from_file.py)
    participant Chunker as ChunkyChunker (chunker.py)
    participant ModelServer as Indexing Model Server
    participant OpenSearch as OpenSearch (danswer_chunk)
    participant DB as PostgreSQL (document & index_attempt)

    Celery->>DB: INSERT INTO index_attempt (status='IN_PROGRESS', cc_pair_id=7)
    Celery->>Connector: poll_source(start_time, end_time)
    Connector->>Parser: Stream raw file bytes (PDF, DOCX)
    Parser-->>Connector: Yield extracted plain text and section hierarchy
    Connector-->>Celery: Yield Document(id="google_drive__file123", text=...)

    Celery->>Chunker: chunk_document(doc, chunk_size=512, overlap=48)
    Chunker-->>Celery: Return 14 Chunks (with prepended title metadata)

    Celery->>ModelServer: POST /encoder (Batch of 14 chunk texts)
    ModelServer-->>Celery: Return 14 x 1024-d float embeddings

    Celery->>OpenSearch: Bulk Index into "danswer_chunk"
    Note over OpenSearch: Store content, embeddings, metadata, and access_control_list

    Celery->>DB: UPSERT INTO document (id, title, link, doc_updated_at)
    Celery->>DB: UPDATE index_attempt SET status='SUCCESS', total_docs=1
```

---

## Journey 4: User Asks a Question (Search, RAG, Citations & Streaming)

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Browser as Web Browser (React 19)
    participant NextProxy as Next.js API Proxy
    participant ChatBackend as FastAPI chat_backend.py
    participant LLMLoop as LLM Loop (llm_loop.py)
    participant SearchTool as SearchTool (search_tool.py)
    participant OpenSearch as OpenSearch
    participant Reranker as Cross-Encoder Reranker
    participant LLM as External LLM (e.g. OpenAI / Claude)
    participant CitationProc as CitationProcessor
    participant DB as PostgreSQL

    User->>Browser: Types "What are our Q3 financial results?"
    Browser->>NextProxy: POST /api/chat/send-message (SSE stream)
    NextProxy->>ChatBackend: Forward POST /api/chat/send-message
    ChatBackend->>LLMLoop: run_llm_loop(user_query, persona_id)

    LLMLoop->>SearchTool: Invokes search tool with query
    SearchTool->>OpenSearch: Hybrid Query (BM25 + k-NN dense vector)
    Note over OpenSearch: Enforces bool.filter: access_control_list CONTAINS user_email
    OpenSearch-->>SearchTool: Top 50 candidate chunks
    SearchTool->>Reranker: Score (Query, Chunk) pairs
    Reranker-->>SearchTool: Top 5 ranked chunks
    SearchTool-->>LLMLoop: Injects top 5 chunks into LLM prompt

    LLMLoop->>LLM: Stream request with system prompt, history, and chunks
    loop Token Streaming
        LLM-->>LLMLoop: Token delta ("According", " to", " [[1]]", ...)
        LLMLoop->>CitationProc: Match citation markers to source metadata
        CitationProc-->>ChatBackend: Emit SSE packet (type="text", content="According to...")
        ChatBackend-->>NextProxy: Forward SSE line
        NextProxy-->>Browser: Flush to UI
        Browser->>User: Displays token + clickable citation pill
    end

    LLMLoop->>DB: INSERT INTO chat_message (prompt, response, citations, tokens)
    ChatBackend-->>Browser: Emit SSE packet (type="message_id", id="msg_987")
```

---

## Journey 5: Creating & Using a Custom AI Agent (Persona)

```mermaid
sequenceDiagram
    autonumber
    actor Curator
    participant UI as Admin / Curators Console
    participant API as Persona API (api.py)
    participant DB as PostgreSQL
    actor Employee
    participant ChatUI as /app Chat Interface
    participant ChatLoop as LLM Loop

    Curator->>UI: Clicks "New Assistant"
    UI->>Curator: Prompts for name, instructions, tools, and document sets
    Curator->>UI: Names "HR Policy Bot", attaches "HR Docs" set, enables Python & Search
    UI->>API: POST /api/admin/persona (payload)
    API->>DB: INSERT INTO persona, prompt, persona__document_set, persona__tool
    DB-->>API: persona_id = 12
    API-->>UI: 201 Created

    Employee->>ChatUI: Selects "HR Policy Bot" from assistant dropdown
    ChatUI->>API: POST /api/chat/create-chat-session (persona_id=12)
    API->>DB: INSERT INTO chat_session (persona_id=12, user_id=...)
    Employee->>ChatUI: Asks "How many vacation days do I get?"
    ChatUI->>ChatLoop: Execute turn with persona_id=12
    ChatLoop->>ChatLoop: Constrain search queries to "HR Docs" document set
    ChatLoop-->>Employee: Streams response adhering to custom HR instructions
```

---

## Journey 6: Administrative Auditing & Usage Tracking

```mermaid
sequenceDiagram
    autonumber
    actor Admin
    participant UI as Admin Analytics (/admin/analytics)
    participant UsageAPI as Usage API (server/features/usage/api.py)
    participant DB as PostgreSQL (llm_usage & chat_message)

    Admin->>UI: Opens "Usage & Cost" dashboard
    UI->>UsageAPI: GET /api/admin/usage/summary?time_range=30d
    UsageAPI->>DB: SELECT date_trunc('day', timestamp), sum(cost), sum(tokens) FROM llm_usage GROUP BY 1
    DB-->>UsageAPI: Daily cost aggregations
    UsageAPI->>DB: SELECT model_name, count(*), sum(cost) FROM llm_usage GROUP BY model_name
    DB-->>UsageAPI: Model distribution breakdown
    UsageAPI-->>UI: JSON summary payload
    UI->>Admin: Renders interactive cost charts and query volume graphs
```

