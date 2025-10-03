# Test Data for Extraction Validation

This directory contains ground truth CSV files for validating LLM extraction accuracy.

## Files

- `sample_ground_truth_stories.csv` - Sample ground truth for 5 user stories
- `sample_ground_truth_epics.csv` - Sample ground truth for 4 epics
- `ground_truth_agent_lab_100.csv` - (To be created) Full 100-document ground truth from agent-lab repo

## CSV Format

### Stories CSV

```csv
document_id,expected_role,expected_action,expected_benefit,expected_status,expected_ac_count
docs/stories/story-2-1.md,backend developer,configure OLLAMA,extraction works,done,8
```

### Epics CSV

```csv
document_id,expected_title,expected_goal,expected_status,expected_story_count
docs/epics/epic-2.md,LLM Extraction,Extract structured data,in progress,9
```

## Usage

Run validation with:

```bash
python scripts/validate_extraction.py \
  --project-id 1 \
  --ground-truth-stories test_data/sample_ground_truth_stories.csv \
  --ground-truth-epics test_data/sample_ground_truth_epics.csv
```

## Creating Ground Truth

To create ground truth for a new repository:

1. Sync the repository via API to populate the database
2. Manually review each document and extract expected values
3. Fill in CSV files with expected_* columns
4. Use `document_id` as the file_path from the documents table (e.g., `docs/stories/story-1.md`)
5. Run validation script to measure accuracy
