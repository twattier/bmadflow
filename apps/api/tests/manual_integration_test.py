"""Manual integration test for GitHub service.

This script tests fetching markdown files from the bmad-code-org/BMAD-METHOD repository.
Run with: python3 -m apps.api.tests.manual_integration_test
"""

import sys
import time
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.github_service import GitHubService


def main():
    """Run manual integration test."""
    print("=" * 60)
    print("GitHub Service Manual Integration Test")
    print("=" * 60)
    print()

    # Initialize service
    token = os.getenv("GITHUB_TOKEN")
    if token:
        print("✓ Using GitHub token from environment")
    else:
        print("⚠ No GitHub token found - using unauthenticated mode")
        print("  (Rate limit: 60 requests/hour)")
    print()

    service = GitHubService(token=token)

    # Test repository
    repo_url = "github.com/bmad-code-org/BMAD-METHOD"
    print(f"Testing repository: {repo_url}")
    print()

    # Validate URL
    print("1. Validating repository URL...")
    try:
        owner, repo = service.validate_repo_url(repo_url)
        print(f"   ✓ Owner: {owner}")
        print(f"   ✓ Repo: {repo}")
    except ValueError as e:
        print(f"   ✗ Error: {e}")
        return 1
    print()

    # Fetch repository tree
    print("2. Fetching repository tree...")
    start_time = time.time()
    try:
        files = service.fetch_repository_tree(owner, repo)
        tree_time = time.time() - start_time
        print(f"   ✓ Found {len(files)} markdown files in /docs folder")
        print(f"   ✓ Time: {tree_time:.2f} seconds")
        print()
        print("   Files found:")
        for file_path in sorted(files):
            print(f"     - {file_path}")
    except ValueError as e:
        print(f"   ✗ Error: {e}")
        return 1
    print()

    # Fetch all markdown content
    print("3. Fetching all markdown file content...")
    start_time = time.time()
    try:
        results = service.fetch_all_markdown_files(owner, repo)
        fetch_time = time.time() - start_time
        print(f"   ✓ Successfully fetched {len(results)} files")
        print(f"   ✓ Time: {fetch_time:.2f} seconds")
        print()

        # Show sample content
        if results:
            file_path, content = results[0]
            print(f"   Sample content from {file_path}:")
            print(f"   {'=' * 56}")
            preview = content[:200] if len(content) > 200 else content
            print(f"   {preview}...")
            print(f"   {'=' * 56}")
            print(f"   Content length: {len(content)} characters")
    except ValueError as e:
        print(f"   ✗ Error: {e}")
        return 1
    print()

    # Summary
    total_time = tree_time + fetch_time
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total files found: {len(files)}")
    print(f"Total files fetched: {len(results)}")
    print(f"Total time: {total_time:.2f} seconds")
    print()

    # Check AC #6 requirement (<2 minutes)
    if total_time < 120:
        print(f"✓ PASS: Completed in {total_time:.2f}s (requirement: <120s)")
    else:
        print(f"✗ FAIL: Took {total_time:.2f}s (requirement: <120s)")
        return 1

    print()
    print("✓ All acceptance criteria verified!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
