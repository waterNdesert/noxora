# Glossary of Technical Terms

This glossary defines technical terms, project-specific concepts, and overloaded terminology in the Onyx codebase.

---

### **CC-Pair (Connector-Credential Pair)**
The primary entity linking a data source definition (`Connector`) to an authentication secret (`Credential`). Every ingestion job, sync schedule, and lock operates on a `cc_pair_id`.

### **Persona**
An AI assistant configured with a specific system prompt, model override, attached tools, and allowed document sets. Formerly termed "Assistant".

### **Turn**
A single request-response exchange in a conversation, consisting of a user prompt, any intermediate tool calls, and the final synthesized assistant message.

### **Document**
A logical entity ingested from an upstream source (e.g., a Google Doc, Slack message, Jira ticket, or webpage). Holds unique IDs, modification timestamps, links, and access control tokens.

### **Chunk**
A subdivision of a Document (typically 512 tokens with 48 tokens of overlap). Chunks are the atomic unit of retrieval stored in OpenSearch with vector embeddings.

### **Document Set**
A curated grouping of documents or CC-pairs created by administrators or curators. Used by users and personas to constrain search queries to specific topics or departments.

### **IndexAttempt**
A database record that tracks an ingestion run for a specific CC-Pair, capturing start time, finish time, document counts, and error logs.

### **RAG (Retrieval-Augmented Generation)**
The architectural pattern of searching for relevant knowledge chunks from a database and injecting them into the LLM's prompt before generating an answer.

### **Hybrid Search**
A search strategy combining sparse keyword retrieval (BM25) and dense semantic vector retrieval (k-NN) using reciprocal rank fusion or weighted scoring.

### **Cross-Encoder**
A neural network model (e.g., `ms-marco-MiniLM-L-6-v2`) that scores the relevance of a query-document pair simultaneously. Used in the reranking stage to reorder candidate search results.

### **Bi-Encoder / Embedding Model**
A model that independently encodes queries and text passages into dense vector embeddings (e.g., `BAAI/bge-large-en-v1.5`), enabling fast vector indexing and approximate nearest neighbor search.

### **Permission Sync**
The background process that inspects access control lists (ACLs) in external systems (like Google Drive or Confluence) and mirrors them into OpenSearch so users only see authorized documents.

### **MCP (Model Context Protocol)**
An open standard (developed by Anthropic) for connecting tools, prompts, and resources to AI coding agents and LLMs via stdio or HTTP/SSE transports.

### **LiteLLM**
The unified Python gateway library used by Onyx to interact with dozens of LLM providers (OpenAI, Anthropic, Gemini, Bedrock, Azure, Ollama) via a standardized interface.

### **Dynamic CE/EE Gating**
Onyx's design pattern (`backend/onyx/utils/variable_functionality.py`) that loads Enterprise Edition modules dynamically when an enterprise license is present, falling back to Community Edition implementations otherwise.

