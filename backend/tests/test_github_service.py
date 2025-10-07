"""Unit tests for GitHub service."""

import os
from datetime import datetime
from unittest.mock import AsyncMock, patch

import httpx
import pytest
import respx

from app.exceptions import GitHubAPIError, RateLimitExceededError
from app.services.github_service import GitHubService


@pytest.mark.asyncio
@respx.mock
async def test_fetch_repository_tree_success():
    """Test successful repository tree fetch."""
    # Arrange
    respx.get("https://api.github.com/repos/user/repo/git/trees/main?recursive=1").mock(
        return_value=httpx.Response(
            200,
            json={
                "tree": [
                    {"path": "README.md", "type": "blob", "sha": "abc123", "size": 1024},
                    {"path": "docs/prd.md", "type": "blob", "sha": "def456", "size": 2048},
                    {"path": "src/main.py", "type": "blob", "sha": "ghi789", "size": 512},
                    {"path": "docs", "type": "tree", "sha": "tree123"},
                ]
            },
            headers={
                "X-RateLimit-Remaining": "4999",
                "X-RateLimit-Limit": "5000",
                "X-RateLimit-Reset": str(int(datetime.now().timestamp()) + 3600),
            },
        )
    )

    service = GitHubService()

    # Act
    files = await service.fetch_repository_tree("https://github.com/user/repo")

    # Assert
    assert len(files) == 2  # Only .md files (not .py, not tree)
    assert files[0].path == "README.md"
    assert files[0].sha == "abc123"
    assert files[1].path == "docs/prd.md"


@pytest.mark.asyncio
@respx.mock
async def test_fetch_repository_tree_authenticated_mode():
    """Test authenticated mode with token."""
    # Arrange
    route = respx.get("https://api.github.com/repos/user/repo/git/trees/main?recursive=1").mock(
        return_value=httpx.Response(
            200,
            json={"tree": []},
            headers={
                "X-RateLimit-Remaining": "4999",
                "X-RateLimit-Limit": "5000",
                "X-RateLimit-Reset": str(int(datetime.now().timestamp()) + 3600),
            },
        )
    )

    # Set token
    with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}):
        service = GitHubService()

        # Act
        await service.fetch_repository_tree("https://github.com/user/repo")

        # Assert
        assert route.called
        assert "Authorization" in route.calls.last.request.headers
        assert route.calls.last.request.headers["Authorization"] == "Bearer test_token"


@pytest.mark.asyncio
@respx.mock
async def test_fetch_repository_tree_unauthenticated_mode():
    """Test unauthenticated mode without token."""
    # Arrange
    route = respx.get("https://api.github.com/repos/user/repo/git/trees/main?recursive=1").mock(
        return_value=httpx.Response(
            200,
            json={"tree": []},
            headers={
                "X-RateLimit-Remaining": "59",
                "X-RateLimit-Limit": "60",
                "X-RateLimit-Reset": str(int(datetime.now().timestamp()) + 3600),
            },
        )
    )

    # Ensure no token
    with patch.dict(os.environ, {}, clear=True):
        service = GitHubService()

        # Act
        await service.fetch_repository_tree("https://github.com/user/repo")

        # Assert
        assert route.called
        assert "Authorization" not in route.calls.last.request.headers


@pytest.mark.asyncio
@respx.mock
async def test_file_filtering_by_extension():
    """Test file filtering by supported extensions."""
    # Arrange
    respx.get("https://api.github.com/repos/user/repo/git/trees/main?recursive=1").mock(
        return_value=httpx.Response(
            200,
            json={
                "tree": [
                    {"path": "README.md", "type": "blob", "sha": "a1"},
                    {"path": "data.csv", "type": "blob", "sha": "a2"},
                    {"path": "config.yaml", "type": "blob", "sha": "a3"},
                    {"path": "config2.yml", "type": "blob", "sha": "a4"},
                    {"path": "data.json", "type": "blob", "sha": "a5"},
                    {"path": "notes.txt", "type": "blob", "sha": "a6"},
                    {"path": "program.exe", "type": "blob", "sha": "bad"},  # Excluded
                    {"path": "script.py", "type": "blob", "sha": "bad2"},  # Excluded
                ]
            },
            headers={
                "X-RateLimit-Remaining": "4999",
                "X-RateLimit-Limit": "5000",
                "X-RateLimit-Reset": str(int(datetime.now().timestamp()) + 3600),
            },
        )
    )

    service = GitHubService()

    # Act
    files = await service.fetch_repository_tree("https://github.com/user/repo")

    # Assert
    assert len(files) == 6
    extensions = {f.path.split(".")[-1] for f in files}
    assert extensions == {"md", "csv", "yaml", "yml", "json", "txt"}


