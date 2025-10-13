# Epic 5: AI Chatbot Interface

**Status**: ✅ **COMPLETE**
**Completion Date**: 2025-10-14
**Last Updated**: 2025-10-14
**Quality Score**: 93.5/100 (Excellent)
**Story Completion**: 6/6 Done (100%)
**Test Pass Rate**: 99.3% (174/179 tests passing)
**Retrospective**: [Epic 5 Retrospective](../retrospectives/epic-5-ai-chatbot-interface-retrospective.md)

---

## Epic Goal

Create the chatbot UI with LLM provider selection, RAG-powered conversation, source attribution with header anchor navigation, conversation history, and sliding source panel.

---

## 🎯 Critical Technical Decisions (APPROVED)

### **Decision 1: LLM Integration Strategy**
- ✅ **APPROVED**: Use **LiteLLM library** for multi-provider support
- **Rationale**: Unified API for 100+ providers, reduces custom code, faster implementation
- **Implementation**: `pip install litellm`
- **Impact**: Saves 2-3 days development time

### **Decision 2: Agent Framework**
- ✅ **APPROVED**: Use **Pydantic AI library** for agent implementation
- **Rationale**: Type-safe, lightweight, aligns with existing Pydantic usage in codebase
- **Implementation**: `pip install pydantic-ai`
- **Fallback**: If unstable, migrate to custom framework in Story 5.2

### **Decision 3: Response Streaming**
- ✅ **APPROVED**: **Defer streaming to Epic 6** (P1, not P0)
- **Rationale**: Reduces Epic 5 complexity, can optimize UX after validating RAG pipeline
- **Epic 5 Behavior**: Return full response (no streaming), show loading indicator
- **Epic 6 Enhancement**: Add SSE streaming support as Story 6.1

### **Decision 4: Conversation Title Generation**
- ✅ **APPROVED**: **Auto-generate from first user message** (first 50 chars)
- **Rationale**: Zero friction, meaningful titles, modern chatbot UX standard
- **Fallback**: If first message <10 chars, use "Conversation - {timestamp}"
- **Future**: Add manual edit in Epic 6 if requested

### **Decision 5: Source Panel Behavior**
- ✅ **APPROVED**: **Replace (one source panel at a time)**
- **Rationale**: Simpler UI, mobile-friendly, most users view one source at a time
- **Enhancement**: Add "Previous Source" button in panel header for quick back navigation
- **Future**: Consider tabs within panel if users request multi-source comparison

---

## Stories

### Story 5.1: Build LLM Provider Configuration and Management

**As a** user,
**I want** to configure LLM providers globally,
**so that** I can select which models to use for chat.

**Acceptance Criteria:**
1. Alembic migration creates `llm_providers` table:
   - `id` (UUID, primary key)
   - `provider_name` (ENUM: 'openai', 'google', 'litellm', 'ollama')
   - `model_name` (VARCHAR(255), e.g., 'llama3', 'gpt-4')
   - `is_default` (BOOLEAN, default: false)
   - `api_config` (JSONB, stores non-sensitive config like api_base, temperature)
   - `created_at` (TIMESTAMP)

2. REST API endpoints:
   - `GET /api/llm-providers` - List all configured providers
   - `POST /api/llm-providers` - Add provider (validates required config)
   - `PUT /api/llm-providers/{id}` - Update provider
   - `DELETE /api/llm-providers/{id}` - Delete provider (prevents deletion if is_default=true)
   - `PUT /api/llm-providers/{id}/set-default` - Set as default (unsets other defaults)

3. API configuration stored in JSONB (not API keys - those in .env):
   ```json
   {
     "api_base": "http://localhost:11434",
     "temperature": 0.7,
     "max_tokens": 500
   }
   ```

4. Seed script creates default Ollama provider:
   ```python
   # backend/scripts/seed_llm_providers.py
   {
     "provider_name": "ollama",
     "model_name": "llama3",
     "is_default": true,
     "api_config": {"api_base": "http://localhost:11434"}
   }
   ```

5. Unit tests for provider CRUD operations (>70% coverage)

**Technical Notes:**
- Use `ENUM` type for provider_name to enforce valid values
- Unique constraint on provider_name + model_name (prevent duplicates)
- Cascade behavior: Conversations FK to llm_providers (SET NULL on delete)

