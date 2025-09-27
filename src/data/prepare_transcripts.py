"""Utilities for converting raw AMI-style transcripts into structured JSON.

This module reads text transcripts where each speaker turn is formatted as
```
Speaker: Utterance text
```
and normalizes the turns into a machine-readable representation.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, List, Optional

SPEAKER_PATTERN = re.compile(r"^(?P<speaker>[^:]+):\s*(?P<text>.*)$")


@dataclass
class Turn:
    """Representation of a normalized speaker turn."""

    speaker: str
    utterance: str
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    annotations: Optional[dict] = None

    def to_dict(self) -> dict:
        data = asdict(self)
        # Ensure annotations defaults to the expected shape.
        data.setdefault("annotations", {"tasks": [], "actions": []})
        if data["annotations"] is None:
            data["annotations"] = {"tasks": [], "actions": []}
        return data


def normalize_speaker(raw: str) -> str:
    """Normalize speaker labels into a consistent identifier."""

    normalized = re.sub(r"\s+", " ", raw.strip())
    # Uppercase for consistency and replace spaces with underscores.
    return normalized.upper().replace(" ", "_")


def parse_transcript(text: Iterable[str]) -> List[Turn]:
    """Parse a transcript into normalized speaker turns."""

    turns: List[Turn] = []
    current_turn: Optional[Turn] = None

    for raw_line in text:
        line = raw_line.strip()
        if not line:
            continue

        match = SPEAKER_PATTERN.match(line)
        if match:
            speaker = normalize_speaker(match.group("speaker"))
            utterance = match.group("text").strip()
            current_turn = Turn(
                speaker=speaker,
                utterance=utterance,
                annotations={"tasks": [], "actions": []},
            )
            turns.append(current_turn)
        elif current_turn is not None:
            # Continuation of the previous speaker's utterance.
            current_turn.utterance = f"{current_turn.utterance} {line}".strip()
        else:
            # Line before any speaker tag; treat as narrator.
            current_turn = Turn(
                speaker="NARRATOR",
                utterance=line,
                annotations={"tasks": [], "actions": []},
            )
            turns.append(current_turn)

    return turns


def prepare_transcripts(input_dir: Path, output_dir: Path) -> None:
    """Convert raw transcripts in ``input_dir`` into JSON files in ``output_dir``."""

    output_dir.mkdir(parents=True, exist_ok=True)

    for transcript_path in sorted(input_dir.glob("*.txt")):
        with transcript_path.open("r", encoding="utf-8") as handle:
            turns = parse_transcript(handle)

        meeting_id = transcript_path.stem
        output_payload = {
            "meeting_id": meeting_id,
            "turns": [turn.to_dict() for turn in turns],
        }

        destination = output_dir / f"{meeting_id}.json"
        with destination.open("w", encoding="utf-8") as sink:
            json.dump(output_payload, sink, ensure_ascii=False, indent=2)

        print(f"Wrote {destination}")


def main(argv: Optional[Iterable[str]] = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/transcripts"),
        help="Directory containing raw transcript .txt files.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed"),
        help="Directory to write normalized JSON transcripts.",
    )
    args = parser.parse_args(argv)

    if not args.input.exists():
        raise FileNotFoundError(f"Input directory not found: {args.input}")

    prepare_transcripts(args.input, args.output)


if __name__ == "__main__":
    main()
