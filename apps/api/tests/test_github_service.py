"""Unit tests for GitHub service."""

import pytest
from unittest.mock import Mock, patch
from github import GithubException
import requests

from src.services.github_service import GitHubService


class TestValidateRepoUrl:
    """Tests for validate_repo_url method."""

    def test_validate_repo_url_valid(self):
        """Test valid repository URL without protocol."""
        service = GitHubService()
        owner, repo = service.validate_repo_url("github.com/owner/repo")
        assert owner == "owner"
        assert repo == "repo"

    def test_validate_repo_url_valid_with_https(self):
        """Test valid repository URL with https protocol."""
        service = GitHubService()
        owner, repo = service.validate_repo_url("https://github.com/owner/repo")
        assert owner == "owner"
        assert repo == "repo"

    def test_validate_repo_url_valid_with_http(self):
        """Test valid repository URL with http protocol."""
        service = GitHubService()
        owner, repo = service.validate_repo_url("http://github.com/owner/repo")
        assert owner == "owner"
        assert repo == "repo"

    def test_validate_repo_url_valid_with_trailing_slash(self):
        """Test valid repository URL with trailing slash."""
        service = GitHubService()
        owner, repo = service.validate_repo_url("github.com/owner/repo/")
        assert owner == "owner"
        assert repo == "repo"

    def test_validate_repo_url_invalid_no_owner(self):
        """Test invalid URL without owner."""
        service = GitHubService()
        with pytest.raises(ValueError, match="Invalid repository URL format"):
            service.validate_repo_url("github.com/repo")

    def test_validate_repo_url_invalid_no_repo(self):
        """Test invalid URL without repo name."""
        service = GitHubService()
        with pytest.raises(ValueError, match="Invalid repository URL format"):
            service.validate_repo_url("github.com/owner")

    def test_validate_repo_url_invalid_extra_path(self):
        """Test invalid URL with extra path segments."""
        service = GitHubService()
        with pytest.raises(ValueError, match="Invalid repository URL format"):
            service.validate_repo_url("github.com/owner/repo/extra/path")

    def test_validate_repo_url_invalid_wrong_domain(self):
        """Test invalid URL with wrong domain."""
        service = GitHubService()
        with pytest.raises(ValueError, match="Invalid repository URL format"):
            service.validate_repo_url("gitlab.com/owner/repo")

    def test_validate_repo_url_invalid_completely_wrong(self):
        """Test completely invalid URL."""
        service = GitHubService()
        with pytest.raises(ValueError, match="Invalid repository URL format"):
            service.validate_repo_url("not-a-valid-url")


