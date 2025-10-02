# Data Models

## Project

Represents a GitHub repository project synced into BMADFlow.

**Key Attributes:**
- `id`: UUID - Primary key
- `name`: string - Project name
- `github_url`: string - Full GitHub repository URL
- `last_sync_timestamp`: datetime
- `sync_status`: enum (`idle`, `syncing`, `error`)
- `sync_progress`: JSON - `{processed: int, total: int, current_file: string}`
- `created_at`: datetime
- `updated_at`: datetime

**TypeScript Interface:**
```typescript
interface Project {
  id: string; // UUID
  name: string;
  github_url: string;
  last_sync_timestamp: string | null;
  sync_status: 'idle' | 'syncing' | 'error';
  sync_progress: { processed: number; total: number; current_file?: string; } | null;
  created_at: string;
  updated_at: string;
}
```

**Relationships:** Has many `Document`

---

## Document

Represents a single markdown file from GitHub repository.

**Key Attributes:**
- `id`: UUID
- `project_id`: UUID (FK)
- `file_path`: string
- `content`: TEXT
- `doc_type`: enum (`scoping`, `architecture`, `epic`, `story`, `qa`, `other`)
- `title`: string
- `excerpt`: string
- `last_modified`: datetime
- `embedding`: vector(768) - pgvector embedding for semantic search (OLLAMA nomic-embed-text, Story 1.7)
- `extraction_status`: enum (`pending`, `processing`, `completed`, `failed`)
- `extraction_confidence`: float (0.0-1.0)
- `created_at`: datetime

**TypeScript Interface:**
```typescript
interface Document {
  id: string;
  project_id: string;
  file_path: string;
  content: string;
  doc_type: 'scoping' | 'architecture' | 'epic' | 'story' | 'qa' | 'other';
  title: string;
  excerpt: string;
  last_modified: string;
  extraction_status: 'pending' | 'processing' | 'completed' | 'failed';
  extraction_confidence: number;
  created_at: string;
}
```

**Relationships:** Belongs to `Project`, has one `ExtractedEpic` or `ExtractedStory`

---

## ExtractedEpic

Stores LLM-extracted structured data from epic markdown documents.

**Key Attributes:**
- `id`: UUID
- `document_id`: UUID (FK, one-to-one)
- `epic_number`: int
- `title`: string
- `goal`: TEXT
- `status`: enum (`draft`, `dev`, `done`)
- `story_count`: int
- `confidence_score`: float
- `extracted_at`: datetime

**TypeScript Interface:**
```typescript
interface ExtractedEpic {
  id: string;
  document_id: string;
  epic_number: number;
  title: string;
  goal: string;
  status: 'draft' | 'dev' | 'done';
  story_count: number;
  confidence_score: number;
  extracted_at: string;
}
```

**Relationships:** Belongs to `Document`, has many `ExtractedStory`

---

## ExtractedStory

Stores LLM-extracted user story components.

**Key Attributes:**
- `id`: UUID
- `document_id`: UUID (FK, one-to-one)
- `story_number`: string (e.g., "1.1", "2.3a")
- `role`: string
- `action`: TEXT
- `benefit`: TEXT
- `acceptance_criteria`: JSONB (array of strings)
- `status`: enum (`draft`, `dev`, `done`)
- `confidence_score`: float
- `extracted_at`: datetime

**TypeScript Interface:**
```typescript
interface ExtractedStory {
  id: string;
  document_id: string;
  story_number: string;
  role: string;
  action: string;
  benefit: string;
  acceptance_criteria: string[];
  status: 'draft' | 'dev' | 'done';
  confidence_score: number;
  extracted_at: string;
}
```

**Relationships:** Belongs to `Document` and `ExtractedEpic`

---

## Relationship

Models relationships between documents (epic → story).

**Key Attributes:**
- `id`: UUID
- `parent_doc_id`: UUID (FK)
- `child_doc_id`: UUID (FK)
- `relationship_type`: enum (`contains`, `relates_to`, `depends_on`)
- `created_at`: datetime

**TypeScript Interface:**
```typescript
interface Relationship {
  id: string;
  parent_doc_id: string;
  child_doc_id: string;
  relationship_type: 'contains' | 'relates_to' | 'depends_on';
  created_at: string;
}

interface GraphData {
  nodes: Array<{
    id: string;
    title: string;
    type: 'epic' | 'story';
    status: 'draft' | 'dev' | 'done';
    document_id: string;
  }>;
  edges: Array<{
    source_id: string;
    target_id: string;
    type: 'contains' | 'relates_to';
  }>;
}
```

---

## Embedding Dimension Configuration (Story 1.7)

**Critical Constraint:** The embedding dimension is **permanently locked** once database schema is created.

**Selected Configuration:**
- **Provider:** OLLAMA (local)
- **Model:** nomic-embed-text
- **Dimension:** **768**
- **pgvector Schema:** `embedding vector(768)`

**Rationale:**
- Privacy-first approach (40% weighting in decision criteria)
- Zero cost for local inference
- Sufficient capability for POC with qwen2.5:3b extraction model
- Can upgrade to qwen2.5:7b if accuracy improvement needed

**Migration Note:**
Switching to a different provider (e.g., LiteLLM with 1536-dimensional embeddings) requires:
1. Full database migration
2. Re-embedding all documents
3. Alembic migration to change vector dimension

**Environment Configuration:**
```bash
LLM_PROVIDER=ollama
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
OLLAMA_EMBEDDING_DIMENSION=768
```

---
