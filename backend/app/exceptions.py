"""Custom exceptions for BMADFlow."""

from datetime import datetime


class BMADFlowError(Exception):
    """Base exception for BMADFlow."""

    pass


class GitHubAPIError(BMADFlowError):
    """GitHub API error."""

    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class RateLimitExceededError(GitHubAPIError):
    """GitHub rate limit exceeded."""

    def __init__(self, reset_time: int):
        self.reset_time = reset_time
        super().__init__(
            f"Rate limit exceeded. Resets at {datetime.fromtimestamp(reset_time)}",
            429,
        )
