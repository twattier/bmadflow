"""Integration tests for GitHub service with real API calls."""

import os

import pytest

from app.services.github_service import GitHubService


@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.getenv("GITHUB_INTEGRATION_TEST"),
    reason="Integration test disabled. Set GITHUB_INTEGRATION_TEST=1 to enable.",
)
async def test_fetch_bmadflow_docs_folder():
    """Test fetching docs folder from real BMADFlow repository."""
    service = GitHubService()

    # Act
    files = await service.fetch_repository_tree(
        github_url="https://github.com/twattier/bmadflow.git", folder_path="docs"
    )

    # Assert - Verify files returned
    assert len(files) > 0, "Should return files from docs folder"

    # Verify all files are from docs/ folder
    for file in files:
        assert file.path.startswith("docs/"), f"File {file.path} should be in docs/ folder"

    # Verify only supported extensions
    extensions = {f.path.split(".")[-1] for f in files if "." in f.path}
    supported = {"md", "yaml", "yml", "json", "txt", "csv"}
    assert extensions.issubset(supported), f"Found unsupported extensions: {extensions - supported}"

    # Verify no .py files included
    py_files = [f.path for f in files if f.path.endswith(".py")]
    assert not py_files, f"Python files should be excluded: {py_files}"

    # Verify FileInfo structure
    for file in files:
        assert file.path, "File should have path"
        assert file.sha, "File should have SHA"
        assert file.type == "blob", "All returned items should be blobs"


@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.getenv("GITHUB_INTEGRATION_TEST"),
    reason="Integration test disabled. Set GITHUB_INTEGRATION_TEST=1 to enable.",
)
async def test_fetch_bmadflow_full_repo():
    """Test fetching entire repository without folder filter."""
    service = GitHubService()

    # Act
    files = await service.fetch_repository_tree(
        github_url="https://github.com/twattier/bmadflow.git"
    )

    # Assert
    assert len(files) > 0, "Should return files from repository"

    # Should have files from various folders
    file_paths = [f.path for f in files]
    assert any("docs/" in path for path in file_paths), "Should include files from docs/"

    # Verify only supported extensions
    for file in files:
        ext = "." + file.path.split(".")[-1] if "." in file.path else ""
        assert ext in {
            ".md",
            ".csv",
            ".yaml",
            ".yml",
            ".json",
            ".txt",
        }, f"Unsupported extension: {ext} in {file.path}"
