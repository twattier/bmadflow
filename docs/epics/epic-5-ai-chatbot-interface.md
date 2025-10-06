# Epic 5: AI Chatbot Interface

## Epic Goal

Create the chatbot UI with LLM provider selection, RAG-powered conversation, source attribution with header anchor navigation, conversation history, and sliding source panel.

## Stories

### Story 5.1: Build LLM Provider Configuration and Management

**As a** user,
**I want** to configure LLM providers globally,
**so that** I can select which models to use for chat.

**Acceptance Criteria:**
1. Alembic migration creates `llm_providers` table: id (UUID), provider_name (enum: openai, google, litellm, ollama), model_name (string), is_default (boolean), api_config (JSONB), created_at
2. REST API endpoints:
   - `GET /api/llm-providers` - List configured providers
   - `POST /api/llm-providers` - Add provider (validates required config)
   - `PUT /api/llm-providers/{id}` - Update provider
   - `DELETE /api/llm-providers/{id}` - Delete provider
   - `PUT /api/llm-providers/{id}/set-default` - Set as default
3. API configuration stored in JSONB (not API keys - those in .env)
4. Seed script creates default Ollama provider (llama2 model)
5. Unit tests for provider CRUD operations

---

### Story 5.2: Implement Pydantic Agent Framework for RAG

**As a** developer,
**I want** a Pydantic-based agent to handle RAG queries with tool interactions,
**so that** I can generate responses with source attribution.

**Acceptance Criteria:**
1. Pydantic agent defined with tools: vector_search, get_document_content
2. Agent workflow: receive query → use vector_search tool → retrieve chunks → generate response with LLM → format with source links
3. Source links formatted: `[filename.md](document_id)` or `[filename.md#section](document_id#anchor)` if header_anchor available
4. Agent returns: response_text, source_documents (list with document_id, file_path, header_anchor)
5. LLM client abstraction supports: OpenAI, Google Gemini, LiteLLM, Ollama
6. Unit tests with mocked LLM responses
7. Integration test: query agent, verify response + sources returned

---

### Story 5.3: Build Chat API Endpoints

**As a** developer,
**I want** REST API endpoints for chatbot conversations,
**so that** the frontend can send queries and receive responses.

**Acceptance Criteria:**
1. Alembic migration creates `conversations` table: id (UUID), project_id (FK), llm_provider_id (FK), title (string), created_at, updated_at
2. Alembic migration creates `messages` table: id (UUID), conversation_id (FK), role (enum: user, assistant), content (text), sources (JSONB array), created_at
3. REST API endpoints:
   - `POST /api/projects/{id}/conversations` - Create new conversation
   - `GET /api/projects/{id}/conversations` - List conversations (last 10)
   - `GET /api/conversations/{id}` - Get conversation with messages
   - `POST /api/conversations/{id}/messages` - Send message, get response (streaming optional)
   - `DELETE /api/conversations/{id}` - Delete conversation
4. Message endpoint calls Pydantic agent for response generation
5. Sources stored in messages table as JSONB array
6. Unit tests for conversation/message CRUD

---

### Story 5.4: Build Chat UI with LLM Provider Selection

**As a** user,
**I want** to start a chat conversation and select which LLM to use,
**so that** I can query my project documentation.

**Acceptance Criteria:**
1. Chat page accessible from Project sidebar navigation
2. "New Conversation" state shows: LLM provider dropdown (populated from configured providers), "Start Conversation" button, empty message input
3. LLM dropdown shows: provider name + model name (e.g., "Ollama - llama2", "OpenAI - GPT-4")
4. Default provider pre-selected
5. Starting conversation creates conversation record via API
6. Message input field with "Send" button
7. Send button disabled if input empty or conversation not started
8. Messages displayed in conversation: user messages (right-aligned), assistant messages (left-aligned)
9. Loading indicator shown while waiting for response
10. Empty state: "New Conversation - Select an LLM provider and ask a question about this project..."

---

### Story 5.5: Implement Source Attribution with Header Anchor Navigation

**As a** user,
**I want** AI responses to include source links that navigate to specific sections,
**so that** I can verify information in the original documents.

**Acceptance Criteria:**
1. Assistant messages display source links at bottom: "Sources: [prd.md#goals](link), [architecture.md#database](link)"
2. Clicking source link opens source panel (40% width) sliding in from right
3. Source panel displays: file path header with close button, document content rendered (markdown/CSV/etc), "Open in Explorer" button at bottom
4. If header_anchor exists: auto-scroll to section with anchor (smooth scroll, highlight section temporarily)
5. If header_anchor null: navigate to document root, show toast: "Navigated to document root (section anchor unavailable)"
6. Source panel stays open until user clicks close button or selects different source
7. User can scroll chat and send new messages while source panel open
8. Multiple source links supported (user can switch between sources)

---

### Story 5.6: Build Conversation History Panel

**As a** user,
**I want** to view my recent conversations and resume them,
**so that** I can continue previous discussions.

**Acceptance Criteria:**
1. "History" button in chat header opens history panel (40% width) sliding in from right
2. History panel displays last 10 conversations as cards
3. Each card shows: first user message (truncated to 50 chars), timestamp (relative: "2 hours ago"), LLM provider used
4. Cards sorted by most recent first
5. Clicking card loads conversation (messages populate chat area) and closes history panel
6. "New" button appears in header when viewing past conversation (creates new conversation)
7. Close button in panel header closes history panel
8. Empty state: "No conversation history yet. Start a new conversation to get started."

---

## Definition of Done

- [ ] All 6 stories completed with acceptance criteria met
- [ ] LLM providers configurable globally
- [ ] Chat UI allows LLM provider selection per conversation
- [ ] RAG agent generates responses with source attribution
- [ ] Source links navigate to specific document sections with header anchors
- [ ] Conversation history displays last 10 conversations
- [ ] Source panel slides in with rendered document content
- [ ] All API endpoints documented in OpenAPI/Swagger
- [ ] Unit and integration tests passing
- [ ] UI follows shadcn/ui design system
- [ ] Response streaming begins within 3s (cloud) or 10s (Ollama) per NFR2
