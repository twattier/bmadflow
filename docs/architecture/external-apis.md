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

## OLLAMA API (External Server)

- **Purpose:** LLM inference for extracting structured BMAD content
- **Documentation:** https://github.com/jmorganca/ollama/blob/main/docs/api.md
- **Base URL:** Configured via environment variable `OLLAMA_BASE_URL` (e.g., `http://your-ollama-server:11434`)
- **Authentication:** None (configure if your server requires it)
- **Rate Limits:** N/A (managed by your OLLAMA server)

**Key Endpoints:**
- `POST /api/generate` - Generate text completion
- `GET /api/tags` - List available models

**Integration Notes:**
- Use `ollama-python` library configured to point to external server
- 30-second timeout per document (configurable via `OLLAMA_TIMEOUT`)
- Your existing GPU-enabled OLLAMA server will be used
- Model selection (Llama 3 8B or Mistral 7B) from Story 1.7 benchmarking
- Backend connects to external OLLAMA server via HTTP API
- Network connectivity required between backend and OLLAMA server

---
