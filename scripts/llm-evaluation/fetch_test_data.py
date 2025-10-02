#!/usr/bin/env python3
"""Fetch test documents from BMAD-METHOD repository."""

import json
import os
from pathlib import Path
import urllib.request
import urllib.error

REPO_URL = "https://raw.githubusercontent.com/twattier/bmadflow/main/docs"

# Document selections for diverse test set
EPIC_FILES = [
    "epics/epic-1-foundation-github-dashboard.md",
    "epics/epic-2-llm-content-extraction.md",
    "epics/epic-3-multi-view-dashboard.md",
    "epics/epic-4-epic-story-visualization.md",
]

STORY_FILES = [
    "stories/story-1-1-project-infrastructure-setup.md",
    "stories/story-1-2-database-schema-for-documents.md",
    "stories/story-1-3-github-api-integration-fetch-repository-files.md",
    "stories/story-1-4-manual-sync-api-endpoint.md",
    "stories/story-1-5-dashboard-shell-with-4-view-navigation.md",
    "stories/story-1-6-project-setup-and-sync-ui.md",
]


def fetch_document(file_path: str, output_dir: Path) -> bool:
    """Fetch a document from GitHub."""
    url = f"{REPO_URL}/{file_path}"
    output_path = output_dir / Path(file_path).name

    try:
        print(f"Fetching {file_path}...", end=" ")
        with urllib.request.urlopen(url) as response:
            content = response.read().decode('utf-8')
            output_path.write_text(content)
            print(f"✅ ({len(content)} bytes)")
            return True
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP {e.code}")
        return False
    except Exception as e:
        print(f"❌ {e}")
        return False


def main():
    """Main entry point."""
    test_data_dir = Path("test_data")
    test_data_dir.mkdir(exist_ok=True)

    manifest = []

    print("Fetching epic documents...")
    for epic_file in EPIC_FILES:
        if fetch_document(epic_file, test_data_dir):
            manifest.append({
                "file": Path(epic_file).name,
                "type": "epic",
                "source": epic_file,
                "complexity": "medium"
            })

    print("\nFetching story documents...")
    for story_file in STORY_FILES:
        if fetch_document(story_file, test_data_dir):
            manifest.append({
                "file": Path(story_file).name,
                "type": "story",
                "source": story_file,
                "complexity": "medium"
            })

    # Save manifest
    manifest_path = test_data_dir / "manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"\n✅ Downloaded {len(manifest)} documents")
    print(f"   Epics: {sum(1 for m in manifest if m['type'] == 'epic')}")
    print(f"   Stories: {sum(1 for m in manifest if m['type'] == 'story')}")
    print(f"   Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
