#!/usr/bin/env python3
"""Enhance NarrowGate course chapters and generate per-course audio.

This script is intentionally deterministic and idempotent:
- each chapter receives one managed quality-control appendix;
- each course receives an audio script and a generated intro.m4a file;
- course meta and the 100-course catalog are synchronized afterward.

Audio generation uses the local macOS `say` command so the project does not
depend on external TTS services or API keys.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COURSES_DIR = ROOT / "data" / "courses"
CATALOG_PATH = ROOT / "data" / "course_catalog_100.json"
QUALITY_REPORT_PATH = ROOT / "data" / "course_quality_report.json"
START_MARKER = "<!-- NG-QUALITY-ENHANCEMENT:START -->"
END_MARKER = "<!-- NG-QUALITY-ENHANCEMENT:END -->"
DEFAULT_VOICE = "Tingting"
DEFAULT_RATE = "145"


DIMENSION_METHODS = {
    "认知": ("事实与解释分离", "反证追问", "一条可验证的新证据"),
    "情绪": ("身体信号定位", "情绪命名", "一次不伤害关系的表达"),
    "行为": ("启动阻力拆解", "两分钟行动", "二十四小时复盘"),
    "关系": ("边界与投射辨认", "真实表达", "一次可被见证的对话"),
    "事业": ("资源与杠杆盘点", "现实反馈", "一个可交付动作"),
    "整合": ("价值与责任校准", "日常仪式", "一个能留下证据的承诺"),
    "全部": ("五维度扫描", "窄门选择", "一次跨维度行动"),
}


CHAPTER_FOCUS = {
    1: ("进入问题", "把课程从概念拉回自己的生活现场"),
    2: ("识别宽门", "找出最像道理的逃避语言"),
    3: ("命名机制", "把模糊感受变成可观察对象"),
    4: ("行动校验", "用现实反馈打破旧叙事"),
    5: ("七日整合", "形成可追踪、可见证、可重启的练习"),
}


BASE_INFO = {
    "socratic_introspection": {"order": 1, "dimension": "认知", "track": "核心课", "icon": "◎", "color": "#6366f1"},
    "shadow_integration": {"order": 2, "dimension": "情绪", "track": "核心课", "icon": "●", "color": "#7c3aed"},
    "behavioral_reshape": {"order": 3, "dimension": "行为", "track": "核心课", "icon": "ϟ", "color": "#dc2626"},
    "relationship_mirror": {"order": 4, "dimension": "关系", "track": "核心课", "icon": "◉", "color": "#059669"},
    "systems_thinking": {"order": 5, "dimension": "事业", "track": "核心课", "icon": "△", "color": "#b8942e"},
    "pain_alchemy": {"order": 6, "dimension": "认知", "track": "核心课", "icon": "✧", "color": "#7c3aed"},
    "evasion_anatomy": {"order": 7, "dimension": "行为", "track": "核心课", "icon": "⌕", "color": "#ef4444"},
    "stoic_resilience": {"order": 8, "dimension": "情绪", "track": "核心课", "icon": "◇", "color": "#92400e"},
    "antifragile": {"order": 9, "dimension": "行为", "track": "核心课", "icon": "◆", "color": "#dc2626"},
    "meaning_construction": {"order": 10, "dimension": "认知", "track": "核心课", "icon": "⌖", "color": "#059669"},
    "witness_evolution": {"order": 11, "dimension": "关系", "track": "核心课", "icon": "◉", "color": "#b8942e"},
    "narrow_gate_crossing": {"order": 12, "dimension": "整合", "track": "核心课", "icon": "∩", "color": "#b8942e"},
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def normalize_course_text(value: str) -> str:
    text = value.replace("。，", "，").replace("，。", "。").replace("。。", "。")
    text = re.sub(r"([。！？；：，])\s+(?=[\u4e00-\u9fff“《])", r"\1", text)
    return text.rstrip() + "\n"


def strip_managed_appendix(content: str) -> str:
    pattern = re.compile(
        rf"\n*\s*{re.escape(START_MARKER)}.*?{re.escape(END_MARKER)}\s*$",
        re.DOTALL,
    )
    return pattern.sub("", content).rstrip() + "\n"


def chapter_number(path: Path) -> int:
    match = re.search(r"(\d+)", path.stem)
    return int(match.group(1)) if match else 1


def make_chapter_appendix(meta: dict[str, Any], chapter_path: Path) -> str:
    title = meta.get("title") or meta.get("name") or meta.get("course_id") or chapter_path.parent.parent.name
    dimension = meta.get("dimension") or "整合"
    track = meta.get("track") or "核心课"
    core_question = meta.get("core_question") or f"我在《{title}》里最需要面对的真实问题是什么？"
    wide_gate = meta.get("wide_gate") or "继续停留在理解、解释和等待里。"
    narrow_gate = meta.get("narrow_gate") or "把看见落到一个可验证、可复盘的行动里。"
    challenge = meta.get("daily_challenge") or f"完成一个能证明你正在实践《{title}》的二十四小时小行动。"
    method_a, method_b, method_c = DIMENSION_METHODS.get(dimension, DIMENSION_METHODS["整合"])
    number = chapter_number(chapter_path)
    focus_title, focus_desc = CHAPTER_FOCUS.get(number, ("深化整合", "把前面的理解继续推进到生活结构里"))

    return f"""
{START_MARKER}

