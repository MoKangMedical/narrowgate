#!/usr/bin/env python3
"""Audit NarrowGate audio files against the neural MP3 standard."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COURSES_DIR = ROOT / "data" / "courses"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def probe_audio(path: Path) -> dict:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe or not path.exists():
        return {}
    result = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-select_streams",
            "a:0",
            "-show_entries",
            "stream=codec_name,sample_rate,channels,bit_rate",
            "-show_entries",
            "format=duration,bit_rate",
            "-of",
            "json",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return {}
    data = json.loads(result.stdout or "{}")
    stream = (data.get("streams") or [{}])[0]
    fmt = data.get("format") or {}
    return {
        "sample_rate": int(stream.get("sample_rate") or 0),
        "channels": int(stream.get("channels") or 0),
        "bit_rate": int(stream.get("bit_rate") or fmt.get("bit_rate") or 0),
        "duration": float(fmt.get("duration") or 0),
    }


def grade_audio(path: Path, probe: dict) -> str:
    if not path.exists():
        return "missing"
    if path.suffix.lower() != ".mp3":
        return "legacy"
    checks = [
        probe.get("sample_rate") == 24000,
        probe.get("channels") == 1,
        40000 <= int(probe.get("bit_rate") or 0) <= 76000,
        25 <= float(probe.get("duration") or 0) <= 120,
    ]
    return "A" if all(checks) else "needs_review"


def main() -> int:
    rows = []
    for meta_path in sorted(COURSES_DIR.glob("*/meta.json")):
        meta = load_json(meta_path)
        audio_rel = meta.get("audio_file") or "audio/intro.m4a"
        audio_path = meta_path.parent / audio_rel
        probe = probe_audio(audio_path)
        rows.append(
            {
                "course_id": meta_path.parent.name,
                "audio_file": str(audio_path.relative_to(ROOT)),
                "grade": grade_audio(audio_path, probe),
                **probe,
            }
        )

    summary = {}
    for row in rows:
        summary[row["grade"]] = summary.get(row["grade"], 0) + 1
    report = {
        "standard": "MP3, 24000Hz, mono, 48-64kbps, ffmpeg loudnorm=I=-16:TP=-1.5:LRA=9",
        "summary": summary,
        "courses": rows,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if summary.get("missing", 0) == 0 and summary.get("needs_review", 0) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
