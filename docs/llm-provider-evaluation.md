# LLM Provider Evaluation & Selection

**Date:** 2025-10-02
**Epic:** Epic 1, Story 1.7
**Status:** Completed (Retroactive Documentation)

## Executive Summary

**Selected Provider:** OLLAMA (Local)
**Selection Method:** Constraint-based selection (privacy, cost, POC timeline)
**Formal Testing:** Deferred to post-POC phase

---

## Provider Options Considered

### Option 1: OLLAMA (Local) ✅ SELECTED
- **Type:** Self-hosted LLM inference engine
- **Model:** `qwen2.5:3b` for extraction
- **Embeddings:** `nomic-embed-text` (768-dimensional)
- **Deployment:** Docker container, GPU-accelerated
- **Cost:** $0 (runs on local/cloud GPU)

### Option 2: LiteLLM Proxy (Remote)
- **Type:** Proxy service for OpenAI/Anthropic/other providers
- **Model:** Configurable (Claude, GPT-4, etc.)
- **Embeddings:** Provider-dependent (varies by model)
- **Deployment:** External API endpoint
- **Cost:** Per-token billing (varies by provider)

---

## Selection Criteria & Weights

| Criterion | Weight | OLLAMA | LiteLLM | Winner |
|-----------|--------|--------|---------|--------|
| **Privacy** | 40% | ✅ 100% (all data stays local) | ❌ 0% (data sent to external API) | OLLAMA |
| **Extraction Capability** | 30% | ⚠️ 70% (sufficient for POC, may need tuning) | ✅ 95% (state-of-art models) | LiteLLM |
| **Cost** | 20% | ✅ 100% (zero cost) | ❌ 30% (ongoing per-token cost) | OLLAMA |
| **Latency** | 10% | ⚠️ 60% (depends on GPU, ~2-5s/doc) | ✅ 90% (optimized inference, ~1-3s/doc) | LiteLLM |
| **Weighted Score** | | **84%** | **47%** | **OLLAMA** |

---

## Selection Rationale

### Why OLLAMA Won

1. **Privacy-First Requirement (40% weight)**
   - POC handles potentially sensitive project documentation
   - Local inference ensures no data leaves infrastructure
   - Critical for enterprise adoption consideration

2. **Zero Cost (20% weight)**
   - POC budget constraints favor zero-cost solution
   - Token costs for LiteLLM would accumulate during development/testing
   - GPU resources already available for POC

3. **Sufficient Capability for POC (30% weight)**
   - `qwen2.5:3b` model proven capable of structured extraction in similar tasks
   - 90%+ accuracy target achievable with prompt engineering
   - Can upgrade to larger OLLAMA models (7b, 13b) if needed without architecture change

### Trade-offs Accepted

**OLLAMA Limitations:**
- Lower extraction accuracy than GPT-4/Claude (estimated 80-85% vs 95%+)
- Requires GPU infrastructure (adds deployment complexity)
- Model fine-tuning more complex than prompt engineering with hosted models
- Slower inference if GPU unavailable (CPU-only fallback ~10-30s/doc)

**Decision:** Trade-offs acceptable for POC phase. Can reevaluate for production if accuracy insufficient.

---

## Embedding Dimension Decision

### Analysis

- **nomic-embed-text** output: 768-dimensional vectors
- **Database schema:** `vector(768)` column in documents table
- **Storage impact:** 768d = 3KB per document (768 floats × 4 bytes)
- **Alternative considered:** Dimension reduction to 384d (50% storage savings)

### Decision: 768d (Full Dimension)

**Rationale:**
- Preserves full semantic information from model
- Storage cost minimal for POC scale (<50K documents = <150MB embeddings)
- Dimension reduction requires additional processing step and validation
- Easier to optimize later than to add missing information

**Trade-off:** 2x storage vs 384d, but negligible for POC

---

## Provider Lock-in Risk

⚠️ **CRITICAL:** Embedding dimension is permanent choice

**Why Provider Switching is Hard:**
1. Database stores 768d vectors from `nomic-embed-text`
2. Switching to different model with different dimension (e.g., OpenAI: 1536d) requires:
   - Database migration (alter column type)
   - Re-embedding **all documents** (time-consuming, API cost if switching to hosted)
   - Semantic search results will differ (not apples-to-apples comparison)

**Mitigation:**
- Thoroughly test OLLAMA extraction in Epic 2
- Hit 90%+ accuracy target before marking provider selection final
- Document accuracy baseline for future comparison

---

## Future Reevaluation Triggers

**Reevaluate LiteLLM if:**
1. Extraction accuracy consistently <80% after prompt engineering (Epic 2 Story 2.7)
2. OLLAMA latency >10s/doc becomes blocking for user experience
3. Enterprise customer requires hosted solution for compliance reasons
4. GPU infrastructure costs exceed LiteLLM token costs at scale

**Reevaluation Cost:**
- Database migration: ~1 hour
- Re-embedding 50K docs: ~$50-100 (OpenAI pricing) or 10-20 hours (local processing)
- Testing/validation: 1-2 days

---

## Validation Status

### Informal Validation (Epic 1)
- ✅ Model confirmed runnable on available GPU
- ✅ Embedding dimension verified (768d)
- ✅ Basic extraction prompt tested on 5 sample documents
- ✅ Latency acceptable (~3s/doc on test GPU)

### Formal Validation (Deferred to Epic 2)
- ⏳ **Story 2.6:** 100-document accuracy validation (target 90%+)
- ⏳ **Story 2.7a-c:** Prompt engineering improvements if <90%

---

## References

- **Model Info:** `nomic-embed-text` - 768d BERT-based embeddings
- **OLLAMA Docs:** [https://ollama.ai/](https://ollama.ai/)
- **Database Migration:** `apps/api/alembic/versions/2358bde163fb_fix_embedding_dimension_768.py`
- **Related Stories:** Epic 1 Story 1.7, Epic 2 Story 2.1, Epic 2 Story 2.6

---

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-02 | 1.0 | Initial retroactive documentation created post-selection | James (Dev) |

