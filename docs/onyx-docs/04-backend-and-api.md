# Backend & REST API Architecture

This document covers the FastAPI backend architecture, API routing design, middleware pipeline, exception handling, and core endpoints.

---

## 1. FastAPI Application Architecture

The core API server is defined in `backend/onyx/main.py` and executed via Uvicorn. It operates as a modular, asynchronous HTTP server structured around FastAPI routers.

### A. Lifecycle Management (`lifespan`)
In `backend/onyx/main.py`, the application lifecycle is managed using FastAPI's `@asynccontextmanager`:

```python
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # 1. Warm up database connections in read-write and read-only pools
    warm_up_connections()
    
    # 2. Verify and initialize auth secrets and rate limiters
    verify_user_auth_secret()
    await setup_auth_limiter()
    
    # 3. Seed initial settings, SAML/OIDC providers, and default persona
    seed_saml_provider_from_conf_dir()
    seed_jwt_settings_from_env()
    
    # 4. Start fleet telemetry in background thread
    start_telemetry()
    
    yield
    
    # Teardown: close database engines and Redis connection pools
    await close_auth_limiter()
    reset_sqlalchemy_async_engine()
```

### B. Middleware Pipeline Order
Inbound HTTP requests flow through a strict sequential stack of middleware:

1. **Request ID Middleware (`request_id_middleware`)**: Assigns a unique UUID to `request.state.request_id` and adds `X-Request-ID` to the response header.
2. **Endpoint Context Middleware (`add_endpoint_context_middleware`)**: Injects route parameters and endpoint tags into the logging context.
3. **Client IP Middleware (`ClientIPMiddleware`)**: Extracts genuine client IPs from `X-Forwarded-For` or reverse proxy headers.
4. **Latency Logging Middleware (`latency_logging_middleware`)**: Measures execution duration in milliseconds for slow query auditing (`LOG_ENDPOINT_LATENCY`).
5. **CORS Middleware (`CORSMiddleware`)**: Restricts cross-origin requests to configured domains (`CORS_ALLOWED_ORIGIN`).
6. **CAPTCHA Protection (`CaptchaCookieMiddleware`, `LoginCaptchaMiddleware`)**: Guards sensitive endpoints (login, signup, reset password) against credential-stuffing attacks.

---

## 2. API Route Hierarchy

All endpoints are registered under `APP_API_PREFIX` (default: `/api`) and categorized into functional routers:

### A. Authentication & User Management
- `POST /api/auth/register`: Local email/password registration.
- `POST /api/auth/jwt/login`: Issues a signed JWT access token in an HTTP-only cookie.
- `POST /api/auth/jwt/logout`: Clears the session cookie.
- `GET /api/users/me`: Returns profile, role (`admin`, `basic`, `curator`, `global_curator`), and permissions of the currently authenticated user.
- `GET /api/auth/oauth/authorize`: Initiates external OAuth2 flow (Google, GitHub, Microsoft).
- `GET /api/saml/login` & `POST /api/saml/acs`: SAML 2.0 Single Sign-On flow.

### B. Chat & Agent Execution (`backend/onyx/server/query_and_chat/chat_backend.py`)
- `POST /api/chat/create-chat-session`: Initializes a persistent conversation with an assigned Persona.
- `POST /api/chat/send-message`: **Core streaming chat endpoint**. Streams Server-Sent Events (SSE) representing LLM tokens, intermediate tool executions, citations, and metadata.
- `GET /api/chat/get-chat-session/{session_id}`: Retrieves full chat history and branches.
- `DELETE /api/chat/delete-chat-session/{session_id}`: Soft-deletes a conversation.
- `POST /api/chat/rename-chat-session`: Renames a chat thread (manually or via LLM auto-title generator).

### C. Search & Document Retrieval (`backend/onyx/server/features/search/api.py`)
- `POST /api/search/intent`: Pre-evaluates query intent to determine whether vector search, keyword search, or direct tool invocation is needed.
- `POST /api/search/hybrid-search`: Performs dual OpenSearch retrieval (BM25 + k-NN dense embeddings) followed by cross-encoder reranking.
- `GET /api/document-set`: Fetches user-accessible document sets used as query scoping filters.

### D. Connectors & Data Sources (`backend/onyx/server/documents/`)
- `GET /api/manage/connector`: Lists all registered connectors and their synchronization status.
- `POST /api/manage/connector`: Creates a new connector configuration.
- `POST /api/manage/credential`: Stores encrypted credentials (OAuth tokens, API keys).
- `POST /api/manage/connector/run-once`: Immediately schedules an on-demand synchronization pass in Celery.
- `GET /api/manage/document/indexing-status`: Monitors real-time chunking and indexing throughput.

### E. Personas & Assistants (`backend/onyx/server/features/persona/api.py`)
- `GET /api/persona`: Lists available personas with assigned system prompts, model overrides, and attached tools.
- `POST /api/admin/persona`: Admin/Curator endpoint to create or update custom assistants.

### F. Tools & MCP Management (`backend/onyx/server/features/tool/api.py`, `.../mcp/api.py`)
- `GET /api/tool`: Lists built-in tools (Search, Web Search, Python Code Interpreter).
- `POST /api/admin/mcp`: Registers an external Model Context Protocol server URL to dynamically import tools into Onyx.

---

## 3. Exception Handling Architecture

Onyx uses structured application exceptions mapped to clear HTTP status codes (`backend/onyx/error_handling/exceptions.py`):

```python
class OnyxException(Exception):
    def __init__(self, message: str, error_code: OnyxErrorCode = OnyxErrorCode.GENERAL_ERROR):
        self.message = message
        self.error_code = error_code
        super().__init__(message)
```

All unhandled exceptions produce a standardized JSON payload:
```json
{
  "detail": "Descriptive human-readable error message",
  "error_code": "CONNECTOR_AUTH_EXPIRED",
  "request_id": "8f8b3c9e-5e92-4f10-b98a-53096b42b918"
}
```
This guarantees that the Next.js frontend can parse error codes deterministically without brittle regex checks on raw error strings.

