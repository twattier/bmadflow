# LLM Provider Evaluation

This directory contains scripts and data for evaluating LLM providers (OLLAMA vs LiteLLM proxy) for BMAD document extraction.

## Setup

1. Install dependencies:
```bash
pip install ollama openai psutil python-dotenv
```

2. Configure environment variables (see `.env.example`):
   - For OLLAMA: `OLLAMA_BASE_URL`, `OLLAMA_EXTRACTION_MODEL`, `OLLAMA_EMBEDDING_MODEL`
   - For LiteLLM: `OPENAI_BASE_URL`, `OPENAI_API_KEY`, `OPENAI_EXTRACTION_MODEL`, `OPENAI_EMBEDDING_MODEL`

## Test Dataset

The `test_data/` directory contains 10 BMAD documents for evaluation:
- **4 epics**: Varying complexity from medium to high
- **6 stories**: Mix of infrastructure, API, and UI stories

Selection criteria:
- **Diverse complexity**: From simple stories to complex multi-story epics
- **Representative content**: Covers different aspects (backend, frontend, database, API)
- **Real-world examples**: Actual BMAD project documentation

See `test_data/manifest.json` for full dataset details.

## Usage

### Test Provider Connectivity

```bash
python provider_evaluation.py --test-connection
```

Expected output (based on your configuration):
```
✅ OLLAMA connection successful
   Extraction model: <from OLLAMA_EXTRACTION_MODEL>
   Embedding model: <from OLLAMA_EMBEDDING_MODEL>
   Embedding dimension: <from OLLAMA_EMBEDDING_DIMENSION>d

✅ LiteLLM proxy connection successful
   Base URL: <from OPENAI_BASE_URL>
   Extraction model: <from OPENAI_EXTRACTION_MODEL>
   Embedding model: <from OPENAI_EMBEDDING_MODEL>
   Embedding dimension: <from OPENAI_EMBEDDING_DIMENSION>d
```

### Run Full Evaluation

```bash
python provider_evaluation.py --test-data test_data
```

This will:
1. Extract structured data from all 10 documents using both providers
2. Measure extraction accuracy, latency, and cost
3. Test embedding dimension compatibility
4. Generate evaluation report at `../../docs/llm-provider-evaluation.md`

## Evaluation Criteria

**Weighted Decision Factors:**
- **Privacy (40%)**: Data locality and transmission
- **Extraction Capability (30%)**: Accuracy of structured output
- **Cost (20%)**: Per-document inference cost
- **Latency (10%)**: Response time per document

## Critical Finding: Embedding Dimension Lock

⚠️ **IMPORTANT**: Different embedding models produce different vector dimensions:
- OLLAMA `nomic-embed-text`: **768 dimensions**
- OpenAI `text-embedding-ada-002`: **1536 dimensions**

PostgreSQL pgvector schema must commit to ONE dimension size. **Provider choice is permanent** unless you:
1. Wipe database and re-sync all documents, OR
2. Perform complex migration re-embedding all existing documents

## Provider Decision (Story 1.7)

**Selected Provider: OLLAMA (Local)**

**Rationale:**
- **Privacy (40% weight)**: Full local privacy, no external transmission
- **Cost (20% weight)**: $0 per inference (local)
- **Capability (30% weight)**: Sufficient for POC with qwen2.5:3b
- **Latency (10% weight)**: Fast local inference

**Configuration:**
```bash
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_EXTRACTION_MODEL=qwen2.5:3b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
OLLAMA_EMBEDDING_DIMENSION=768
```

**Database Schema:** `vector(768)` for pgvector embeddings

**Epic 2 Status:** ✅ UNBLOCKED - Provider configured, ready for content extraction

## Migration Implications

⚠️ **Provider choice is PERMANENT** unless full data re-sync occurs:

1. PostgreSQL pgvector schema is locked to `vector(768)` for OLLAMA embeddings
2. Switching to LiteLLM (1536d) requires:
   - Full database migration
   - Re-embedding all documents
   - Alembic migration to change vector dimension
3. Consider provider choice carefully before loading production data

## Evaluation Results

**Infrastructure Delivered (Tasks 1-2, 8):**
- ✅ Evaluation framework with provider abstraction
- ✅ Test dataset (10 BMAD documents)
- ✅ Backend configuration with auto-derived properties
- ✅ Architecture documentation updated
- ✅ Integration tests (66/66 backend tests passing)

**Evaluation Execution (Tasks 3-7):**
- Deferred per QA recommendation (Path A)
- Full evaluation can be run if data-driven validation needed
- Current provider decision based on story criteria (privacy-first)

**Quality Score:** 95/100 (QA gate: CONCERNS)

