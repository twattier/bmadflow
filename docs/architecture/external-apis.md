# External APIs

## GitHub REST API v3

- **Purpose:** Fetch markdown files from public GitHub repositories
- **Documentation:** https://docs.github.com/en/rest
- **Base URL:** `https://api.github.com`
- **Authentication:** GitHub Personal Access Token (optional for POC, recommended)
- **Rate Limits:** 60 req/hr (unauthenticated), 5000 req/hr (authenticated)

**Key Endpoints:**
- `GET /repos/{owner}/{repo}/git/trees/{sha}?recursive=1` - Get repository tree
- `GET /repos/{owner}/{repo}/contents/{path}` - Get file contents

**Integration Notes:**
- Use PyGithub library for Python client
- Implement exponential backoff for rate limit errors
- Filter for `/docs` folder only

## OLLAMA API (Selected Provider - Story 1.7)

- **Purpose:** Local LLM inference for extracting structured BMAD content
- **Documentation:** https://github.com/jmorganca/ollama/blob/main/docs/api.md
- **Base URL:** Configured via `OLLAMA_BASE_URL` environment variable
  - Docker: `http://ollama:11434` (container networking)
  - Host: `http://localhost:11434`
- **Authentication:** None required (local server)
- **Rate Limits:** None (local inference)

**Selected Models (Story 1.7 Decision):**
- **Extraction Model:** `qwen2.5:3b` - Lightweight model for structured extraction
- **Embedding Model:** `nomic-embed-text` - 768-dimensional embeddings
- **Rationale:** Privacy-first (40% weight), zero cost, sufficient capability for POC

**Key Endpoints:**
- `POST /api/generate` - Generate text completion for extraction
- `POST /api/embeddings` - Generate embeddings for semantic search
- `GET /api/tags` - List available models

**Integration Notes:**
- Use `ollama` Python library (v0.3.0+)
- Auto-detects Docker environment (container name vs localhost)
- 30-second timeout per document (configurable via `OLLAMA_TIMEOUT`)
- Embedding dimension: **768** (locked for pgvector schema)
- Backend connects via Docker network (bmad-flow_bmadflow-network)

## LiteLLM Proxy (Alternative Provider - Not Selected)

- **Purpose:** OpenAI-compatible proxy for cloud LLM providers
- **Documentation:** https://docs.litellm.ai/docs/
- **Base URL:** Configured via `OPENAI_BASE_URL` environment variable
- **Authentication:** API key via `OPENAI_API_KEY`
- **Rate Limits:** Varies by backend provider

**Configuration Example:**
```bash
OPENAI_BASE_URL=https://llmproxy.ai.orange
OPENAI_API_KEY=sk-xxxxx
OPENAI_EXTRACTION_MODEL=openai/gpt-4.1
OPENAI_EMBEDDING_MODEL=openai/text-embedding-ada-002
```

**Integration Notes:**
- Uses OpenAI Python SDK with custom `base_url` parameter
- Provides OpenAI-compatible `/v1/chat/completions` and `/v1/embeddings` endpoints
- Embedding dimension: **1536** (OpenAI ada-002)
- **Not selected** for Story 1.7 due to privacy trade-off (40% weight)

---
