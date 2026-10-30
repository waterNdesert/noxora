# Technical Requirements & System Specifications

This document outlines the infrastructure, software dependencies, network requirements, performance benchmarks, and security compliance standards needed to rebuild and operate an Onyx-equivalent platform.

---

## 1. Hardware & Infrastructure Specifications

| Component | Minimal Evaluation Scale (< 50 Users) | Enterprise Production Scale (> 500 Users, Millions of Docs) |
| :--- | :--- | :--- |
| **API & Web Servers** | 2 vCPUs, 4 GB RAM | 8+ vCPUs, 16+ GB RAM (Autoscaling Pods) |
| **Celery Workers** | 2 vCPUs, 4 GB RAM | 16+ vCPUs, 32+ GB RAM (Partitioned Queues) |
| **PostgreSQL Database** | 2 vCPUs, 4 GB RAM, 50 GB SSD | 8 vCPUs, 32 GB RAM, 500+ GB NVMe (Multi-AZ Replica) |
| **OpenSearch Cluster** | 2 vCPUs, 8 GB RAM, 100 GB SSD | 3 Master + 4 Data Nodes (32 GB RAM, 1+ TB NVMe each) |
| **Redis Cache / Broker** | 1 vCPU, 2 GB RAM | 2 Nodes Cluster (8 GB RAM each) |
| **Model Server (Embeddings)**| 2 vCPUs, 4 GB RAM (CPU) | 1x NVIDIA T4 or A10G GPU (16 GB VRAM) |
| **Blob Storage (MinIO/S3)** | 20 GB Local Storage | AWS S3 / Cloudflare R2 (Pay-as-you-go) |

---

## 2. Software & Runtime Dependencies

| Technology | Supported / Tested Versions | Role in Architecture |
| :--- | :--- | :--- |
| **Python** | `3.13+` | FastAPI server, Celery workers, model server |
| **Node.js** | `22.x` or `24.x` (LTS) | Next.js 16 frontend build and runtime |
| **PostgreSQL** | `15+` or `16+` | Authoritative relational data plane |
| **OpenSearch** | `2.11+` | Dense vector k-NN and sparse BM25 retrieval |
| **Redis** | `7.0+` | Message broker, distributed locks, session cache |
| **Docker Engine** | `24.0+` | Container runtime |
| **Kubernetes** | `1.28+` | Enterprise container orchestration |

---

## 3. Network Egress & Firewall Allowlist

To operate external connectors, LLMs, and telemetry, the following egress ports and domains must be accessible:

| Service | Target Destination / Ports | Purpose |
| :--- | :--- | :--- |
| **OpenAI API** | `api.openai.com:443` | LLM inference, embedding generation |
| **Anthropic API** | `api.anthropic.com:443` | Claude LLM reasoning |
| **Google Cloud APIs** | `*.googleapis.com:443` | Google Drive connector, Gemini LLM |
| **Microsoft Graph** | `graph.microsoft.com:443` | OneDrive, SharePoint, Teams connectors |
| **Slack API** | `slack.com/api:443` | Slack connector and Slackbot events |
| **Hugging Face Hub** | `huggingface.co:443` | Downloading local embedding & reranker weights |
| **AWS Endpoints** | `*.amazonaws.com:443` | S3 blob storage, Bedrock inference, SES email |

---

## 4. Performance & Latency Benchmarks (SLAs)

| Operation | Target Latency / Throughput | Notes |
| :--- | :--- | :--- |
| **First Token Latency (TTFT)** | `< 800 ms` | From user message dispatch to initial streamed token |
| **Hybrid Search Retrieval** | `< 250 ms` | Combined OpenSearch BM25 + k-NN retrieval |
| **Cross-Encoder Reranking** | `< 150 ms` | Rescoring top 50 passages (GPU-accelerated) |
| **Ingestion Throughput** | `> 50 docs/sec` | Batch tokenization, chunking, and vector indexing |
| **API Server Concurrency** | `> 500 req/sec` | Stateless read requests per 4-core worker |

---

## 5. Security & Compliance Standards

1. **Encryption at Rest**:
   - AES-GCM 256-bit encryption for all stored connector credentials and OAuth secrets (`backend/onyx/db/credentials.py`).
   - PostgreSQL and OpenSearch volume encryption via LUKS or AWS KMS.
2. **Encryption in Transit**:
   - TLS 1.3 enforced across all public endpoints and inter-service HTTP communications.
3. **Data Retention & Privacy**:
   - Zero retention for external LLM API payloads (contractual opt-out with OpenAI / Anthropic).
   - Document deletion propagates immediately to OpenSearch and PostgreSQL.
4. **Audit Logging**:
   - Every administrative action, role elevation, and user query is recorded in persistent audit logs (`docs/AUDIT_LOGGING.md`).

