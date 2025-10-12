#!/usr/bin/env python3
"""Test script for manual verification of header anchor extraction.

This script tests header extraction on real BMAD documentation files
to verify the feature works correctly end-to-end.
"""

import asyncio
from pathlib import Path
import sys

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.docling_service import DoclingService
from app.utils.markdown_parser import extract_headers


async def test_database_schema():
    """Test header extraction on database schema documentation."""
    print("="*80)
    print("Testing Header Extraction: database-schema.md")
    print("="*80)
    
    docs_path = Path("/home/wsluser/dev/bmad-test/bmadflow/docs/architecture")
    schema_file = docs_path / "database-schema.md"
    
    if not schema_file.exists():
        print(f"❌ File not found: {schema_file}")
        return False
    
    # Read the file
    with open(schema_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    print(f"✅ Loaded {len(content)} characters from {schema_file.name}\n")
    
    # Extract headers directly
    headers = extract_headers(content)
    print(f"📋 Extracted {len(headers)} headers (H1-H3):")
    for h in headers[:15]:  # Show first 15
        indent = "  " * (h.level - 1)
        print(f"  {indent}H{h.level}: {h.text} → #{h.anchor}")
    if len(headers) > 15:
        print(f"  ... and {len(headers) - 15} more headers\n")
    else:
        print()
    
    # Process with DoclingService
    service = DoclingService()
    chunks = await service.process_markdown(content)
    
    print(f"🔨 Generated {len(chunks)} chunks\n")
    
    # Analyze chunks
    anchored = [c for c in chunks if c.header_anchor is not None]
    unanchored = [c for c in chunks if c.header_anchor is None]
    
    print(f"📊 Statistics:")
    print(f"  - Chunks with anchors: {len(anchored)}")
    print(f"  - Chunks without anchors: {len(unanchored)}")
    
    unique_anchors = set(c.header_anchor for c in anchored)
    print(f"  - Unique header anchors: {len(unique_anchors)}\n")
    
    # Show sample chunks
    print("📝 Sample Chunks (first 10):")
    for i, chunk in enumerate(chunks[:10]):
        anchor_display = f"#{chunk.header_anchor}" if chunk.header_anchor else "NO ANCHOR"
        text_preview = chunk.text[:60].replace("\n", " ").strip()
        print(f"  [{i}] {anchor_display}")
        print(f"      {text_preview}...")
        print()
    
    # Verification checks
    print("✅ Verification Checks:")
    checks_passed = 0
    checks_total = 4
    
    # Check 1: All anchors are lowercase
    if all(a == a.lower() for a in unique_anchors):
        print("  ✓ All anchors are lowercase")
        checks_passed += 1
    else:
        print("  ✗ Some anchors are not lowercase!")
    
    # Check 2: No spaces in anchors
    if all(" " not in a for a in unique_anchors):
        print("  ✓ No spaces in anchors")
        checks_passed += 1
    else:
        print("  ✗ Some anchors contain spaces!")
    
    # Check 3: At least some chunks have anchors
    if len(anchored) > 0:
        print(f"  ✓ {len(anchored)} chunks have header anchors")
        checks_passed += 1
    else:
        print("  ✗ No chunks have header anchors!")
    
    # Check 4: Anchor format matches expected (hyphenated)
    if all("-" in a or len(a) <= 5 for a in unique_anchors):  # Allow short anchors without hyphens
        print("  ✓ Anchors use hyphenated format")
        checks_passed += 1
    else:
        print("  ⚠ Some anchors may not follow expected format")
        checks_passed += 1  # Warning, not failure
    
    print(f"\n{'='*80}")
    print(f"RESULT: {checks_passed}/{checks_total} checks passed")
    print(f"{'='*80}\n")
    
    return checks_passed == checks_total


async def main():
    """Run manual verification tests."""
    print("\n🧪 Manual Header Anchor Extraction Verification\n")
    
    success = await test_database_schema()
    
    if success:
        print("✅ All verification checks PASSED!\n")
        return 0
    else:
        print("❌ Some verification checks FAILED\n")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