class TestFetchRepositoryTree:
    """Tests for fetch_repository_tree method."""

    @patch("src.services.github_service.Github")
    def test_fetch_repository_tree_success(self, mock_github_class):
        """Test successful repository tree fetch with filtering."""
        # Setup mocks
        mock_github = Mock()
        mock_github_class.return_value = mock_github

        mock_repo = Mock()
        mock_repo.default_branch = "main"

        mock_tree = Mock()
        mock_tree.tree = [
            Mock(path="docs/prd.md", type="blob"),
            Mock(path="docs/architecture.md", type="blob"),
            Mock(path="docs/epics/epic-1.md", type="blob"),
            Mock(path="README.md", type="blob"),  # Not in docs/
            Mock(path="src/main.py", type="blob"),  # Not in docs/
            Mock(path="docs/image.png", type="blob"),  # Not .md
            Mock(path="docs", type="tree"),  # Directory, not file
        ]

        mock_repo.get_git_tree.return_value = mock_tree
        mock_github.get_repo.return_value = mock_repo

        # Test
        service = GitHubService()
        files = service.fetch_repository_tree("owner", "repo")

        # Verify
        assert len(files) == 3
        assert "docs/prd.md" in files
        assert "docs/architecture.md" in files
        assert "docs/epics/epic-1.md" in files
        assert "README.md" not in files
        assert "src/main.py" not in files
        assert "docs/image.png" not in files

        mock_github.get_repo.assert_called_once_with("owner/repo")
        mock_repo.get_git_tree.assert_called_once_with("main", recursive=True)

    @patch("src.services.github_service.Github")
    def test_fetch_repository_tree_404_error(self, mock_github_class):
        """Test 404 error when repository not found."""
        mock_github = Mock()
        mock_github_class.return_value = mock_github

        error = GithubException(404, {"message": "Not Found"}, headers={})
        mock_github.get_repo.side_effect = error

        service = GitHubService()
        with pytest.raises(ValueError, match="Repository not found: owner/repo"):
            service.fetch_repository_tree("owner", "repo")

    @patch("src.services.github_service.Github")
    def test_fetch_repository_tree_403_rate_limit(self, mock_github_class):
        """Test 403 error for rate limit exceeded."""
        mock_github = Mock()
        mock_github_class.return_value = mock_github

        error = GithubException(403, {"message": "Rate limit exceeded"}, headers={})
        mock_github.get_repo.side_effect = error

        service = GitHubService()
        with pytest.raises(ValueError, match="GitHub API rate limit exceeded"):
            service.fetch_repository_tree("owner", "repo")

    @patch("src.services.github_service.Github")
    def test_fetch_repository_tree_other_github_error(self, mock_github_class):
        """Test other GitHub API errors."""
        mock_github = Mock()
        mock_github_class.return_value = mock_github

        error = GithubException(500, {"message": "Internal Server Error"}, headers={})
        mock_github.get_repo.side_effect = error

        service = GitHubService()
        with pytest.raises(ValueError, match="GitHub API error"):
            service.fetch_repository_tree("owner", "repo")

    @patch("src.services.github_service.Github")
    def test_fetch_repository_tree_network_error(self, mock_github_class):
        """Test network connection error."""
        mock_github = Mock()
        mock_github_class.return_value = mock_github

        mock_github.get_repo.side_effect = requests.ConnectionError("Connection failed")

        service = GitHubService()
        with pytest.raises(ValueError, match="Network error fetching repository"):
            service.fetch_repository_tree("owner", "repo")

    @patch("src.services.github_service.Github")
    def test_fetch_repository_tree_timeout_error(self, mock_github_class):
        """Test network timeout error."""
        mock_github = Mock()
        mock_github_class.return_value = mock_github

        mock_github.get_repo.side_effect = requests.Timeout("Request timed out")

        service = GitHubService()
        with pytest.raises(ValueError, match="Network error fetching repository"):
            service.fetch_repository_tree("owner", "repo")

    @patch("src.services.github_service.Github")
    def test_fetch_repository_tree_empty_docs(self, mock_github_class):
        """Test repository with no markdown files in docs folder."""
        mock_github = Mock()
        mock_github_class.return_value = mock_github

        mock_repo = Mock()
        mock_repo.default_branch = "main"

        mock_tree = Mock()
        mock_tree.tree = [
            Mock(path="README.md", type="blob"),
            Mock(path="src/main.py", type="blob"),
        ]

        mock_repo.get_git_tree.return_value = mock_tree
        mock_github.get_repo.return_value = mock_repo

        service = GitHubService()
        files = service.fetch_repository_tree("owner", "repo")

        assert len(files) == 0