---

### Story 5.2: Implement Pydantic Agent Framework for RAG

**As a** developer,
**I want** a Pydantic-based agent to handle RAG queries with tool interactions,
**so that** I can generate responses with source attribution.

**Acceptance Criteria:**

1. **Pydantic AI agent defined** with tools:
   - `vector_search` - Queries Epic 4 vector search API
   - `get_document_content` - Retrieves full document content (optional, for follow-up)

2. **Agent workflow**:
   ```
   User Query → vector_search(query) → Get top 5 chunks
              → Assemble context from chunks
              → LLM call with system prompt + context + query
              → Parse response
              → Format source links
              → Return response + sources
   ```

3. **Source links formatted**:
   - With anchor: `[architecture.md#rag-pipeline](document_id#header_anchor)`
   - Without anchor: `[prd.md](document_id)`

4. **Agent returns structured response**:
   ```python
   {
     "response_text": "RAG works by...",
     "source_documents": [
       {
         "document_id": "uuid",
         "file_path": "docs/architecture.md",
         "file_name": "architecture.md",
         "header_anchor": "rag-pipeline",
         "similarity_score": 0.92
       }
     ]
   }
   ```

5. **LLM client abstraction using LiteLLM**:
   - Supports: OpenAI (gpt-4, gpt-3.5-turbo)
   - Supports: Google Gemini (gemini-pro)
   - Supports: Ollama (llama3, mistral)
   - Supports: LiteLLM proxy (any model)

   ```python
   from litellm import completion

   response = completion(
       model=f"{provider}/{model_name}",
       messages=[{"role": "system", "content": system_prompt},
                 {"role": "user", "content": query}],
       api_base=api_config.get("api_base"),
       temperature=api_config.get("temperature", 0.7)
   )
   ```

6. **System prompt for RAG** (defined in config/prompts.py):
   ```
   You are an AI assistant helping users understand project documentation.

   Answer the user's question based on the provided context.
   Be concise and cite sources when possible.
   If the context doesn't contain enough information, say so.

   Context:
   {context_chunks}

   Question: {user_question}
   ```

7. **Unit tests** with mocked LLM responses (use `respx` for HTTP mocking)

8. **Integration test**: Query agent with real Ollama, verify response structure + sources

**Technical Notes:**
- **No streaming in Epic 5** - return full response (streaming deferred to Epic 6)
- Use `top_k=5` for vector search (balance between context and token usage)
- Context assembly: Join chunks with `\n\n---\n\n` separator
- Error handling: If vector search fails, return error message (no LLM call)
- Install: `pip install pydantic-ai litellm`

**Implementation Strategy:**
```python
# app/services/rag_agent_service.py
from pydantic_ai import Agent
from litellm import completion

class RAGAgentService:
    def __init__(self, llm_provider_id: UUID):
        self.provider = get_llm_provider(llm_provider_id)
        self.agent = self._create_agent()

    def _create_agent(self):
        return Agent(
            model=f"{self.provider.provider_name}/{self.provider.model_name}",
            tools=[self.vector_search_tool]
        )

    async def generate_response(self, project_id: UUID, query: str):
        # Tool execution → LLM call → Response formatting
        ...
```

---

### Story 5.3: Build Chat API Endpoints

**As a** developer,
**I want** REST API endpoints for chatbot conversations,
**so that** the frontend can send queries and receive responses.

**Acceptance Criteria:**

1. **Alembic migration creates `conversations` table**:
   - `id` (UUID, primary key)
   - `project_id` (UUID, FK to projects, ON DELETE CASCADE)
   - `llm_provider_id` (UUID, FK to llm_providers, ON DELETE SET NULL)
   - `title` (VARCHAR(255), auto-generated from first message)
   - `created_at` (TIMESTAMP)
   - `updated_at` (TIMESTAMP)

2. **Alembic migration creates `messages` table**:
   - `id` (UUID, primary key)
   - `conversation_id` (UUID, FK to conversations, ON DELETE CASCADE)
   - `role` (ENUM: 'user', 'assistant')
   - `content` (TEXT)
   - `sources` (JSONB array, nullable, for assistant messages only)
   - `created_at` (TIMESTAMP)

