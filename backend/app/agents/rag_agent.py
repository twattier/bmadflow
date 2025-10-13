"""RAG agent for document-grounded question answering."""

import logging
from typing import List
from uuid import UUID

from pydantic import Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base_agent import BaseAgent
from app.agents.prompts.rag_system_prompt import RAG_SYSTEM_PROMPT
from app.agents.tools.vector_search import ChunkResult, VectorSearchTool
from app.schemas.agent import RAGResponse, SourceAttribution
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class RAGAgent(BaseAgent):
    """RAG chatbot agent with tool access for document retrieval."""

    llm_provider_id: UUID = Field(..., description="LLM provider UUID")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of chunks to retrieve")

    async def process_query(self, user_message: str, db: AsyncSession) -> RAGResponse:
        """Process user query with RAG pipeline.

        Workflow:
        1. Use VectorSearchTool to retrieve relevant chunks
        2. Format chunks as context for LLM
        3. Call LLM with system prompt + context + user message
        4. Parse response and extract sources
        5. Return structured response with source attribution

        Args:
            user_message: User's question or query
            db: Database session

        Returns:
            RAGResponse with generated text and source attribution

        Raises:
            ConnectionError: If Ollama or LLM service unavailable
            ValueError: If LLM provider not found
        """
        logger.info(
            f"Processing RAG query for project {self.project_id}, "
            f"conversation {self.conversation_id}"
        )

        # Step 1: Retrieve relevant chunks using vector search
        search_tool = VectorSearchTool(query=user_message, top_k=self.top_k)
        chunks = await search_tool.execute(self.project_id, db)

        if not chunks:
            logger.warning(f"No relevant chunks found for query: {user_message[:100]}")
            return RAGResponse(
                response_text="I couldn't find any relevant information in the documentation to answer your question. Please try rephrasing or ask about a different topic.",
                sources=[],
            )

        logger.info(f"Retrieved {len(chunks)} relevant chunks")

        # Step 2: Format context for LLM
        context = self._format_context(chunks)

        # Step 3: Generate LLM response
        llm_service = LLMService()
        messages = [
            {"role": "system", "content": RAG_SYSTEM_PROMPT},
            {"role": "system", "content": f"Context from documentation:\n\n{context}"},
            {"role": "user", "content": user_message},
        ]

        try:
            response_text = await llm_service.generate_completion(
                self.llm_provider_id, messages, db
            )
        except Exception as e:
            logger.error(f"LLM completion failed: {e}", exc_info=True)
            raise

        # Step 4: Format source attribution
        sources = self._format_sources(chunks)

        logger.info(
            f"RAG query completed: generated {len(response_text)} chars "
            f"with {len(sources)} sources"
        )

        return RAGResponse(response_text=response_text, sources=sources)

    def _format_context(self, chunks: List[ChunkResult]) -> str:
        """Format chunks as context for LLM prompt.

        Args:
            chunks: List of ChunkResult objects from vector search

        Returns:
            Formatted context string with source references
        """
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            # Format source reference with header anchor if available
            filename = chunk.file_path.split("/")[-1]
            anchor = f"#{chunk.header_anchor}" if chunk.header_anchor else ""
            source_ref = f"{filename}{anchor}"

            context_parts.append(f"[Source {i}: {source_ref}]\n{chunk.chunk_text}\n")

        return "\n".join(context_parts)

    def _format_sources(self, chunks: List[ChunkResult]) -> List[SourceAttribution]:
        """Format source attribution for frontend display.

        Args:
            chunks: List of ChunkResult objects from vector search

        Returns:
            List of SourceAttribution objects with document IDs and anchors
        """
        return [
            SourceAttribution(
                document_id=chunk.document_id,
                file_path=chunk.file_path,
                header_anchor=chunk.header_anchor,
                similarity_score=chunk.similarity_score,
            )
            for chunk in chunks
        ]
