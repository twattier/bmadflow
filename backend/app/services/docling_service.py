"""Docling document processing service.

This service handles document chunking using Docling's HybridChunker with
HuggingFace tokenization for optimal RAG performance.
"""

import logging
from typing import List

from app.schemas.chunk import ChunkProcessed
from app.utils.markdown_parser import extract_headers, find_nearest_header

logger = logging.getLogger(__name__)


class DoclingService:
    """Service for processing documents into chunks using Docling.

    Uses Docling's HybridChunker with HuggingFace tokenization to split
    documents into semantically meaningful chunks while respecting token limits.

    Attributes:
        chunker: Docling HybridChunker instance configured with tokenization
    """

    def __init__(self):
        """Initialize DoclingService with HybridChunker.

        Configures HybridChunker with HuggingFace tokenizer using the
        all-MiniLM-L6-v2 model to match embedding tokenization strategy.
        """
        try:
            from docling.chunking import HybridChunker
            from docling_core.transforms.chunker.tokenizer.huggingface import (
                HuggingFaceTokenizer,
            )
            from transformers import AutoTokenizer

            # Initialize HuggingFace tokenizer for all-MiniLM-L6-v2
            hf_tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
            tokenizer = HuggingFaceTokenizer(
                tokenizer=hf_tokenizer, max_tokens=512  # Chunk size in tokens
            )

            # Initialize HybridChunker with tokenizer
            self.chunker = HybridChunker(tokenizer=tokenizer, merge_peers=True)

            logger.info(
                "DoclingService initialized with HybridChunker and all-MiniLM-L6-v2 tokenizer"
            )

        except ImportError as e:
            logger.error(f"Failed to import Docling dependencies: {e}")
            raise RuntimeError("Docling is not installed. Install with: pip install docling") from e

    async def process_markdown(self, content: str) -> List[ChunkProcessed]:
        """Process markdown content into chunks with header anchor extraction.

        Loads markdown content, extracts H1-H3 headers, chunks using HybridChunker,
        and associates each chunk with its nearest preceding header anchor for
        precise document navigation.

        Args:
            content: Raw markdown content as string

        Returns:
            List of ChunkProcessed objects with text, index, metadata, and header_anchor

        Raises:
            ValueError: If content is empty or invalid
        """
        if not content or not content.strip():
            raise ValueError("Markdown content cannot be empty")

        try:
            from docling.datamodel.base_models import InputFormat
            from docling.document_converter import DocumentConverter

            # Extract headers before chunking for anchor generation
            headers = extract_headers(content)
            logger.info(f"Extracted {len(headers)} headers from markdown content")

            # Convert markdown to Docling document
            converter = DocumentConverter()
            result = converter.convert_string(
                content, format=InputFormat.MD, name="markdown_content"
            )
            doc = result.document

            # Chunk the document
            chunks = list(self.chunker.chunk(dl_doc=doc))

            logger.info(f"Generated {len(chunks)} chunks from markdown content")

            # Convert to ChunkProcessed objects with header anchors
            chunk_responses = []
            for idx, chunk in enumerate(chunks):
                # Determine chunk position in document
                # Try to get position from Docling metadata first
                chunk_position = 0
                if (
                    chunk.meta.doc_items
                    and chunk.meta.doc_items[0].prov
                    and hasattr(chunk.meta.doc_items[0].prov[0], "charspan")
                ):
                    chunk_position = chunk.meta.doc_items[0].prov[0].charspan.start
                else:
                    # Fallback: Find position by searching for chunk text in original content
                    # Use first 50 chars of chunk text to find position
                    search_text = chunk.text[:50].strip()
                    if search_text:
                        pos = content.find(search_text)
                        if pos != -1:
                            chunk_position = pos

                # Find nearest preceding header anchor
                header_anchor = find_nearest_header(chunk_position, headers)

                if header_anchor:
                    logger.debug(
                        f"Chunk {idx} at position {chunk_position} → anchor: {header_anchor}"
                    )

                chunk_responses.append(
                    ChunkProcessed(
                        text=chunk.text,
                        index=idx,
                        header_anchor=header_anchor,  # Add header anchor field
                        metadata={
                            "file_type": "md",
                            "position": chunk_position,
                            "total_chunks": len(chunks),
                            "headers": (
                                [
                                    item.label
                                    for item in chunk.meta.headings
                                    if hasattr(item, "label")
                                ]
                                if hasattr(chunk.meta, "headings")
                                and chunk.meta.headings is not None
                                else []
                            ),
                        },
                    )
                )

            return chunk_responses

        except Exception as e:
            logger.error(f"Error processing markdown content: {e}")
            raise

    async def process_csv(self, content: str) -> List[ChunkProcessed]:
        """Process CSV content into chunks.

        Parses CSV with Docling and chunks by rows or logical groups,
        preserving header information in metadata.

        Args:
            content: Raw CSV content as string

        Returns:
            List of ChunkProcessed objects with text, index, and metadata

        Raises:
            ValueError: If content is empty or invalid CSV format
        """
        if not content or not content.strip():
            raise ValueError("CSV content cannot be empty")

        try:
            from docling.datamodel.base_models import InputFormat
            from docling.document_converter import DocumentConverter

            # Convert CSV to Docling document
            # Docling's convert_string only supports MD/HTML, treat CSV as markdown
            converter = DocumentConverter()
            result = converter.convert_string(content, format=InputFormat.MD, name="csv_content.md")
            doc = result.document

            # Chunk the document
            chunks = list(self.chunker.chunk(dl_doc=doc))

            logger.info(f"Generated {len(chunks)} chunks from CSV content")

            # Convert to ChunkResponse objects
            chunk_responses = []
            for idx, chunk in enumerate(chunks):
                chunk_responses.append(
                    ChunkProcessed(
                        text=chunk.text,
                        index=idx,
                        header_anchor=None,  # CSV files don't have markdown headers
                        metadata={
                            "file_type": "csv",
                            "position": (
                                chunk.meta.doc_items[0].prov[0].charspan.start
                                if chunk.meta.doc_items and chunk.meta.doc_items[0].prov
                                else 0
                            ),
                            "total_chunks": len(chunks),
                        },
                    )
                )

            return chunk_responses

        except Exception as e:
            logger.error(f"Error processing CSV content: {e}")
            raise

    async def process_yaml_json(self, content: str, file_type: str) -> List[ChunkProcessed]:
        """Process YAML or JSON content into chunks.

        Parses structured data with Docling and chunks by structural elements
        (objects, arrays) while preserving hierarchy information.

        Args:
            content: Raw YAML or JSON content as string
            file_type: File extension ('yaml', 'yml', or 'json')

        Returns:
            List of ChunkProcessed objects with text, index, and metadata

        Raises:
            ValueError: If content is empty, file_type unsupported, or invalid format
        """
        if not content or not content.strip():
            raise ValueError(f"{file_type.upper()} content cannot be empty")

        if file_type not in ["yaml", "yml", "json"]:
            raise ValueError(f"Unsupported file type: {file_type}. Must be yaml, yml, or json")

        try:
            from docling.datamodel.base_models import InputFormat
            from docling.document_converter import DocumentConverter

            # Docling doesn't have separate YAML/JSON formats - handle as text
            # We'll process as MD format which handles text content
            converter = DocumentConverter()
            result = converter.convert_string(
                content, format=InputFormat.MD, name=f"{file_type}_content"
            )
            doc = result.document

            # Chunk the document
            chunks = list(self.chunker.chunk(dl_doc=doc))

            logger.info(f"Generated {len(chunks)} chunks from {file_type.upper()} content")

            # Convert to ChunkResponse objects
            chunk_responses = []
            for idx, chunk in enumerate(chunks):
                chunk_responses.append(
                    ChunkProcessed(
                        text=chunk.text,
                        index=idx,
                        header_anchor=None,  # YAML/JSON files don't have markdown headers
                        metadata={
                            "file_type": file_type,
                            "position": (
                                chunk.meta.doc_items[0].prov[0].charspan.start
                                if chunk.meta.doc_items and chunk.meta.doc_items[0].prov
                                else 0
                            ),
                            "total_chunks": len(chunks),
                        },
                    )
                )

            return chunk_responses

        except Exception as e:
            logger.error(f"Error processing {file_type.upper()} content: {e}")
            raise