3. **REST API endpoints**:

   **POST `/api/projects/{project_id}/conversations`**
   - Request: `{"llm_provider_id": "uuid"}`
   - Response: `{"id": "uuid", "project_id": "uuid", "llm_provider_id": "uuid", "title": null, "created_at": "..."}`
   - Creates conversation with null title (set on first message)

   **GET `/api/projects/{project_id}/conversations`**
   - Response: Last 10 conversations ordered by `updated_at DESC`
   - Includes: `id`, `title`, `created_at`, `updated_at`, `llm_provider` (joined)

   **GET `/api/conversations/{conversation_id}`**
   - Response: Conversation with all messages (ordered by `created_at ASC`)
   - Includes: Full message history with sources

   **POST `/api/conversations/{conversation_id}/messages`**
   - Request: `{"content": "How does RAG work?"}`
   - Response: `{"user_message": {...}, "assistant_message": {...}}`
   - Workflow:
     1. Create user message record
     2. Call RAGAgentService.generate_response()
     3. Create assistant message record with sources
     4. **If first message**: Auto-generate conversation title (first 50 chars of user message)
     5. Return both messages

   **DELETE `/api/conversations/{conversation_id}`**
   - Soft delete (or hard delete with CASCADE)
   - Returns 204 No Content

4. **Conversation title auto-generation** (on first message):
   ```python
   if conversation.messages.count() == 1:  # First user message
       title = user_message.content[:50]
       if len(user_message.content) > 50:
           title += "..."
       conversation.title = title
   ```

5. **Sources stored in JSONB**:
   ```json
   [
     {
       "document_id": "uuid",
       "file_path": "docs/architecture.md",
       "file_name": "architecture.md",
       "header_anchor": "rag-pipeline",
       "similarity_score": 0.92
     }
   ]
   ```

6. **Unit tests** for conversation/message CRUD (>70% coverage)

7. **Integration test**: Create conversation → Send message → Verify agent called → Check sources

**Technical Notes:**
- **No streaming** - return full response synchronously
- Error handling: If agent fails, save user message but return 500 error
- Conversation title fallback: If first message <10 chars, use "Conversation - {timestamp}"

---

### Story 5.4: Build Chat UI with LLM Provider Selection

**As a** user,
**I want** to start a chat conversation and select which LLM to use,
**so that** I can query my project documentation.

**Acceptance Criteria:**

1. Chat page accessible from Project sidebar navigation (new route: `/projects/{id}/chat`)

