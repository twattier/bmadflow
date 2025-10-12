# Epic 5: Pre-Development Checklist

**Epic**: AI Chatbot Interface
**Status**: 🟢 Ready for Development
**Last Updated**: 2025-10-13

---

## ✅ Critical Decisions (ALL APPROVED)

- [x] **Decision 1**: Use LiteLLM library for multi-provider LLM support
- [x] **Decision 2**: Use Pydantic AI library for agent framework
- [x] **Decision 3**: Defer response streaming to Epic 6 (P1, not P0)
- [x] **Decision 4**: Auto-generate conversation titles from first message
- [x] **Decision 5**: Source panel replaces (one at a time, not stacked)

**All decisions documented in**: [epic-5-ai-chatbot-interface-UPDATED.md](../epics/epic-5-ai-chatbot-interface-UPDATED.md)

---

## 🔧 Environment Setup

### **1. Python Dependencies**

```bash
cd /home/wsluser/dev/bmad-test/bmadflow/backend

# Install LiteLLM (multi-provider LLM support)
pip install litellm

# Install Pydantic AI (agent framework)
pip install pydantic-ai

# Verify installation
python -c "import litellm; import pydantic_ai; print('Dependencies OK')"
```

**Expected Output**: `Dependencies OK`

- [ ] LiteLLM installed successfully
- [ ] Pydantic AI installed successfully
- [ ] Import test passed

---

### **2. Ollama Setup (Required for Story 5.2)**

```bash
# Check Ollama is running
curl http://localhost:11434/api/version

# Expected: {"version":"..."}
```

- [ ] Ollama service running (port 11434)

```bash
# Check llama3 model installed
ollama list | grep llama3

# If not found, pull model:
ollama pull llama3
```

- [ ] llama3 model installed

```bash
# Test model works
ollama run llama3 "Say hello"

# Expected: Friendly response from llama3
```

- [ ] llama3 model responds successfully

---

### **3. Environment Variables**

**Edit `.env` file** (add if not exists):

```bash
# Epic 5: LLM Configuration
OLLAMA_ENDPOINT_URL=http://localhost:11434

# Optional: Cloud LLM Providers (for Story 5.2b - multi-provider)
# OPENAI_API_KEY=sk-...          # OpenAI (optional)
# GOOGLE_API_KEY=...             # Google Gemini (optional)
# ANTHROPIC_API_KEY=...          # Anthropic Claude (optional)
```

- [ ] `OLLAMA_ENDPOINT_URL` set in `.env`
- [ ] `.env.example` updated with Epic 5 variables

---

### **4. Database Validation**

```bash
# Verify pgvector extension enabled (from Epic 4)
psql -h localhost -U postgres -d bmadflow -c "SELECT * FROM pg_extension WHERE extname = 'vector';"

# Expected: Row with extname='vector'
```

- [ ] pgvector extension enabled

```bash
# Verify Epic 4 tables exist
psql -h localhost -U postgres -d bmadflow -c "\dt chunks"

# Expected: Table "public.chunks"
```

- [ ] `chunks` table exists (Epic 4)

---

## 📚 Documentation Review

### **1. Epic 4 Handoff (CRITICAL)**

**Read**: [epic-4-to-epic-5-handoff.md](../handoffs/epic-4-to-epic-5-handoff.md)

**Key Sections**:
- [ ] Section 2: Vector Search API contract (`POST /api/projects/{id}/search`)
- [ ] Section 5.1: Session-per-task pattern for async operations (CRITICAL LEARNING)
- [ ] Section 6: Testing recommendations (concurrent operations)

**Vector Search API**:
```bash
# Test vector search endpoint
curl -X POST "http://localhost:8000/api/projects/{PROJECT_ID}/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "How does RAG work?", "top_k": 5}'

# Expected: 200 OK with results array
```

- [ ] Vector search API tested and working
- [ ] Understand response schema (chunk_id, document_id, header_anchor, similarity_score)

---

### **2. Epic 4 Retrospective**

**Read**: [epic-4-retrospective.md](../retrospectives/epic-4-retrospective.md)

**Key Learnings**:
- [ ] Session-per-task pattern for async operations (lines 260-318)
- [ ] Production validation non-negotiable (lines 322-332)
- [ ] Integration tests for concurrent operations (lines 236-240)

**Apply to Epic 5**:
- If Story 5.2 uses async parallelism → Use session-per-task pattern
- Production validate Story 5.2 with real Ollama (not just mocks)
- Integration tests for RAG agent (real vector search + LLM)

---

### **3. Epic 5 Updated Requirements**

**Read**: [epic-5-ai-chatbot-interface-UPDATED.md](../epics/epic-5-ai-chatbot-interface-UPDATED.md)

- [ ] All 6 stories reviewed
- [ ] Acceptance criteria understood
- [ ] Technical decisions internalized
- [ ] Database schema reviewed

---

## 🎯 Story Preparation

### **Story 5.1: LLM Provider Configuration**