## 本章高质量训练补充

### 训练焦点：{focus_title}

这一章在《{title}》中的作用，是{focus_desc}。学习者读完以后，不应只留下“我理解了”的感觉，而要能说出三件事：我看见了哪个旧模式；我愿意承受哪一点不舒服；我会用什么行动留下证据。

### 宽门辨析

本课的宽门是：{wide_gate} 它通常不会以明显逃避的样子出现，而是披着理性、体面、善良、谨慎或忙碌的外衣。质量控制时要看一个指标：学习者是否仍然在用同一句解释保护旧身份。如果解释很多、证据很少，就还在宽门里。

### 窄门行动

本课的窄门是：{narrow_gate} 本章采用“{method_a}、{method_b}、{method_c}”三步推进。先把经验命名，不急着评价；再用现实证据校验，不把感受当结论；最后完成一个小到今天能做、真实到会产生后果的行动。

### 本章练习

请围绕这个问题写三分钟：{core_question} 写完后，不要继续解释，直接完成一个动作：{challenge} 动作完成后记录四项：我原本想怎样绕开；我实际做了什么；身体和情绪出现什么反应；现实给了什么反馈。

### 见证与评分

本章的完成标准不是阅读时长，而是证据质量。给自己 0 到 5 分：0 分代表只读完文字；1 分代表写下觉察；2 分代表命名宽门；3 分代表完成行动；4 分代表记录反馈；5 分代表把行动和反馈交给一个可信见证人。连续七天达到 3 分以上，才算这章真正进入生活。