2. **"New Conversation" state** shows:
   - LLM provider dropdown (populated from `GET /api/llm-providers`)
   - "Start Conversation" button (calls `POST /api/projects/{id}/conversations`)
   - Message input field (disabled until conversation started)
   - Empty state message (AC#10)

3. **LLM dropdown** shows:
   - Format: `{provider_name} - {model_name}` (e.g., "Ollama - llama3", "OpenAI - gpt-4")
   - Default provider pre-selected (where `is_default=true`)

4. **Starting conversation**:
   - User clicks "Start Conversation" → API call → Conversation ID received
   - Message input becomes enabled
   - Dropdown disappears (LLM locked for conversation)

5. **Message input field**:
   - Text area with "Send" button
   - Enter key sends message (Shift+Enter for new line)
   - Max length: 2000 characters (with counter)

6. **Send button behavior**:
   - Disabled if: input empty OR conversation not started OR waiting for response
   - Enabled when: input has text AND conversation started AND not loading

7. **Messages displayed**:
   - User messages: Right-aligned, blue background
   - Assistant messages: Left-aligned, gray background
   - Timestamp below each message (relative: "2 minutes ago")
   - Loading indicator while waiting for assistant response

8. **Loading indicator**:
   - Animated dots: "Assistant is typing..."
   - Shown after Send clicked, hidden when response received

9. **Empty state** (before conversation started):
   ```
   🤖 New Conversation

   Select an LLM provider and ask a question about this project's documentation.
   ```

10. **Error handling**:
    - If message send fails: Show toast "Failed to send message. Please try again."
    - Retry button appears next to failed message

**Technical Notes:**
- Use shadcn/ui components: `Select`, `Button`, `Textarea`, `ScrollArea`
- Polling NOT needed (no streaming, response returned synchronously)
- Auto-scroll to bottom on new message
- Conversation persists: If user navigates away and returns, load existing conversation

---

### Story 5.5: Implement Source Attribution with Header Anchor Navigation

**As a** user,
**I want** AI responses to include source links that navigate to specific sections,
**so that** I can verify information in the original documents.

**Acceptance Criteria:**

1. **Assistant messages display source links** at bottom:
   ```
   Sources: [prd.md#goals](link), [architecture.md#database](link), [readme.md](link)
   ```
   - Format: Markdown-style links
   - Clicking link opens source panel (AC#2)

2. **Source panel** (40% width) slides in from right:
   - Animation: Smooth 300ms slide-in
   - Panel overlays chat area (chat becomes 60% width)
   - Panel has white background, border-left

3. **Source panel displays**:
   - Header: File path (e.g., "docs/architecture.md") + Close button (X)
   - Body: Document content rendered (markdown → MarkdownRenderer, CSV → table, etc.)
   - Footer: "Open in Explorer" button (navigates to `/projects/{id}/docs/{doc_id}`)

4. **If header_anchor exists**:
   - Auto-scroll to section with anchor (smooth scroll behavior)
   - Highlight section temporarily (yellow background fade-out over 2s)
   - Scroll position: Anchor at top of visible area

5. **If header_anchor is null**:
   - Navigate to document root (no scroll)
   - Show toast: "Navigated to document root (section anchor unavailable)"

6. **Source panel behavior**:
   - Clicking different source: **Replaces** current source (panel updates, doesn't stack)
   - Close button: Closes panel, chat returns to 100% width
   - Panel stays open while user scrolls chat or sends new messages

7. **Chat interaction while panel open**:
   - User can scroll chat messages
   - User can send new messages
   - New assistant responses appear in chat (panel stays open)

8. **Multiple source links**:
   - Each source is a clickable link
   - User clicks Source A → panel shows Source A
   - User clicks Source B → panel updates to Source B (Source A closes)
   - Enhancement: Add "Previous Source" button in panel header (quick back navigation)

**Technical Notes:**
- Reuse `MarkdownRenderer` component from Epic 3 (Story 3.6)
- Header anchor format: GitHub-style (e.g., `#rag-pipeline-architecture`)
- Scroll to anchor: Use `document.getElementById(anchor).scrollIntoView({behavior: 'smooth'})`
- Highlight effect: CSS animation with `@keyframes` (fade yellow → transparent)
- Panel state: Store in React context or Zustand store (persists across message sends)

**Implementation:**
```tsx
// Panel component
<SourcePanel
  documentId={currentSource.document_id}
  anchor={currentSource.header_anchor}
  onClose={() => setCurrentSource(null)}
/>

// Anchor scrolling
useEffect(() => {
  if (anchor) {
    const element = document.getElementById(anchor);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
      element.classList.add('highlight-fade');
    } else {
      toast("Navigated to document root (section anchor unavailable)");
    }
  }
}, [anchor]);
```

---

### Story 5.6: Build Conversation History Panel

**As a** user,
**I want** to view my recent conversations and resume them,
**so that** I can continue previous discussions.

**Acceptance Criteria:**

1. **"History" button** in chat header:
   - Icon: Clock or history icon
   - Clicking opens history panel (40% width) sliding in from right

2. **History panel displays** last 10 conversations:
   - Fetched from `GET /api/projects/{id}/conversations`
   - Displayed as cards in vertical list

3. **Each card shows**:
   - **Title**: Conversation title (truncated to 50 chars if longer)
   - **Timestamp**: Relative format ("2 hours ago", "Yesterday", "3 days ago")
   - **LLM Provider**: Badge showing provider + model (e.g., "Ollama - llama3")

4. **Cards sorted** by most recent first (`updated_at DESC`)

5. **Clicking card**:
   - Loads conversation via `GET /api/conversations/{id}`
   - Messages populate chat area
   - History panel closes automatically
   - Chat UI updates to show loaded conversation

6. **"New" button** in header:
   - Only appears when viewing past conversation (not on new conversation)
   - Clicking creates new conversation (resets to "New Conversation" state)

7. **Close button** in panel header:
   - Clicking closes history panel
   - Chat remains unchanged

8. **Empty state** (if no conversations):
   ```
   📜 No conversation history yet

   Start a new conversation to get started.
   ```

**Technical Notes:**
- History panel and Source panel share the same slot (only one can be open at a time)
- If Source panel open when History clicked → close Source, open History
- Relative timestamps: Use `date-fns` library (`formatDistanceToNow()`)
- Card hover effect: Slight elevation shadow
- Smooth slide-in animation (300ms)

---

## Definition of Done

**Epic 5 Complete When:**

- [x] All 6 stories completed with acceptance criteria met ✅
- [x] **Backend (Stories 5.1-5.3)**:
  - [x] LLM providers configurable via REST API ✅
  - [x] Pydantic AI agent with LiteLLM integration working ✅
  - [x] Chat API endpoints functional (conversations + messages) ✅
  - [x] Conversation titles auto-generated from first message ✅
  - [x] >70% test coverage (unit + integration) - 92-94% achieved ✅
  - [x] OpenAPI documentation complete ✅
- [x] **Frontend (Stories 5.4-5.6)**:
  - [x] Chat UI with LLM provider selection ✅
  - [x] Source panel with header anchor navigation (replace behavior) ✅
  - [x] Conversation history panel (last 10) ✅
  - [x] UI follows shadcn/ui design system ✅
  - [x] Component tests passing - 19-24 tests per story ✅
- [x] **Integration**:
  - [x] RAG agent generates responses with source attribution ✅
  - [x] Source links navigate to Documentation Explorer with anchors ✅
  - [x] E2E test: Create conversation → Send message → View source → Resume conversation ✅
- [x] **Performance**:
  - [x] Response time <10s for Ollama (local LLM) ✅
  - [x] Response time <5s for cloud LLMs (OpenAI, Google) ✅
  - [x] Vector search <500ms (validated in Epic 4) ✅
- [x] **Deferred to Epic 6**:
  - ⏸️ Response streaming (P1, not P0) - Confirmed deferred
  - ⏸️ Manual conversation title editing - Confirmed deferred
  - ⏸️ Source panel tabs (multi-source comparison) - Confirmed deferred

**Epic Completion Summary:**
- **Stories Delivered**: 6/6 (100%)
- **Average Quality Score**: 93.5/100
- **Total Tests**: 179 (174 passing, 99.3% pass rate)
- **Duration**: 2 days (vs estimated 6 days - 67% faster)
- **Critical Issues**: 0
- **Retrospective**: [View Epic 5 Retrospective](../retrospectives/epic-5-ai-chatbot-interface-retrospective.md)

---

## Pre-Development Checklist

**Complete before starting Story 5.1:**

### Environment Setup
- [ ] Install LiteLLM: `pip install litellm`
- [ ] Install Pydantic AI: `pip install pydantic-ai`
- [ ] Add to `.env`:
  ```bash
  # Ollama (required for Story 5.2)
  OLLAMA_ENDPOINT_URL=http://localhost:11434

  # Optional: Other LLM providers
  OPENAI_API_KEY=sk-...  # Optional
  GOOGLE_API_KEY=...     # Optional
  ```
- [ ] Verify Ollama running: `ollama list | grep llama3` (pull if needed)
- [ ] Verify Ollama model: `ollama run llama3 "test"` (should respond)

### Documentation
- [ ] Review Epic 4 handoff document (vector search API contract)
- [ ] Review Epic 4 retrospective (session-per-task pattern, testing guidelines)
- [ ] Define system prompt template for RAG (see Story 5.2 AC#6)
- [ ] Create Epic 5 architecture diagram (optional but recommended)

### Validation
- [ ] Test vector search API: `curl -X POST http://localhost:8000/api/projects/{id}/search -d '{"query":"test","top_k":5}'`
- [ ] Confirm pgvector enabled: `psql -c "SELECT * FROM pg_extension WHERE extname='vector'"`
- [ ] Verify Epic 1-4 functionality stable (no regressions)

### Team Alignment
- [ ] All 5 critical decisions approved (✅ DONE)
- [ ] Story 5.2 complexity acknowledged (highest risk story)
- [ ] Quality gates defined: >70% backend coverage, unit tests for frontend
- [ ] Streaming deferred to Epic 6 (confirmed)

---

## Technical Architecture

### RAG Flow (Story 5.2)
```
User Query
    ↓
Frontend: POST /api/conversations/{id}/messages
    ↓
Backend: Message endpoint
    ↓
RAG Agent Service
    ↓
Tool: vector_search
    ↓
Epic 4: POST /api/projects/{id}/search (top_k=5)
    ↓
Context Assembly (join chunks with separator)
    ↓
LiteLLM: completion(model, messages, context)
    ↓
Response + Source Attribution
    ↓
Format sources with document_id + header_anchor
    ↓
Save assistant message with sources (JSONB)
    ↓
Return to frontend
    ↓
Frontend: Display message + source links
```

### Database Schema
```
llm_providers (Story 5.1)
├─ id (UUID, PK)
├─ provider_name (ENUM: openai, google, litellm, ollama)
├─ model_name (VARCHAR)
├─ is_default (BOOLEAN)
├─ api_config (JSONB)
└─ created_at (TIMESTAMP)

conversations (Story 5.3)
├─ id (UUID, PK)
├─ project_id (UUID, FK → projects)
├─ llm_provider_id (UUID, FK → llm_providers, SET NULL)
├─ title (VARCHAR, auto-generated)
├─ created_at (TIMESTAMP)
└─ updated_at (TIMESTAMP)

messages (Story 5.3)
├─ id (UUID, PK)
├─ conversation_id (UUID, FK → conversations, CASCADE)
├─ role (ENUM: user, assistant)
├─ content (TEXT)
├─ sources (JSONB, nullable)
└─ created_at (TIMESTAMP)
```

---

## Risk Management

### High Risk - Mitigated
- ✅ **Story 5.2 Complexity**: Using proven libraries (LiteLLM, Pydantic AI) reduces risk
- ✅ **Multiple LLM Providers**: Start with Ollama (simplest), add others incrementally
- ✅ **Streaming Complexity**: Deferred to Epic 6, reduces scope

### Medium Risk - Monitored
- ⚠️ **Pydantic AI Library**: New library (6 months old), may have edge cases
  - **Mitigation**: Comprehensive unit tests, fallback to custom agent if needed
- ⚠️ **LLM API Costs**: Cloud providers (OpenAI, Google) charge per token
  - **Mitigation**: Start with Ollama (free), add cost monitoring in Epic 6
- ⚠️ **Context Window Limits**: Different models have different token limits
  - **Mitigation**: Use `top_k=5` (conservative), truncate if needed

### Low Risk
- ✅ **Frontend UI**: Standard patterns, shadcn/ui components, low complexity
- ✅ **Database Schema**: Simple CRUD, follows existing patterns
- ✅ **Epic 4 Integration**: Vector search API validated, 100% ready

---

## Success Metrics

**Epic 5 Success = Meeting These Targets:**

| Metric | Target | How Measured |
|--------|--------|--------------|
| **Story Completion** | 6/6 (100%) | All ACs met, QA approved |
| **Test Coverage** | >70% backend | pytest --cov |
| **Response Time** | <10s Ollama, <5s cloud | Production testing |
| **Quality Score** | >90/100 avg | QA gate per story |
| **Zero Blocking Issues** | 0 critical bugs | QA validation |
| **RAG Accuracy** | 80%+ relevant responses | Manual testing with 20 queries |

---

## Next Steps

**You are now ready to start Story 5.1!** 🚀

**Story 5.1 Execution Plan:**
1. Create Alembic migration for `llm_providers` table
2. Create `LLMProvider` SQLAlchemy model
3. Create Pydantic schemas (LLMProviderCreate, LLMProviderResponse, etc.)
4. Create `LLMProviderRepository` with CRUD operations
5. Create REST API endpoints in `app/routers/llm_providers.py`
6. Create seed script: `backend/scripts/seed_llm_providers.py`
7. Write unit tests (>70% coverage)
8. Production validation: Test all CRUD endpoints
9. QA gate: Submit for review

**Estimated Time**: 1 day (6-8 hours)

---

**Document Status**: ✅ Final - Ready for Development
**Approved By**: Product Manager (John)
**Date**: 2025-10-13
**Next Review**: After Story 5.3 complete (mid-epic checkpoint)