**Required Reading**:
- [ ] Review existing Project model: `backend/app/models/project.py`
- [ ] Review existing Project schema: `backend/app/schemas/project.py`
- [ ] Review existing Project repository: `backend/app/repositories/project.py`
- [ ] Review existing Project router: `backend/app/routers/projects.py`

**Pattern to Follow**:
- Model: SQLAlchemy with UUID, ENUM, JSONB
- Schema: Pydantic BaseModel with Create/Update/Response variants
- Repository: CRUD methods (create, get_all, get_by_id, update, delete)
- Router: FastAPI endpoints with dependency injection

**Seed Script Reference**:
- [ ] Review seed pattern (if exists): `backend/scripts/`

---

### **Story 5.2: RAG Agent Framework**

**Required Reading**:
- [ ] LiteLLM documentation: https://docs.litellm.ai/docs/
- [ ] Pydantic AI documentation: https://ai.pydantic.dev/
- [ ] Epic 4 vector search implementation: `backend/app/api/v1/search.py`

**System Prompt Template** (define before Story 5.2):
```python
# backend/app/config/prompts.py

RAG_SYSTEM_PROMPT = """You are an AI assistant helping users understand project documentation.

Answer the user's question based on the provided context below.
Be concise and cite sources when possible.
If the context doesn't contain enough information to answer the question, say so clearly.

Context:
{context}

Question: {question}
"""
```

- [ ] System prompt template defined
- [ ] Understand LiteLLM completion API
- [ ] Understand Pydantic AI agent + tools pattern

---

### **Story 5.3: Chat API Endpoints**

