# Database Schema

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    github_url TEXT NOT NULL,
    last_sync_timestamp TIMESTAMP WITH TIME ZONE,
    sync_status VARCHAR(50) NOT NULL DEFAULT 'idle',
    sync_progress JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    content TEXT NOT NULL,
    doc_type VARCHAR(50) NOT NULL,
    title VARCHAR(500) NOT NULL,
    excerpt TEXT,
    last_modified TIMESTAMP WITH TIME ZONE,
    embedding vector(384),
    extraction_status VARCHAR(50) NOT NULL DEFAULT 'pending',
    extraction_confidence FLOAT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_project_file UNIQUE(project_id, file_path)
);

CREATE INDEX idx_documents_project_id ON documents(project_id);
CREATE INDEX idx_documents_doc_type ON documents(doc_type);
CREATE INDEX idx_documents_extraction_status ON documents(extraction_status);

CREATE TABLE extracted_epics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL UNIQUE REFERENCES documents(id) ON DELETE CASCADE,
    epic_number INTEGER,
    title VARCHAR(500) NOT NULL,
    goal TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    story_count INTEGER DEFAULT 0,
    confidence_score FLOAT,
    extracted_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_extracted_epics_document_id ON extracted_epics(document_id);

CREATE TABLE extracted_stories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL UNIQUE REFERENCES documents(id) ON DELETE CASCADE,
    story_number VARCHAR(50) NOT NULL,
    role VARCHAR(255),
    action TEXT,
    benefit TEXT,
    acceptance_criteria JSONB,
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    confidence_score FLOAT,
    extracted_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_extracted_stories_document_id ON extracted_stories(document_id);

CREATE TABLE relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_doc_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    child_doc_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    relationship_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_parent_child UNIQUE(parent_doc_id, child_doc_id, relationship_type),
    CONSTRAINT no_self_reference CHECK (parent_doc_id != child_doc_id)
);

CREATE INDEX idx_relationships_parent ON relationships(parent_doc_id);
CREATE INDEX idx_relationships_child ON relationships(child_doc_id);

CREATE TABLE feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    better_than_github BOOLEAN NOT NULL,
    favorite_feature VARCHAR(255),
    improvement_suggestions TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

---