class TestFetchMarkdownContent:
    """Tests for fetch_markdown_content method."""

    @patch("src.services.github_service.Github")
    def test_fetch_markdown_content_success(self, mock_github_class):
        """Test successful markdown content fetch."""
        mock_github = Mock()
        mock_github_class.return_value = mock_github

        mock_repo = Mock()
        mock_content = Mock()
        mock_content.decoded_content = b"# Test Markdown\n\nThis is test content."

        mock_repo.get_contents.return_value = mock_content
        mock_github.get_repo.return_value = mock_repo

        service = GitHubService()
        file_path, content = service.fetch_markdown_content(
            "owner", "repo", "docs/test.md"
        )

        assert file_path == "docs/test.md"
        assert content == "# Test Markdown\n\nThis is test content."
        mock_github.get_repo.assert_called_once_with("owner/repo")
        mock_repo.get_contents.assert_called_once_with("docs/test.md")

    @patch("src.services.github_service.Github")
    def test_fetch_markdown_content_404_error(self, mock_github_class):
        """Test 404 error when file not found."""
        mock_github = Mock()
        mock_github_class.return_value = mock_github

        mock_repo = Mock()
        error = GithubException(404, {"message": "Not Found"}, headers={})
        mock_repo.get_contents.side_effect = error
        mock_github.get_repo.return_value = mock_repo

        service = GitHubService()
        with pytest.raises(ValueError, match="File not found: docs/test.md"):
            service.fetch_markdown_content("owner", "repo", "docs/test.md")

    @patch("src.services.github_service.Github")
    def test_fetch_markdown_content_403_rate_limit(self, mock_github_class):
        """Test 403 error for rate limit exceeded."""
        mock_github = Mock()
        mock_github_class.return_value = mock_github

        mock_repo = Mock()
        error = GithubException(403, {"message": "Rate limit exceeded"}, headers={})
        mock_repo.get_contents.side_effect = error
        mock_github.get_repo.return_value = mock_repo

        service = GitHubService()
        with pytest.raises(ValueError, match="GitHub API rate limit exceeded"):
            service.fetch_markdown_content("owner", "repo", "docs/test.md")


class TestFetchAllMarkdownFiles:
    """Tests for fetch_all_markdown_files method."""

    @patch("src.services.github_service.Github")
    def test_fetch_all_markdown_files_success(self, mock_github_class):
        """Test successful fetch of all markdown files."""
        mock_github = Mock()
        mock_github_class.return_value = mock_github

        mock_repo = Mock()
        mock_repo.default_branch = "main"

        # Setup tree
        mock_tree = Mock()
        mock_tree.tree = [
            Mock(path="docs/file1.md", type="blob"),
            Mock(path="docs/file2.md", type="blob"),
        ]
        mock_repo.get_git_tree.return_value = mock_tree

        # Setup content
        mock_content1 = Mock()
        mock_content1.decoded_content = b"Content 1"
        mock_content2 = Mock()
        mock_content2.decoded_content = b"Content 2"

        mock_repo.get_contents.side_effect = [mock_content1, mock_content2]
        mock_github.get_repo.return_value = mock_repo

        service = GitHubService()
        results = service.fetch_all_markdown_files("owner", "repo")

        assert len(results) == 2
        assert results[0] == ("docs/file1.md", "Content 1")
        assert results[1] == ("docs/file2.md", "Content 2")

    @patch("src.services.github_service.Github")
    def test_fetch_all_markdown_files_partial_failure(self, mock_github_class):
        """Test fetch continues when individual files fail."""
        mock_github = Mock()
        mock_github_class.return_value = mock_github

        mock_repo = Mock()
        mock_repo.default_branch = "main"

        # Setup tree
        mock_tree = Mock()
        mock_tree.tree = [
            Mock(path="docs/file1.md", type="blob"),
            Mock(path="docs/file2.md", type="blob"),
            Mock(path="docs/file3.md", type="blob"),
        ]
        mock_repo.get_git_tree.return_value = mock_tree

        # Setup content - file2 fails
        mock_content1 = Mock()
        mock_content1.decoded_content = b"Content 1"
        mock_content3 = Mock()
        mock_content3.decoded_content = b"Content 3"

        error = GithubException(404, {"message": "Not Found"}, headers={})
        mock_repo.get_contents.side_effect = [mock_content1, error, mock_content3]
        mock_github.get_repo.return_value = mock_repo

        service = GitHubService()
        results = service.fetch_all_markdown_files("owner", "repo")

        # Should get 2 files (file1 and file3), skip file2
        assert len(results) == 2
        assert results[0] == ("docs/file1.md", "Content 1")
        assert results[1] == ("docs/file3.md", "Content 3")


class TestGitHubServiceInit:
    """Tests for GitHubService initialization."""

    @patch("src.services.github_service.Github")
    def test_init_with_token(self, mock_github_class):
        """Test initialization with token."""
        GitHubService(token="test_token")
        mock_github_class.assert_called_once_with("test_token")

    @patch("src.services.github_service.Github")
    def test_init_without_token(self, mock_github_class):
        """Test initialization without token."""
        GitHubService()
        mock_github_class.assert_called_once_with()
