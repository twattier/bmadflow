# BMADFlow

**AI-Powered Documentation Chatbot with RAG Architecture**

BMADFlow is a proof-of-concept (POC) application that enables developers to interact with GitHub repository documentation using natural language. Built with FastAPI, React, PostgreSQL with pgvector, and Ollama for local embeddings, it provides an intelligent chat interface for exploring codebases.

## Project Overview

This application allows users to:
- Sync documentation from GitHub repositories
- Browse and search documentation with vector similarity
- Chat with an AI assistant that has context of your documentation
- Explore structured markdown, CSV, YAML, and JSON files

**Architecture**: Monorepo with Python FastAPI backend and React TypeScript frontend

## Prerequisites

Before getting started, ensure you have the following installed:

- **Docker Desktop** - For containerized PostgreSQL and pgAdmin
- **Python 3.11+** - Backend development
- **Node.js 18+** - Frontend development
- **Ollama** - Local LLM and embedding model hosting (with `nomic-embed-text` model)

### Install Ollama Model

```bash
ollama pull nomic-embed-text
```

## Backend Setup

### 1. Create Virtual Environment (Recommended)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 3. Verify Code Quality Tools

```bash
# Format check
black --check backend/

# Lint check
ruff check backend/
```

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Verify ESLint and Prettier

```bash
# Run linting
npm run lint
```

## Documentation

For detailed architecture, API specifications, and development guidelines, see:

- [Architecture Documentation](docs/architecture.md)
- [PRD](docs/prd.md)
- [User Stories](docs/stories/)
- [Tech Stack](docs/architecture/tech-stack.md)
- [Coding Standards](docs/architecture/coding-standards.md)

## Project Structure

```
bmadflow/
├── backend/          # Python FastAPI application
├── frontend/         # React TypeScript application
├── docs/             # Architecture and requirements documentation
└── README.md         # This file
```

## License

This is a proof-of-concept project for demonstration purposes.