@pytest.mark.asyncio
@respx.mock
async def test_folder_path_filtering():
    """Test filtering files by folder path."""
    # Arrange
    respx.get("https://api.github.com/repos/user/repo/git/trees/main?recursive=1").mock(
        return_value=httpx.Response(
            200,
            json={
                "tree": [
                    {"path": "README.md", "type": "blob", "sha": "a1"},
                    {"path": "docs/prd.md", "type": "blob", "sha": "a2"},
                    {"path": "docs/architecture.md", "type": "blob", "sha": "a3"},
                    {"path": "src/main.py", "type": "blob", "sha": "bad"},
                ]
            },
            headers={
                "X-RateLimit-Remaining": "4999",
                "X-RateLimit-Limit": "5000",
                "X-RateLimit-Reset": str(int(datetime.now().timestamp()) + 3600),
            },
        )
    )

    service = GitHubService()

    # Act
    files = await service.fetch_repository_tree("https://github.com/user/repo", folder_path="docs")

    # Assert
    assert len(files) == 2
    assert all(f.path.startswith("docs/") for f in files)
    assert files[0].path == "docs/prd.md"
    assert files[1].path == "docs/architecture.md"


@pytest.mark.asyncio
@respx.mock
@patch("app.services.github_service.asyncio.sleep", new_callable=AsyncMock)
async def test_rate_limit_approaching_triggers_backoff(mock_sleep):
    """Test exponential backoff when rate limit approaching."""
    # Arrange
    reset_time = int(datetime.now().timestamp()) + 10
    respx.get("https://api.github.com/repos/user/repo/git/trees/main?recursive=1").mock(
        return_value=httpx.Response(
            200,
            json={"tree": []},
            headers={
                "X-RateLimit-Remaining": "4",  # Less than 5
                "X-RateLimit-Limit": "5000",
                "X-RateLimit-Reset": str(reset_time),
            },
        )
    )

    service = GitHubService()

    # Act
    await service.fetch_repository_tree("https://github.com/user/repo")

    # Assert
    mock_sleep.assert_called_once()
    # Should sleep for approximately 10 seconds (reset_time - now)
    sleep_duration = mock_sleep.call_args[0][0]
    assert 9 <= sleep_duration <= 11  # Allow small timing variance


@pytest.mark.asyncio
@respx.mock
async def test_rate_limit_exceeded_raises_error():
    """Test rate limit exceeded raises RateLimitExceededError."""
    # Arrange
    reset_time = int(datetime.now().timestamp()) + 3600
    respx.get("https://api.github.com/repos/user/repo/git/trees/main?recursive=1").mock(
        return_value=httpx.Response(
            403,
            json={"message": "API rate limit exceeded"},
            headers={
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Limit": "60",
                "X-RateLimit-Reset": str(reset_time),
            },
        )
    )

    service = GitHubService()

    # Act & Assert
    with pytest.raises(RateLimitExceededError) as exc_info:
        await service.fetch_repository_tree("https://github.com/user/repo")

    assert exc_info.value.reset_time == reset_time
    assert exc_info.value.status_code == 429


@pytest.mark.asyncio
async def test_invalid_github_url_raises_error():
    """Test invalid GitHub URL raises GitHubAPIError."""
    service = GitHubService()

    # Act & Assert - not github.com
    with pytest.raises(GitHubAPIError) as exc_info:
        await service.fetch_repository_tree("https://gitlab.com/user/repo")
    assert exc_info.value.status_code == 400
    assert "Invalid GitHub URL" in exc_info.value.message

    # Act & Assert - invalid format
    with pytest.raises(GitHubAPIError) as exc_info:
        await service.fetch_repository_tree("https://github.com/user")
    assert exc_info.value.status_code == 400
    assert "Invalid GitHub URL format" in exc_info.value.message


