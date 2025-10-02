# LLM Provider Configuration Guide

This document describes the environment-based configuration for LLM provider evaluation.

## Configuration Files

All configuration is managed through environment variables in `.env` file:

```
bmadflow/
├── .env                    # Active configuration (gitignored)
├── .env.example            # Template with both provider options
└── scripts/llm-evaluation/
    ├── provider_evaluation.py   # Reads from environment
    ├── test_connection.py       # Reads from environment
    └── fetch_test_data.py       # Uses configured repo URL
```

## Environment Variables

### OLLAMA Provider (Local)

```bash
OLLAMA_BASE_URL=http://ollama:11434              # Container name or localhost
OLLAMA_EXTRACTION_MODEL=qwen2.5:3b               # Your extraction model
OLLAMA_EMBEDDING_MODEL=nomic-embed-text          # Your embedding model
OLLAMA_EMBEDDING_DIMENSION=768                   # Model's vector dimension
```

### LiteLLM Proxy Provider (Remote)

```bash
OPENAI_BASE_URL=https://llmproxy.ai.orange       # Your proxy endpoint
OPENAI_API_KEY=sk-xxxxx                          # Your API key
OPENAI_EXTRACTION_MODEL=openai/gpt-4.1           # Model via proxy
OPENAI_EMBEDDING_MODEL=openai/text-embedding-ada-002
OPENAI_EMBEDDING_DIMENSION=1536                  # Model's vector dimension
```

### Active Provider Selection

```bash
LLM_PROVIDER=ollama              # 'ollama' or 'openai'
```

**Note:** Embedding dimension is automatically derived from `LLM_PROVIDER`:
- `ollama` → uses `OLLAMA_EMBEDDING_DIMENSION` (768)
- `openai` → uses `OPENAI_EMBEDDING_DIMENSION` (1536)

## No Hardcoded Values

All scripts load configuration from environment:

- **provider_evaluation.py**: Uses `EvaluationConfig.from_env()` with sensible defaults
- **test_connection.py**: Loads via `load_dotenv()` with environment fallbacks
- **fetch_test_data.py**: Repository URL from variable (for documentation)

## Testing Configuration

```bash
# Test OLLAMA connection with your configured models
python test_connection.py

# Test both providers
python provider_evaluation.py --test-connection
```

Output will show your configured models, not hardcoded examples.

## Changing Configuration

1. Edit `.env` file with your values
2. No code changes needed
3. Scripts automatically use new configuration

## Critical: Embedding Dimension Lock

**⚠️ WARNING:** Once you choose a provider and load data into the database:

- PostgreSQL pgvector column is locked to that dimension (768 or 1536)
- Switching providers requires full database migration and re-embedding
- Choose `LLM_PROVIDER` carefully before initial data load
- The embedding dimension is automatically determined by your provider choice

## Default Fallbacks

Scripts provide sensible defaults if environment variables are missing:

| Variable | Default | Notes |
|----------|---------|-------|
| `OLLAMA_BASE_URL` | Auto-detect | `http://ollama:11434` in Docker, `http://localhost:11434` otherwise |
| `OLLAMA_EXTRACTION_MODEL` | `qwen2.5:3b` | Fallback only |
| `OLLAMA_EMBEDDING_MODEL` | `nomic-embed-text` | Fallback only |
| `OLLAMA_EMBEDDING_DIMENSION` | `768` | Fallback only |
| `OPENAI_EMBEDDING_DIMENSION` | `1536` | Fallback only |

**Best Practice:** Always set these explicitly in `.env` to avoid surprises.

