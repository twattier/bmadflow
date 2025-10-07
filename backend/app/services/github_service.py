"""GitHub API integration service."""

import asyncio
import logging
import os
import time
from typing import List, Optional, Tuple
from urllib.parse import urlparse

import httpx

from app.exceptions import GitHubAPIError, RateLimitExceededError
from app.schemas.github import FileInfo

logger = logging.getLogger(__name__)

# Supported file extensions for documentation
SUPPORTED_EXTENSIONS = {".md", ".csv", ".yaml", ".yml", ".json", ".txt"}


class GitHubService:
    """Service for GitHub API interactions."""

    def __init__(self):
        """Initialize GitHub service with optional authentication."""
        self.token = os.getenv("GITHUB_TOKEN")
        self.base_url = "https://api.github.com"
        self.headers = {}
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"
            logger.info("GitHub API: Authenticated mode (5000 requests/hour)")
        else:
            logger.warning(
                "GitHub API: Unauthenticated mode (60 requests/hour). "
                "Set GITHUB_TOKEN for higher rate limits."
            )

    async def fetch_repository_tree(
        self, github_url: str, folder_path: Optional[str] = None
    ) -> List[FileInfo]:
        """
        Fetch repository file tree from GitHub.

        Args:
            github_url: GitHub repository URL (e.g., https://github.com/owner/repo)
            folder_path: Optional folder path to filter files (e.g., "docs")

        Returns:
            List of FileInfo objects for supported file types

        Raises:
            GitHubAPIError: If GitHub API request fails
            RateLimitExceededError: If rate limit exceeded
        """
        owner, repo = self._parse_github_url(github_url)

        # Fetch repository tree recursively
        tree_url = f"{self.base_url}/repos/{owner}/{repo}/git/trees/main?recursive=1"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(tree_url, headers=self.headers, timeout=30.0)

                #  Raise HTTP errors first (403, 404, etc.)
                response.raise_for_status()

                # Check rate limits after confirming success
                await self._check_rate_limit(response)

                data = response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                # Rate limit exceeded
                reset_time = int(e.response.headers.get("X-RateLimit-Reset", 0))
                raise RateLimitExceededError(reset_time)
            elif e.response.status_code == 404:
                raise GitHubAPIError(
                    f"Repository not found: {owner}/{repo}", e.response.status_code
                )
            else:
                raise GitHubAPIError(str(e), e.response.status_code)
        except httpx.RequestError as e:
            logger.error(f"GitHub API request failed: {e}")
            raise GitHubAPIError(f"Network error: {e}", 500)

        # Filter files
        files = []
        tree = data.get("tree", [])

        for item in tree:
            if item["type"] != "blob":
                continue

            file_path = item["path"]

            # Filter by folder path if specified
            if folder_path:
                normalized_folder = folder_path.strip("/")
                if not file_path.startswith(normalized_folder + "/"):
                    continue

            # Filter by supported extensions
            if not any(file_path.endswith(ext) for ext in SUPPORTED_EXTENSIONS):
                continue

            files.append(
                FileInfo(
                    path=file_path,
                    sha=item["sha"],
                    type=item["type"],
                    size=item.get("size"),
                )
            )

        logger.info(
            f"Fetched {len(files)} files from {owner}/{repo}"
            + (f" (folder: {folder_path})" if folder_path else "")
        )

        return files

    async def download_file_content(self, github_url: str, file_path: str) -> Tuple[str, str]:
        """
        Download file content from GitHub.

        Args:
            github_url: GitHub repository URL
            file_path: Relative file path within repository

        Returns:
            Tuple of (file_content, commit_sha)

        Raises:
            GitHubAPIError: If download fails
            RateLimitExceededError: If rate limit exceeded
        """
        owner, repo = self._parse_github_url(github_url)

        # Construct raw content URL
        raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/{file_path}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(raw_url, headers=self.headers, timeout=30.0)

                # Handle 404 errors gracefully
                if response.status_code == 404:
                    raise GitHubAPIError(f"File not found: {file_path} in {owner}/{repo}", 404)

                # Raise HTTP errors for other issues
                response.raise_for_status()

                # Check rate limits after confirming success
                await self._check_rate_limit(response)

                # Get commit SHA from GitHub API (using file info endpoint)
                file_url = f"{self.base_url}/repos/{owner}/{repo}/contents/{file_path}"
                file_response = await client.get(file_url, headers=self.headers, timeout=30.0)
                file_response.raise_for_status()
                file_data = file_response.json()
                commit_sha = file_data.get("sha", "")

                content = response.text
                logger.debug(f"Downloaded {file_path} from {owner}/{repo} ({len(content)} bytes)")

                return content, commit_sha

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                # Rate limit exceeded
                reset_time = int(e.response.headers.get("X-RateLimit-Reset", 0))
                raise RateLimitExceededError(reset_time)
            elif e.response.status_code == 404:
                raise GitHubAPIError(f"File not found: {file_path} in {owner}/{repo}", 404)
            else:
                raise GitHubAPIError(str(e), e.response.status_code)
        except httpx.RequestError as e:
            logger.error(f"GitHub download request failed: {e}")
            raise GitHubAPIError(f"Network error: {e}", 500)

    async def _check_rate_limit(self, response: httpx.Response) -> None:
        """
        Check GitHub API rate limits and handle accordingly.

        Args:
            response: HTTP response from GitHub API

        Raises:
            RateLimitExceededError: If rate limit is exceeded
        """
        remaining = int(response.headers.get("X-RateLimit-Remaining", 999))
        limit = int(response.headers.get("X-RateLimit-Limit", 60))
        reset_time = int(response.headers.get("X-RateLimit-Reset", 0))

        logger.debug(f"GitHub API rate limit: {remaining}/{limit} remaining")

        # Exponential backoff when approaching rate limit
        if remaining < 5:
            wait_seconds = reset_time - time.time()
            if wait_seconds > 0:
                logger.warning(
                    f"GitHub rate limit approaching ({remaining} remaining). "
                    f"Waiting {wait_seconds:.0f}s until reset."
                )
                await asyncio.sleep(wait_seconds)

    def _parse_github_url(self, github_url: str) -> tuple[str, str]:
        """
        Parse GitHub URL to extract owner and repo name.

        Args:
            github_url: GitHub repository URL

        Returns:
            Tuple of (owner, repo)

        Raises:
            GitHubAPIError: If URL format is invalid
        """
        # Remove .git suffix if present
        url = github_url.rstrip("/")
        if url.endswith(".git"):
            url = url[:-4]

        # Parse URL
        parsed = urlparse(url)

        # Validate GitHub domain
        if parsed.netloc not in ["github.com", "www.github.com"]:
            raise GitHubAPIError(
                f"Invalid GitHub URL: {github_url}. Must be a github.com URL.", 400
            )

        # Extract owner/repo from path
        path_parts = parsed.path.strip("/").split("/")
        if len(path_parts) < 2:
            raise GitHubAPIError(
                f"Invalid GitHub URL format: {github_url}. "
                "Expected format: https://github.com/owner/repo",
                400,
            )

        owner = path_parts[0]
        repo = path_parts[1]

        return owner, repo