**Required Reading**:
- [ ] Review migration pattern: `backend/alembic/versions/e43b4d239b48_create_projects_table.py`
- [ ] Review conversation title auto-generation logic (Epic 5 doc, Story 5.3 AC#4)

**Auto-Title Logic**:
```python
# Implement in POST /api/conversations/{id}/messages
if len(conversation.messages) == 1:  # First user message
    title = user_message.content[:50]
    if len(user_message.content) > 50:
        title += "..."
    conversation.title = title
    await db.commit()
```

- [ ] Auto-title logic understood
- [ ] JSONB sources schema understood

---

## 🧪 Testing Strategy

### **Backend Testing (Stories 5.1-5.3)**

**Requirements**:
- Minimum 70% test coverage (Epic 4 standard)
- Unit tests with mocked dependencies
- Integration tests with real services

**Test Structure**:
```
backend/tests/
├── unit/
│   ├── test_llm_provider_repository.py   # Story 5.1
│   ├── test_rag_agent_service.py          # Story 5.2 (mocked LLM)
│   └── test_conversation_repository.py    # Story 5.3
├── integration/
│   ├── test_llm_provider_api.py           # Story 5.1
│   ├── test_rag_agent_integration.py      # Story 5.2 (real Ollama)
│   └── test_conversation_api.py           # Story 5.3
```

- [ ] Understand pytest fixtures pattern
- [ ] Understand mocking strategy (respx for HTTP, AsyncMock for DB)

---

### **Frontend Testing (Stories 5.4-5.6)**

**Requirements**:
- Component tests with React Testing Library
- E2E test for happy path (Playwright)

**Test Coverage**:
- [ ] Chat UI: Message send, loading states, error handling
- [ ] Source panel: Open, close, anchor navigation
- [ ] History panel: Load conversations, resume

---

## 🚀 Quality Gates (Per Story)

### **Definition of Done - Each Story**

**Backend Stories (5.1-5.3)**:
- [ ] All acceptance criteria met
- [ ] >70% test coverage (unit + integration)
- [ ] Black + Ruff formatting (100% compliance)
- [ ] Type hints on all functions
- [ ] Google-style docstrings
- [ ] OpenAPI documentation updated
- [ ] Production validation with real services
- [ ] QA gate passed (submit for review)

**Frontend Stories (5.4-5.6)**:
- [ ] All acceptance criteria met
- [ ] Component tests passing
- [ ] E2E test for happy path
- [ ] Responsive design validated (mobile + desktop)
- [ ] shadcn/ui design system followed
- [ ] No console errors/warnings
- [ ] QA gate passed

---

## 📊 Architecture Validation

### **RAG Flow (End-to-End)**

Validate you understand this flow:

```
1. User types question in Chat UI (Story 5.4)
   ↓
2. Frontend: POST /api/conversations/{id}/messages
   ↓
3. Backend: Create user message record (Story 5.3)
   ↓
4. Backend: Call RAGAgentService.generate_response() (Story 5.2)
   ↓
5. RAG Agent: Tool call → vector_search (Epic 4 API)
   ↓
6. Epic 4: POST /api/projects/{id}/search → Returns top 5 chunks
   ↓
7. RAG Agent: Assemble context from chunks
   ↓
8. RAG Agent: LiteLLM completion(model, messages, context)
   ↓
9. LiteLLM: Call Ollama → Generate response
   ↓
10. RAG Agent: Format sources with document_id + header_anchor
   ↓
11. Backend: Save assistant message with sources (JSONB)
   ↓
12. Backend: Auto-generate conversation title (if first message)
   ↓
13. Backend: Return user_message + assistant_message to frontend
   ↓
14. Frontend: Display messages in chat
   ↓
15. Frontend: Render source links (Story 5.5)
   ↓
16. User clicks source → Open source panel with anchor scroll
```

- [ ] RAG flow understood end-to-end
- [ ] Identify potential failure points (Ollama down, vector search empty, etc.)

---

### **Database Schema**

Validate you understand relationships:

```
projects (Epic 2)
    ↓ (1:many)
conversations (Story 5.3)
    ├─ FK: project_id
    ├─ FK: llm_provider_id (Story 5.1)
    ↓ (1:many)
messages (Story 5.3)
    ├─ FK: conversation_id
    └─ sources (JSONB) → Contains document_id + header_anchor

llm_providers (Story 5.1)
    ↓ (1:many)
conversations
```

- [ ] Schema relationships understood
- [ ] CASCADE behavior understood (delete conversation → delete messages)
- [ ] SET NULL behavior understood (delete provider → conversations.llm_provider_id = NULL)

---

## 🎯 Risk Checklist

### **High Risk Items - MONITORED**

- [ ] **Story 5.2 Complexity**: Most complex story, multiple LLM integrations
  - **Mitigation**: Using proven libraries (LiteLLM, Pydantic AI)
  - **Fallback**: If Pydantic AI unstable, migrate to custom agent

- [ ] **LiteLLM Library**: External dependency, need to validate stability
  - **Mitigation**: Test with Ollama first, add unit tests with mocks

- [ ] **Pydantic AI Library**: New library (6 months old), may have edge cases
  - **Mitigation**: Comprehensive unit tests, integration tests with real Ollama

### **Medium Risk Items**

- [ ] **LLM API Costs**: Cloud providers (OpenAI, Google) charge per token
  - **Mitigation**: Start with Ollama (free), add cost monitoring later

- [ ] **Context Window Limits**: Different models have different token limits
  - **Mitigation**: Use `top_k=5` (conservative), truncate context if needed

### **Low Risk Items**

- [ ] Frontend UI complexity (Stories 5.4-5.6)
  - Standard patterns, shadcn/ui components, low complexity

---

## 📅 Timeline & Sequencing

### **Week 1: Backend Foundation**
- Day 1: Story 5.1 (LLM Provider Configuration)
- Day 2-3: Story 5.2 (RAG Agent Framework) - **HIGH COMPLEXITY**

### **Week 2: Chat Implementation**
- Day 4: Story 5.3 (Chat API Endpoints)
- Day 5: Story 5.4 (Chat UI)

### **Week 3: Advanced Features**
- Day 6-7: Story 5.5 (Source Attribution) - **HIGH COMPLEXITY**
- Day 8: Story 5.6 (Conversation History)

**Critical Path**: 5.1 → 5.2 → 5.3 → 5.4 → 5.5
**Parallelization**: After 5.3, can work 5.6 in parallel with 5.5 (saves ~1 day)

---

## ✅ Final Pre-Flight Check

**Before starting Story 5.1, confirm ALL of the following:**

### **Environment**
- [ ] LiteLLM installed (`pip install litellm`)
- [ ] Pydantic AI installed (`pip install pydantic-ai`)
- [ ] Ollama running (`curl http://localhost:11434/api/version`)
- [ ] llama3 model installed (`ollama list | grep llama3`)
- [ ] `.env` updated with `OLLAMA_ENDPOINT_URL`
- [ ] pgvector enabled (Epic 4 dependency)

### **Documentation**
- [ ] Epic 4 handoff read (vector search API contract)
- [ ] Epic 4 retrospective read (session-per-task pattern)
- [ ] Epic 5 updated requirements read (all 6 stories)
- [ ] System prompt template defined (Story 5.2 prep)

### **Code Review**
- [ ] Project model/schema/repository reviewed (patterns)
- [ ] Alembic migration pattern reviewed
- [ ] FastAPI router pattern reviewed
- [ ] Testing patterns understood (unit vs integration)

### **Decisions**
- [ ] All 5 critical decisions approved and documented
- [ ] Story 5.2 complexity acknowledged (highest risk)
- [ ] Quality gates defined (>70% backend coverage)
- [ ] Streaming deferred to Epic 6 (confirmed)

### **Team Alignment**
- [ ] PO approved Epic 5 start (this checklist)
- [ ] Dev ready to execute Story 5.1
- [ ] QA prepared for per-story gates

---

## 🚀 Ready to Start?

**If ALL checkboxes above are checked:**

✅ **YOU ARE READY TO START STORY 5.1**

**Next Step**: Execute Story 5.1 implementation plan
- Location: [epic-5-ai-chatbot-interface-UPDATED.md](../epics/epic-5-ai-chatbot-interface-UPDATED.md) → Story 5.1

**Estimated Time**: 1 day (6-8 hours)

---

**Good luck! 🚀**

---

**Checklist Status**: ✅ Complete
**Approved By**: Product Manager (John)
**Date**: 2025-10-13
**Next Review**: After Story 5.1 complete (QA gate)
