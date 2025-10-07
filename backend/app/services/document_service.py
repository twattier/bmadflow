"""Document storage service."""

import logging
from typing import Any, Dict, List, Tuple
from uuid import UUID

from app.models.document import Document
from app.repositories.document_repository import DocumentRepository
from app.schemas.document import FileTreeNode, FileTreeResponse
from app.schemas.github import FileInfo

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for document storage operations."""

    def __init__(self, document_repo: DocumentRepository):
        """Initialize document service with repository."""
        self.document_repo = document_repo

    async def store_document(
        self, project_doc_id: UUID, file_info: FileInfo, content: str, commit_sha: str
    ) -> Document:
        """Store document in database.

        Args:
            project_doc_id: ProjectDoc UUID
            file_info: FileInfo object with file metadata
            content: File content as string
            commit_sha: GitHub commit SHA

        Returns:
            Created/updated Document instance
        """
        # Extract file metadata
        file_name = file_info.path.split("/")[-1]
        file_type = file_name.split(".")[-1] if "." in file_name else "txt"
        file_size = len(content)

        # Store document using upsert
        doc = await self.document_repo.upsert(
            project_doc_id=project_doc_id,
            file_path=file_info.path,
            content=content,
            file_type=file_type,
            file_size=file_size,
            commit_sha=commit_sha,
        )

        logger.info(f"Stored document: {file_info.path} ({file_size} bytes)")

        return doc

    async def store_documents_batch(
        self, project_doc_id: UUID, files: List[Tuple[FileInfo, str, str]]
    ) -> List[Document]:
        """Store multiple documents, continue on individual failures.

        Args:
            project_doc_id: ProjectDoc UUID
            files: List of tuples (FileInfo, content, commit_sha)

        Returns:
            List of successfully stored documents
        """
        stored_docs = []

        for file_info, content, commit_sha in files:
            try:
                doc = await self.store_document(project_doc_id, file_info, content, commit_sha)
                stored_docs.append(doc)
                logger.info(f"✓ Stored: {file_info.path} ({len(content)} bytes)")
            except Exception as e:
                logger.error(f"✗ Failed to store {file_info.path}: {e}", exc_info=True)
                # Continue processing remaining files

        logger.info(
            f"Batch storage complete: {len(stored_docs)}/{len(files)} files stored successfully"
        )

        return stored_docs

    async def build_file_tree(self, project_id: UUID) -> FileTreeResponse:
        """Build hierarchical file tree from documents.

        Args:
            project_id: Project UUID

        Returns:
            FileTreeResponse with hierarchical tree structure
        """
        # Fetch all documents for project
        documents = await self.document_repo.list_by_project_id(project_id)

        # Build tree structure
        tree_nodes = self._parse_documents_to_tree(documents)

        return FileTreeResponse(project_id=project_id, tree=tree_nodes)

    def _parse_documents_to_tree(self, documents: List[Document]) -> List[FileTreeNode]:
        """Parse flat document list into hierarchical tree structure.

        Args:
            documents: List of Document objects

        Returns:
            List of FileTreeNode objects representing root level
        """
        if not documents:
            return []

        # Build tree structure using nested dictionaries
        tree_dict: Dict[str, Any] = {}

        for doc in documents:
            parts = doc.file_path.split("/")
            current = tree_dict

            # Navigate/create folder structure
            for i, part in enumerate(parts[:-1]):
                if part not in current:
                    current[part] = {"__folders__": {}, "__files__": []}
                current = current[part]["__folders__"]

            # Add file to final folder
            file_name = parts[-1]
            parent = tree_dict
            for part in parts[:-1]:
                parent = parent[part]["__folders__"]

            parent.setdefault("__files__", []).append(
                {
                    "id": doc.id,
                    "name": file_name,
                    "path": doc.file_path,
                    "file_type": doc.file_type,
                    "size": doc.file_size,
                }
            )

        # Convert dictionary to FileTreeNode list
        return self._dict_to_tree_nodes(tree_dict, "")

    def _dict_to_tree_nodes(
        self, tree_dict: Dict[str, Any], parent_path: str
    ) -> List[FileTreeNode]:
        """Convert nested dictionary to FileTreeNode list.

        Args:
            tree_dict: Nested dictionary structure
            parent_path: Parent folder path

        Returns:
            List of FileTreeNode objects, sorted (folders first, then files, alphabetical)
        """
        nodes = []

        # Process folders
        folder_names = [k for k in tree_dict.keys() if k not in ("__folders__", "__files__")]
        for folder_name in sorted(folder_names):
            folder_path = f"{parent_path}/{folder_name}" if parent_path else folder_name
            folder_data = tree_dict[folder_name]

            # Recursively build children
            children = self._dict_to_tree_nodes(folder_data["__folders__"], folder_path)

            # Add files from this folder
            files = folder_data.get("__files__", [])
            for file_data in sorted(files, key=lambda f: f["name"]):
                children.append(
                    FileTreeNode(
                        type="file",
                        name=file_data["name"],
                        path=file_data["path"],
                        id=file_data["id"],
                        file_type=file_data["file_type"],
                        size=file_data["size"],
                    )
                )

            nodes.append(
                FileTreeNode(
                    type="folder",
                    name=folder_name,
                    path=folder_path,
                    children=children if children else None,
                )
            )

        # Add root-level files (files with no folders in path)
        root_files = tree_dict.get("__files__", [])
        for file_data in sorted(root_files, key=lambda f: f["name"]):
            nodes.append(
                FileTreeNode(
                    type="file",
                    name=file_data["name"],
                    path=file_data["path"],
                    id=file_data["id"],
                    file_type=file_data["file_type"],
                    size=file_data["size"],
                )
            )

        return nodes
