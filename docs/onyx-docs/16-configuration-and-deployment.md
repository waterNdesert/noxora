# Configuration & Production Deployment Guide

This guide details configuration settings, environment variables, production deployment options, TLS termination, and maintenance routines.

---

## 1. Key Environment Variables

Configurations are defined in `backend/onyx/configs/app_configs.py` and loaded from environment variables:

### Core Application & Web
| Variable | Default | Description |
| :--- | :--- | :--- |
| `WEB_DOMAIN` | `http://localhost:3000` | The public URL of the Onyx web interface. |
| `APP_API_PREFIX` | `/api` | Base URL path for all backend REST endpoints. |
| `USER_AUTH_SECRET` | *(Required)* | 32+ character secret key used to sign JWT session cookies. |
| `ENCRYPTION_KEY_SECRET` | *(Required)* | 32-byte key used to encrypt connector credentials at rest. |

### Database & Storage
| Variable | Default | Description |
| :--- | :--- | :--- |
| `POSTGRES_HOST` | `localhost` | PostgreSQL server hostname. |
| `POSTGRES_PORT` | `5432` | PostgreSQL server port. |
| `POSTGRES_DB` | `postgres` | Primary relational database name. |
| `POSTGRES_USER` | `postgres` | Database username. |
| `POSTGRES_PASSWORD` | `password` | Database password. |
| `REDIS_HOST` | `localhost` | Redis server hostname (used for Celery broker & cache). |
| `OPENSEARCH_HOST` | `localhost` | OpenSearch cluster hostname. |
| `OPENSEARCH_PORT` | `9200` | OpenSearch HTTP port. |

### LLM & Model Inference
| Variable | Default | Description |
| :--- | :--- | :--- |
| `GEN_AI_MODEL_PROVIDER` | `openai` | Default LLM provider (`openai`, `anthropic`, `azure`, `bedrock`). |
| `GEN_AI_MODEL_VERSION` | `gpt-4o` | Default chat model name. |
| `FAST_GEN_AI_MODEL_VERSION` | `gpt-4o-mini` | Fast model used for query intent classification and titling. |
| `DOCUMENT_ENCODER_MODEL` | `BAAI/bge-large-en-v1.5` | Dense vector embedding model name. |
| `INDEXING_MODEL_SERVER_HOST` | `indexing_model_server` | Hostname of the dedicated embedding worker server. |

---

## 2. Production Deployment Options

### Option 1: Docker Compose (Quick Single-Server Production)
Located in `deployment/docker_compose/`:

```bash
cd deployment/docker_compose

# 1. Generate production environment file
cp env.prod.template .env
# Edit .env with your domain name, secrets, and provider keys

# 2. Initialize Let's Encrypt SSL certificates (optional)
./init-letsencrypt.sh

# 3. Launch full stack
docker compose -f docker-compose.prod.yml up -d
```

This starts:
- Nginx reverse proxy (Ports 80/443 with automated SSL certificates)
- Next.js Web Server
- FastAPI API Server
- Celery Background Workers & Beat
- Local Model Inference Servers
- PostgreSQL 15, OpenSearch 2.x, Redis 7, MinIO

---

### Option 2: Kubernetes (Enterprise Production via Helm)
Located in `deployment/helm/`:

```bash
# 1. Add repository and inspect values
cd deployment/helm

# 2. Configure custom secrets and values
helm upgrade --install onyx ./charts/onyx \
  --namespace onyx --create-namespace \
  -f custom-values.yaml
```

**Helm Chart Architecture**:
- StatefulSets for PostgreSQL and OpenSearch (or connect to managed AWS RDS Aurora and Amazon OpenSearch Service).
- Deployments with Horizontal Pod Autoscalers (HPA) for `api-server` and `web-server`.
- Scalable Worker Deployments for Celery indexing queues.

---

### Option 3: Air-Gapped / Offline Environments
For secure enterprise environments without external internet access:
- Use `deployment/docker_compose/docker-compose.airgap-test.yml`.
- Configure local embedding models (`DOCUMENT_ENCODER_MODEL`) loaded from mounted local volumes.
- Connect Onyx to an on-premise LLM server (e.g., vLLM or Ollama) with `OPENAI_API_BASE=http://vllm:8000/v1`.

---

## 3. Maintenance & Backup Procedures

### PostgreSQL Backup
```bash
PGPASSWORD="$POSTGRES_PASSWORD" pg_dump -h localhost -U postgres -d postgres -F c -b -v -f onyx_db_backup.dump
```

### OpenSearch Snapshot
Register a snapshot repository (S3 or shared filesystem) and trigger snapshots via the OpenSearch REST API:
```bash
curl -X PUT "localhost:9200/_snapshot/onyx_backup/snapshot_1?wait_for_completion=true"
```