@pytest.mark.asyncio
async def test_parse_github_url_with_git_suffix():
    """Test parsing GitHub URL with .git suffix."""
    service = GitHubService()

    # Act
    owner, repo = service._parse_github_url("https://github.com/user/repo.git")

    # Assert
    assert owner == "user"
    assert repo == "repo"


@pytest.mark.asyncio
@respx.mock
async def test_network_error_raises_github_api_error():
    """Test network errors raise GitHubAPIError."""
    # Arrange
    respx.get("https://api.github.com/repos/user/repo/git/trees/main?recursive=1").mock(
        side_effect=httpx.RequestError("Connection failed")
    )

    service = GitHubService()

    # Act & Assert
    with pytest.raises(GitHubAPIError) as exc_info:
        await service.fetch_repository_tree("https://github.com/user/repo")

    assert exc_info.value.status_code == 500
    assert "Network error" in exc_info.value.message


# Tests for download_file_content (Story 2.4)


@pytest.mark.asyncio
@respx.mock
async def test_download_file_content_success():
    """Test successful file content download."""
    # Arrange
    raw_route = respx.get("https://raw.githubusercontent.com/user/repo/main/docs/prd.md").mock(
        return_value=httpx.Response(
            200,
            text="# Product Requirements Document\n\nThis is the PRD content.",
            headers={
                "X-RateLimit-Remaining": "4999",
                "X-RateLimit-Limit": "5000",
                "X-RateLimit-Reset": str(int(datetime.now().timestamp()) + 3600),
            },
        )
    )

    api_route = respx.get("https://api.github.com/repos/user/repo/contents/docs/prd.md").mock(
        return_value=httpx.Response(
            200,
            json={
                "name": "prd.md",
                "path": "docs/prd.md",
                "sha": "abc123def456",
                "size": 1024,
                "type": "file",
            },
            headers={
                "X-RateLimit-Remaining": "4998",
                "X-RateLimit-Limit": "5000",
                "X-RateLimit-Reset": str(int(datetime.now().timestamp()) + 3600),
            },
        )
    )

    service = GitHubService()

    # Act
    content, commit_sha = await service.download_file_content(
        "https://github.com/user/repo", "docs/prd.md"
    )

    # Assert
    assert raw_route.called
    assert api_route.called
    assert content == "# Product Requirements Document\n\nThis is the PRD content."
    assert commit_sha == "abc123def456"


@pytest.mark.asyncio
@respx.mock
async def test_download_file_content_404():
    """Test 404 error when file not found."""
    # Arrange
    respx.get("https://raw.githubusercontent.com/user/repo/main/missing.md").mock(
        return_value=httpx.Response(404, text="404: Not Found")
    )

    service = GitHubService()

    # Act & Assert
    with pytest.raises(GitHubAPIError) as exc_info:
        await service.download_file_content("https://github.com/user/repo", "missing.md")

    assert exc_info.value.status_code == 404
    assert "File not found" in exc_info.value.message
    assert "missing.md" in exc_info.value.message


@pytest.mark.asyncio
@respx.mock
async def test_download_file_content_rate_limit():
    """Test rate limit exceeded during download."""
    # Arrange
    reset_time = int(datetime.now().timestamp()) + 3600
    respx.get("https://raw.githubusercontent.com/user/repo/main/docs/prd.md").mock(
        return_value=httpx.Response(
            403,
            json={"message": "API rate limit exceeded"},
            headers={
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Limit": "60",
                "X-RateLimit-Reset": str(reset_time),
            },
        )
    )

    service = GitHubService()

    # Act & Assert
    with pytest.raises(RateLimitExceededError) as exc_info:
        await service.download_file_content("https://github.com/user/repo", "docs/prd.md")

    assert exc_info.value.reset_time == reset_time


@pytest.mark.asyncio
@respx.mock
async def test_download_file_content_network_error():
    """Test network error during download."""
    # Arrange
    respx.get("https://raw.githubusercontent.com/user/repo/main/docs/prd.md").mock(
        side_effect=httpx.RequestError("Connection timeout")
    )

    service = GitHubService()

    # Act & Assert
    with pytest.raises(GitHubAPIError) as exc_info:
        await service.download_file_content("https://github.com/user/repo", "docs/prd.md")

    assert exc_info.value.status_code == 500
    assert "Network error" in exc_info.value.message
