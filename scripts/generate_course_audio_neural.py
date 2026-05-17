#!/usr/bin/env python3
"""Generate NarrowGate course audio with the neural audio standard.

Pipeline:
1. create a 150-230 character course oral script, optionally with DeepSeek;
2. synthesize with edge_tts and zh-CN-YunyangNeural by default;
3. normalize with ffmpeg loudnorm and export 24kHz mono MP3.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path
from typing import Any

import requests


ROOT = Path(__file__).resolve().parents[1]
COURSES_DIR = ROOT / "data" / "courses"
DEFAULT_VOICE = "zh-CN-YunyangNeural"
DEFAULT_RATE = "-8%"
DEFAULT_PITCH = "-2Hz"
DEFAULT_BITRATE = "48k"
DEFAULT_MODEL = "deepseek-v4-flash"
LOUDNORM_FILTER = "loudnorm=I=-16:TP=-1.5:LRA=9"
SAMPLE_RATE = 24000
CHANNELS = 1
MIN_SCRIPT_CHARS = 150
MAX_SCRIPT_CHARS = 230

sys.path.insert(0, str(ROOT / "scripts"))
from enhance_courses_and_audio import build_catalog, build_quality_report, write_json  # noqa: E402


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def clean_text(value: str) -> str:
    text = re.sub(r"\s+", " ", value or "").strip()
    return text.replace("。，", "，").replace("，。", "。").replace("。。", "。")


def trim_phrase(value: str, limit: int) -> str:
    value = clean_text(value)
    return value if len(value) <= limit else value[:limit].rstrip("，。；：、 ") + "..."


def fit_script_length(script: str) -> str:
    script = clean_text(script)
    if len(script) <= MAX_SCRIPT_CHARS:
        if len(script) < MIN_SCRIPT_CHARS:
            script += "不用急着变好，只要诚实看见，并完成一个能留下证据的小行动。"
        return clean_text(script)

    sentences = re.split(r"(?<=[。！？])", script)
    result = ""
    for sentence in sentences:
        if len(result + sentence) > MAX_SCRIPT_CHARS:
            break
        result += sentence
    if len(result) < MIN_SCRIPT_CHARS:
        result = script[:MAX_SCRIPT_CHARS].rstrip("，。；：、 ") + "。"
    return clean_text(result)


def local_oral_script(meta: dict[str, Any], course_dir: Path) -> str:
    title = clean_text(meta.get("title") or meta.get("name") or course_dir.name)
    subtitle = trim_phrase(meta.get("subtitle", ""), 28)
    core_question = trim_phrase(
        meta.get("core_question") or f"我在《{title}》里最需要面对的真实问题是什么？",
        36,
    )
    wide_gate = trim_phrase(meta.get("wide_gate") or "继续停留在解释和等待里", 26)
    narrow_gate = trim_phrase(meta.get("narrow_gate") or "把看见落到一个可验证的行动里", 30)
    challenge = trim_phrase(meta.get("daily_challenge") or f"完成一个能证明你正在实践《{title}》的小行动", 34)
    description = trim_phrase(meta.get("description", ""), 48)

    script = (
        f"欢迎进入《{title}》。{subtitle}。这不是一门增加道理的课，而是训练你看见自己如何走宽门。"
        f"{description}请把这个问题放在心里：{core_question}"
        f"当你想{wide_gate}时，先停一下，选择{narrow_gate}。"
        f"今天只完成一个动作：{challenge}。"
        f"完成后记录三句话：我想逃开什么，我做了什么，现实给了什么反馈。"
    )
    return fit_script_length(script)


def deepseek_oral_script(meta: dict[str, Any], local_fallback: str) -> str | None:
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return None

    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
    model = os.getenv("DEEPSEEK_MODEL", DEFAULT_MODEL)
    endpoint = f"{base_url}/chat/completions"
    prompt = {
        "title": meta.get("title") or meta.get("name"),
        "subtitle": meta.get("subtitle", ""),
        "description": meta.get("description", ""),
        "core_question": meta.get("core_question", ""),
        "wide_gate": meta.get("wide_gate", ""),
        "narrow_gate": meta.get("narrow_gate", ""),
        "daily_challenge": meta.get("daily_challenge", ""),
    }
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "你是窄门课程的中文口播稿作者。请写150到230个中文字符的课程导入稿。"
                    "要求像老师对学习者说话，温和、沉稳、有停顿感；不要Markdown；不要标题；不要逐字复述正文。"
                    "必须包含：课程要面对的真实问题、宽门、窄门、今天的最小行动。"
                ),
            },
            {
                "role": "user",
                "content": json.dumps(prompt, ensure_ascii=False),
            },
        ],
        "temperature": 0.35,
        "max_tokens": 360,
        "stream": False,
    }
    try:
        response = requests.post(
            endpoint,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        text = response.json()["choices"][0]["message"]["content"]
        return fit_script_length(text)
    except Exception as exc:
        print(f"DeepSeek script generation failed; using local fallback. reason={exc}")
        return local_fallback


async def edge_tts_save(text: str, path: Path, voice: str, rate: str, pitch: str) -> None:
    import edge_tts

    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate, pitch=pitch)
    await communicate.save(str(path))


def normalize_audio(raw_path: Path, output_path: Path, bitrate: str) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise SystemExit("ffmpeg was not found; cannot normalize audio")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-loglevel",
            "error",
            "-i",
            str(raw_path),
            "-af",
            LOUDNORM_FILTER,
            "-ar",
            str(SAMPLE_RATE),
            "-ac",
            str(CHANNELS),
            "-c:a",
            "libmp3lame",
            "-b:a",
            bitrate,
            str(output_path),
        ],
        check=True,
    )


def probe_audio(path: Path) -> dict[str, Any]:
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
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return {}
    data = json.loads(result.stdout or "{}")
    stream = (data.get("streams") or [{}])[0]
    fmt = data.get("format") or {}
    return {
        "codec": stream.get("codec_name", ""),
        "sample_rate": int(stream.get("sample_rate") or 0),
        "channels": int(stream.get("channels") or 0),
        "bit_rate": int(stream.get("bit_rate") or fmt.get("bit_rate") or 0),
        "duration_seconds": round(float(fmt.get("duration") or 0), 3),
    }


def update_course_meta(
    course_dir: Path,
    meta: dict[str, Any],
    audio_file: str,
    script_file: str,
    probe: dict[str, Any],
    voice: str,
    rate: str,
    pitch: str,
    bitrate: str,
    script_provider: str,
) -> None:
    meta["audio_required"] = True
    meta["audio_status"] = "file_ready"
    meta["audio_file"] = audio_file
    meta["audio_script"] = script_file
    meta["audio_provider"] = "edge_tts"
    meta["audio_model"] = "edge_tts"
    meta["audio_voice"] = voice
    meta["audio_rate"] = rate
    meta["audio_pitch"] = pitch
    meta["audio_format"] = "mp3"
    meta["audio_bitrate"] = bitrate
    meta["audio_sample_rate"] = SAMPLE_RATE
    meta["audio_channels"] = CHANNELS
    meta["audio_loudnorm"] = LOUDNORM_FILTER
    meta["audio_script_provider"] = script_provider
    meta["audio_duration_seconds"] = int(round(float(probe.get("duration_seconds") or 0)))
    meta["audio_min_duration_seconds"] = 25
    meta["audio_generation_standard"] = (
        "150-230字课程口播稿 + zh-CN-YunyangNeural + 慢速低音调 + "
        "ffmpeg loudnorm=I=-16:TP=-1.5:LRA=9 + 24000Hz mono MP3"
    )
    meta["audio_enhanced_at"] = date.today().isoformat()
    (course_dir / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def generate_one(
    course_dir: Path,
    force: bool,
    voice: str,
    rate: str,
    pitch: str,
    bitrate: str,
    script_provider: str,
    dry_run: bool,
) -> tuple[bool, dict[str, Any]]:
    meta_path = course_dir / "meta.json"
    meta = load_json(meta_path)
    fallback = local_oral_script(meta, course_dir)
    provider_used = "local"
    if script_provider in {"auto", "deepseek"}:
        generated = deepseek_oral_script(meta, fallback)
        if generated:
            script = generated
            provider_used = "deepseek" if os.getenv("DEEPSEEK_API_KEY") else "local"
        elif script_provider == "deepseek":
            raise SystemExit("DEEPSEEK_API_KEY is required when --script-provider deepseek is used")
        else:
            script = fallback
    else:
        script = fallback

    script = fit_script_length(script)
    audio_dir = course_dir / "audio"
    script_path = audio_dir / "intro.txt"
    output_path = audio_dir / "intro.mp3"

    if dry_run:
        print(f"[dry-run] {course_dir.name} chars={len(script)} provider={provider_used}")
        print(script)
        return False, {"duration_seconds": 0}

    if output_path.exists() and not force:
        probe = probe_audio(output_path)
        return False, probe

    audio_dir.mkdir(exist_ok=True)
    script_path.write_text(script + "\n", encoding="utf-8")

    with tempfile.TemporaryDirectory(prefix="narrowgate_edge_tts_") as tmp:
        raw_path = Path(tmp) / "raw.mp3"
        asyncio.run(edge_tts_save(script, raw_path, voice, rate, pitch))
        normalize_audio(raw_path, output_path, bitrate)

    probe = probe_audio(output_path)
    update_course_meta(
        course_dir,
        meta,
        audio_file="audio/intro.mp3",
        script_file="audio/intro.txt",
        probe=probe,
        voice=voice,
        rate=rate,
        pitch=pitch,
        bitrate=bitrate,
        script_provider=provider_used,
    )
    return True, probe


def selected_courses(course_id: str | None, limit: int | None) -> list[Path]:
    if course_id:
        course_dir = COURSES_DIR / course_id
        if not (course_dir / "meta.json").exists():
            raise SystemExit(f"course not found: {course_id}")
        return [course_dir]
    course_dirs = sorted(p for p in COURSES_DIR.iterdir() if (p / "meta.json").exists())
    return course_dirs[:limit] if limit else course_dirs


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate NarrowGate neural course audio")
    parser.add_argument("--course-id", help="Generate one course by id")
    parser.add_argument("--limit", type=int, help="Generate first N courses")
    parser.add_argument("--force", action="store_true", help="Regenerate existing intro.mp3 files")
    parser.add_argument("--dry-run", action="store_true", help="Only print the generated oral script")
    parser.add_argument("--voice", default=os.getenv("EDGE_TTS_VOICE", DEFAULT_VOICE))
    parser.add_argument("--rate", default=os.getenv("EDGE_TTS_RATE", DEFAULT_RATE))
    parser.add_argument("--pitch", default=os.getenv("EDGE_TTS_PITCH", DEFAULT_PITCH))
    parser.add_argument("--bitrate", default=os.getenv("NEURAL_AUDIO_BITRATE", DEFAULT_BITRATE))
    parser.add_argument("--script-provider", choices=["auto", "local", "deepseek"], default="auto")
    args = parser.parse_args()

    generated = 0
    course_dirs = selected_courses(args.course_id, args.limit)
    for index, course_dir in enumerate(course_dirs, start=1):
        did_generate, probe = generate_one(
            course_dir=course_dir,
            force=args.force,
            voice=args.voice,
            rate=args.rate,
            pitch=args.pitch,
            bitrate=args.bitrate,
            script_provider=args.script_provider,
            dry_run=args.dry_run,
        )
        generated += int(did_generate)
        duration = probe.get("duration_seconds", 0)
        print(f"[{index:03d}/{len(course_dirs):03d}] {course_dir.name}: {'generated' if did_generate else 'skipped'} {duration}s")

    if not args.dry_run:
        catalog = build_catalog()
        write_json(ROOT / "data" / "course_catalog_100.json", catalog)
        write_json(ROOT / "data" / "course_quality_report.json", build_quality_report(catalog))
    print(f"generated {generated} neural audio files")


if __name__ == "__main__":
    main()