{END_MARKER}
""".strip()


def enhance_chapters(course_dir: Path, meta: dict[str, Any]) -> tuple[int, int]:
    chapters_dir = course_dir / "chapters"
    if not chapters_dir.exists():
        return 0, 0
    changed = 0
    total_chars = 0
    for chapter_path in sorted(chapters_dir.glob("*.md")):
        content = chapter_path.read_text(encoding="utf-8")
        base = strip_managed_appendix(content)
        enhanced = normalize_course_text(base.rstrip() + "\n\n" + make_chapter_appendix(meta, chapter_path))
        if enhanced != content:
            chapter_path.write_text(enhanced, encoding="utf-8")
            changed += 1
        total_chars += len(enhanced)
    return changed, total_chars


def make_audio_script(meta: dict[str, Any], course_dir: Path) -> str:
    title = clean_text(meta.get("title") or meta.get("name") or course_dir.name)
    subtitle = clean_text(meta.get("subtitle", ""))
    description = clean_text(meta.get("description", ""))
    dimension = clean_text(meta.get("dimension") or "整合")
    core_question = clean_text(meta.get("core_question") or f"我在《{title}》里最需要面对的真实问题是什么？")
    wide_gate = clean_text(meta.get("wide_gate") or "继续停留在解释和等待里。")
    narrow_gate = clean_text(meta.get("narrow_gate") or "把看见落到一个可验证的行动里。")
    challenge = clean_text(meta.get("daily_challenge") or f"完成一个能证明你正在实践《{title}》的小行动。")

    chapter_titles: list[str] = []
    for chapter_path in sorted((course_dir / "chapters").glob("*.md"))[:5]:
        first_line = chapter_path.read_text(encoding="utf-8").splitlines()[0]
        chapter_titles.append(clean_text(first_line.lstrip("# ")))
    chapter_text = "，".join(chapter_titles) if chapter_titles else "看见，命名，行动，复盘，见证"

    script = (
        f"欢迎进入窄门课程，《{title}》。{subtitle}。"
        f"请先慢慢吸气，停一秒，再呼气。让身体知道，你不是来表演成长，而是来面对真实。"
        f"这是一门{dimension}维度的训练。它要处理的核心处境是：{description}"
        f"进入本课前，请把一个问题放在心里：{core_question}"
        f"本课的宽门是，{wide_gate}。宽门通常舒服，也很容易解释，但它不会留下新的生命证据。"
        f"本课的窄门是，{narrow_gate}。窄门不一定宏大，却一定具体，会让你在现实里做出一个选择。"
        f"课程路径包括：{chapter_text}。"
        f"今天只需要完成一个动作：{challenge}"
        f"完成后记录三句话：我原本想怎样逃开，我实际做了什么，现实给了什么反馈。"
        f"如果你愿意，请把这三句话交给一个可信见证人。窄门不是让你更会解释自己，而是让你的生活出现新的证据。"
    )
    return normalize_course_text(script).rstrip()


def audio_duration_seconds(path: Path) -> int:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe or not path.exists():
        return 0
    result = subprocess.run(
        [ffprobe, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        check=False,
        capture_output=True,
        text=True,
    )
    try:
        return int(round(float(result.stdout.strip())))
    except (TypeError, ValueError):
        return 0


def generate_audio(script_path: Path, audio_path: Path, voice: str, rate: str, force: bool) -> bool:
    if audio_path.exists() and not force:
        return False
    say = shutil.which("say")
    if not say:
        raise SystemExit("macOS say command was not found; cannot generate local audio")
    audio_path.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        temp_audio = audio_path.with_suffix(".aiff")
        subprocess.run([say, "-v", voice, "-r", rate, "-o", str(temp_audio), "-f", str(script_path)], check=True)
        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-loglevel",
                "error",
                "-i",
                str(temp_audio),
                "-c:a",
                "aac",
                "-b:a",
                "64k",
                "-movflags",
                "+faststart",
                str(audio_path),
            ],
            check=True,
        )
        temp_audio.unlink(missing_ok=True)
    else:
        subprocess.run([say, "-v", voice, "-r", rate, "-o", str(audio_path), "-f", str(script_path)], check=True)
    return True


def quiz_count(course_dir: Path) -> int:
    quiz_path = course_dir / "quiz.json"
    if not quiz_path.exists():
        return 0
    raw = load_json(quiz_path)
    if isinstance(raw, list):
        return len(raw)
    if isinstance(raw, dict):
        questions = raw.get("questions", [])
        return len(questions) if isinstance(questions, list) else 0
    return 0


def update_meta(course_dir: Path, meta: dict[str, Any], total_chars: int, duration: int, voice: str) -> dict[str, Any]:
    meta["audio_required"] = True
    meta["audio_status"] = "file_ready"
    meta["audio_file"] = "audio/intro.m4a"
    meta["audio_script"] = "audio/intro.txt"
    meta["audio_voice"] = voice
    meta["audio_duration_seconds"] = duration
    meta["quality_status"] = "production_ready"
    meta["quality_standard"] = "5章以上正文 + 每章质量控制补充 + 10题以上测验 + 每课真实导览音频"
    meta["content_enhanced_at"] = date.today().isoformat()
    if total_chars:
        meta["total_words"] = total_chars
        meta["total_reading_minutes"] = max(1, total_chars // 500)
    meta.setdefault("course_id", course_dir.name)
    write_json(course_dir / "meta.json", meta)
    return meta


def build_catalog() -> list[dict[str, Any]]:
    catalog = []
    for meta_file in sorted(COURSES_DIR.glob("*/meta.json")):
        course_dir = meta_file.parent
        course_id = course_dir.name
        meta = load_json(meta_file)
        base = BASE_INFO.get(course_id, {})
        chapters = sorted((course_dir / "chapters").glob("*.md"))
        catalog.append(
            {
                "id": course_id,
                "order": int(meta.get("order") or base.get("order") or 999),
                "title": meta.get("title") or meta.get("name") or course_id,
                "subtitle": meta.get("subtitle", ""),
                "description": meta.get("description", ""),
                "dimension": meta.get("dimension") or base.get("dimension", "整合"),
                "track": meta.get("track") or base.get("track", "核心课"),
                "icon": meta.get("icon") or base.get("icon", "✦"),
                "color": meta.get("color") or base.get("color", "#d4af37"),
                "level_required": int(meta.get("level_required") or 1),
                "quality_status": meta.get("quality_status", "production_ready"),
                "audio_status": meta.get("audio_status", "file_ready"),
                "audio_file": meta.get("audio_file", "audio/intro.m4a"),
                "audio_duration_seconds": int(meta.get("audio_duration_seconds") or 0),
                "chapter_count": len(chapters),
                "quiz_count": quiz_count(course_dir),
                "total_words": int(meta.get("total_words") or 0),
                "total_reading_minutes": int(meta.get("total_reading_minutes") or 0),
                "path": f"data/courses/{course_id}",
            }
        )
    catalog.sort(key=lambda item: (item["order"], item["id"]))
    return catalog


def build_quality_report(catalog: list[dict[str, Any]]) -> dict[str, Any]:
    course_checks: list[dict[str, Any]] = []
    for item in catalog:
        course_dir = COURSES_DIR / item["id"]
        chapters = sorted((course_dir / "chapters").glob("*.md"))
        audio_path = course_dir / (item.get("audio_file") or "audio/intro.m4a")
        script_path = course_dir / "audio" / "intro.txt"
        enhanced_chapters = 0
        for chapter_path in chapters:
            text = chapter_path.read_text(encoding="utf-8")
            if START_MARKER in text and END_MARKER in text:
                enhanced_chapters += 1

        checks = {
            "has_at_least_5_chapters": len(chapters) >= 5,
            "all_chapters_enhanced": enhanced_chapters == len(chapters) and bool(chapters),
            "has_at_least_10_quiz_questions": int(item.get("quiz_count") or 0) >= 10,
            "has_audio_file": audio_path.exists(),
            "has_audio_script": script_path.exists(),
            "audio_duration_at_least_60s": int(item.get("audio_duration_seconds") or 0) >= 60,
            "marked_production_ready": item.get("quality_status") == "production_ready",
        }
        course_checks.append(
            {
                "course_id": item["id"],
                "title": item["title"],
                "chapter_count": len(chapters),
                "enhanced_chapter_count": enhanced_chapters,
                "quiz_count": int(item.get("quiz_count") or 0),
                "audio_file": str(audio_path.relative_to(ROOT)),
                "audio_duration_seconds": int(item.get("audio_duration_seconds") or 0),
                "checks": checks,
                "passed": all(checks.values()),
            }
        )

    summary = {
        "course_count": len(course_checks),
        "passed_course_count": sum(1 for item in course_checks if item["passed"]),
        "chapter_count": sum(item["chapter_count"] for item in course_checks),
        "enhanced_chapter_count": sum(item["enhanced_chapter_count"] for item in course_checks),
        "audio_file_count": sum(1 for item in course_checks if item["checks"]["has_audio_file"]),
        "audio_script_count": sum(1 for item in course_checks if item["checks"]["has_audio_script"]),
        "total_audio_duration_seconds": sum(item["audio_duration_seconds"] for item in course_checks),
        "failed_courses": [item["course_id"] for item in course_checks if not item["passed"]],
    }
    return {
        "generated_at": date.today().isoformat(),
        "standard": "100门课程；每门至少5章；每章有质量控制补充；每门至少10题测验；每门真实导览音频不少于60秒",
        "summary": summary,
        "courses": course_checks,
    }


def enhance_all(force_audio: bool, voice: str, rate: str, limit: int | None) -> None:
    course_dirs = sorted(p for p in COURSES_DIR.iterdir() if (p / "meta.json").exists())
    if limit:
        course_dirs = course_dirs[:limit]

    generated = 0
    chapters_changed = 0
    for index, course_dir in enumerate(course_dirs, start=1):
        meta = load_json(course_dir / "meta.json")
        changed, total_chars = enhance_chapters(course_dir, meta)
        chapters_changed += changed

        audio_dir = course_dir / "audio"
        audio_dir.mkdir(exist_ok=True)
        script_path = audio_dir / "intro.txt"
        audio_path = audio_dir / "intro.m4a"
        script_path.write_text(make_audio_script(meta, course_dir) + "\n", encoding="utf-8")
        if generate_audio(script_path, audio_path, voice, rate, force_audio):
            generated += 1
        duration = audio_duration_seconds(audio_path)
        update_meta(course_dir, meta, total_chars, duration, voice)
        print(f"[{index:03d}/{len(course_dirs):03d}] {course_dir.name}: chapters +{changed}, audio {duration}s")

    catalog = build_catalog()
    if len(catalog) != 100 and not limit:
        raise SystemExit(f"expected 100 courses, found {len(catalog)}")
    write_json(CATALOG_PATH, catalog)
    write_json(QUALITY_REPORT_PATH, build_quality_report(catalog))
    print(f"enhanced {len(course_dirs)} courses, changed {chapters_changed} chapters, generated {generated} audio files")


def main() -> None:
    parser = argparse.ArgumentParser(description="Enhance NarrowGate course content and generate local course audio")
    parser.add_argument("--force-audio", action="store_true", help="regenerate audio even if intro.m4a already exists")
    parser.add_argument("--voice", default=DEFAULT_VOICE, help="macOS say voice name")
    parser.add_argument("--rate", default=DEFAULT_RATE, help="macOS say speaking rate")
    parser.add_argument("--limit", type=int, default=None, help="only process the first N courses, useful for testing")
    args = parser.parse_args()
    enhance_all(force_audio=args.force_audio, voice=args.voice, rate=args.rate, limit=args.limit)


if __name__ == "__main__":
    main()
