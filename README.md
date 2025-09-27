# Project Transcript Preparation

This repository includes utilities for preparing AMI-style meeting transcripts for downstream experiments.

## Raw transcripts

Place the eight AMI transcript files in `data/transcripts/` using the following filenames:

- `EN2001a.txt`
- `EN2001b.txt`
- `EN2001d.txt`
- `EN2001e.txt`
- `EN2002a.txt`
- `EN2002b.txt`
- `EN2002c.txt`
- `EN2002d.txt`

Sample placeholder transcripts are already provided in the repository so you can run the pipeline immediately.

## Preparing structured JSON

The ingestion script normalizes speaker turns and writes structured JSON files to the specified output directory. Run it with:

```bash
python -m src.data.prepare_transcripts --input data/transcripts --output data/processed
```

The command reads every `.txt` transcript in the input directory and writes a corresponding `.json` file into `data/processed/`. Each invocation prints the location of the files it writes so you can quickly confirm the output.

## Output format

Every generated JSON file follows this structure:

```json
{
  "meeting_id": "EN2001a",
  "turns": [
    {
      "speaker": "CHAIR",
      "utterance": "Good morning everyone, let's review yesterday's notes.",
      "start_time": null,
      "end_time": null,
      "annotations": {
        "tasks": [],
        "actions": []
      }
    }
  ]
}
```

- `meeting_id` is the stem of the transcript filename.
- `turns` is an ordered list of normalized speaker turns.
- `speaker` is uppercased and spaces are replaced with underscores so that each label is consistent across meetings.
- `utterance` contains the normalized text for that speaker turn. If a transcript line extends over multiple lines without a new speaker tag, the script concatenates it to the previous turn.
- `start_time` and `end_time` fields are included for future timestamp enrichment and currently set to `null`.
- `annotations.tasks` and `annotations.actions` are placeholders for future task labeling work.

Adjust the input or output paths with the `--input` and `--output` arguments when integrating with other pipelines.
