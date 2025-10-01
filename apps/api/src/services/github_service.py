"""GitHub API service for fetching repository files."""

import logging
import re
from typing import List, Optional, Tuple

from github import Github, GithubException
import requests

logger = logging.getLogger(__name__)


class GitHubService:
    """Service for interacting with GitHub REST API to fetch markdown files."""

    def __init__(self, token: Optional[str] = None):
        """
        Initialize GitHub client with optional token.

        Args:
            token: GitHub Personal Access Token (optional but recommended for rate limits)
        """
        self.github = Github(token) if token else Github()
        logger.info(
            f"GitHubService initialized with {'authenticated' if token else 'unauthenticated'} client"
        )

    def validate_repo_url(self, url: str) -> Tuple[str, str]:
        """
        Parse and validate repository URL.

        Args:
            url: Repository URL in format 'github.com/org/repo' or 'https://github.com/org/repo'

        Returns:
            Tuple of (owner, repo) if valid

        Raises:
            ValueError: If URL format is invalid
        """
        # Remove protocol if present
        url = url.replace("https://", "").replace("http://", "")

        # Match github.com/owner/repo pattern
        pattern = r"^github\.com/([^/]+)/([^/]+)/?$"
        match = re.match(pattern, url)

        if not match:
            raise ValueError(
                f"Invalid repository URL format: {url}. Expected format: github.com/owner/repo"
            )

        owner, repo = match.groups()
        logger.debug(f"Validated repository URL: owner={owner}, repo={repo}")
        return owner, repo

    def fetch_repository_tree(self, owner: str, repo: str) -> List[str]:
        """
        Fetch all markdown files from /docs folder using GitHub REST API.

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            List of file paths for markdown files in /docs folder

        Raises:
            ValueError: If repository not found, rate limit exceeded, or network error
        """
        try:
            # Get repository
            repository = self.github.get_repo(f"{owner}/{repo}")
            logger.info(f"Fetching repository tree for {owner}/{repo}")

            # Get default branch
            default_branch = repository.default_branch

            # Get tree recursively
            tree = repository.get_git_tree(default_branch, recursive=True)

            # Filter for markdown files in /docs folder
            markdown_files = []
            for item in tree.tree:
                # Check if it's a blob (file) and in docs folder
                if item.type == "blob" and item.path.startswith("docs/"):
                    # Check if it has .md extension
                    if item.path.endswith(".md"):
                        markdown_files.append(item.path)

            logger.info(
                f"Found {len(markdown_files)} markdown files in /docs folder"
            )
            return markdown_files

        except GithubException as e:
            if e.status == 404:
                error_msg = f"Repository not found: {owner}/{repo}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            elif e.status == 403:
                error_msg = "GitHub API rate limit exceeded. Please provide a token."
                logger.error(error_msg)
                raise ValueError(error_msg)
            else:
                error_msg = f"GitHub API error: {e.data.get('message', str(e)) if hasattr(e, 'data') else str(e)}"
                logger.error(error_msg)
                raise ValueError(error_msg)
        except (requests.ConnectionError, requests.Timeout) as e:
            error_msg = f"Network error fetching repository: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error fetching repository tree: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    def fetch_markdown_content(
        self, owner: str, repo: str, file_path: str
    ) -> Tuple[str, str]:
        """
        Fetch content of a single markdown file.

        Args:
            owner: Repository owner
            repo: Repository name
            file_path: Path to file in repository

        Returns:
            Tuple of (file_path, content_text)

        Raises:
            ValueError: If file not found, rate limit exceeded, or network error
        """
        try:
            repository = self.github.get_repo(f"{owner}/{repo}")
            content_file = repository.get_contents(file_path)

            # Decode base64-encoded content
            content_text = content_file.decoded_content.decode("utf-8")

            logger.debug(f"Fetched content for {file_path} ({len(content_text)} chars)")
            return (file_path, content_text)

        except GithubException as e:
            if e.status == 404:
                error_msg = f"File not found: {file_path}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            elif e.status == 403:
                error_msg = "GitHub API rate limit exceeded. Please provide a token."
                logger.error(error_msg)
                raise ValueError(error_msg)
            else:
                error_msg = f"GitHub API error: {e.data.get('message', str(e)) if hasattr(e, 'data') else str(e)}"
                logger.error(error_msg)
                raise ValueError(error_msg)
        except (requests.ConnectionError, requests.Timeout) as e:
            error_msg = f"Network error fetching file content: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error fetching file content: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    def fetch_all_markdown_files(
        self, owner: str, repo: str
    ) -> List[Tuple[str, str]]:
        """
        Fetch all markdown files from /docs folder with their content.

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            List of tuples (file_path, content_text) for all markdown files

        Raises:
            ValueError: If repository errors occur
        """
        # Get list of markdown files
        file_paths = self.fetch_repository_tree(owner, repo)

        # Fetch content for each file
        results = []
        for file_path in file_paths:
            try:
                file_content = self.fetch_markdown_content(owner, repo, file_path)
                results.append(file_content)
            except ValueError as e:
                logger.warning(f"Skipping file {file_path}: {e}")
                continue

        logger.info(
            f"Successfully fetched {len(results)} of {len(file_paths)} markdown files"
        )
        return results
