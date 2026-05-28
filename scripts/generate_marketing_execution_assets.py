#!/usr/bin/env python3
"""Generate publish-ready marketing operation assets for NarrowGate."""

from __future__ import annotations

import csv
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MARKETING_DIR = PROJECT_ROOT / "data" / "marketing"
DOCS_MARKETING_DIR = PROJECT_ROOT / "docs" / "data" / "marketing"
BASE_URL = "https://narrowgatemind.top"
CAMPAIGN = "narrowgate_launch_30d"


QUALITY_GATE = [
    "不承诺治愈、疗效或保证改变",
    "不制造焦虑式恐吓，不羞辱用户",
    "不替代医疗、心理治疗或危机干预",
    "引导用户做官网灵魂审计或课程试听，避免站外私下交易暗示",
    "发布前核对平台审核提示，必要时降低绝对化表达",
]


DIGITAL_HUMAN_PROFILE = {
    "name": "窄门导师",
    "persona": "平静、清醒、克制，不鸡血，不许诺，用一个问题推动行动。",
    "visual_style": "深色背景，金色窄门线条，半身数字人，低饱和光影，字幕清晰。",
    "voice_style": {
        "voice": "zh-CN-YunyangNeural 或同等沉稳中文男声",
        "rate": "-6% 到 -8%",
        "pitch": "-2Hz",
        "post_processing": "loudnorm=I=-16:TP=-1.5:LRA=9, 24000Hz, mono, MP3 48-64kbps",
    },
    "video_spec": {
        "aspect_ratio": "9:16",
        "duration_seconds": "20-45",
        "subtitle": "全程中文字幕，关键句用金色强调",
        "opening_frame": "第一帧必须出现问题句或冲突句",
    },
}


def landing_url(channel: str, day: int) -> str:
    content = f"day{day:02d}_{channel}"
    return (
        f"{BASE_URL}/?utm_source={channel}"
        f"&utm_medium=social&utm_campaign={CAMPAIGN}&utm_content={content}"
    )


def format_caption(item: dict) -> str:
    tags = " ".join(f"#{tag}" for tag in item.get("tags", []))
    parts = [item.get("hook", ""), item.get("body", ""), item.get("cta", ""), tags]
    return "\n\n".join(part for part in parts if part)


def build_assets(campaign: dict) -> list[dict]:
    assets = []
    for item in campaign["items"]:
        day = int(item["day"])
        channel = item["channel"]
        asset_id = f"day{day:02d}_{channel}"
        assets.append(
            {
                "id": asset_id,
                "day": day,
                "channel": channel,
                "title": item["title"],
                "hook": item["hook"],
                "caption": format_caption(item),
                "cta": item["cta"],
                "tags": item.get("tags", []),
                "creative_brief": item.get("asset", ""),
                "landing_url": landing_url(channel, day),
                "publish_status": "ready_to_publish",
                "quality_gate": QUALITY_GATE,
            }
        )
    return assets


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(path: Path, assets: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "id",
        "day",
        "channel",
        "title",
        "hook",
        "caption",
        "cta",
        "tags",
        "creative_brief",
        "landing_url",
        "publish_status",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for asset in assets:
            row = dict(asset)
            row["tags"] = " ".join(asset.get("tags", []))
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def build_digital_human_package(assets: list[dict]) -> dict:
    scripts = []
    for asset in assets:
        if asset["channel"] != "digital_human":
            continue
        scripts.append(
            {
                "id": asset["id"],
                "day": asset["day"],
                "title": asset["title"],
                "spoken_script": asset["caption"],
                "scene": DIGITAL_HUMAN_PROFILE["visual_style"],
                "landing_url": asset["landing_url"],
                "quality_gate": [
                    "口播时长控制在45秒以内",
                    "开头3秒必须提出一个清晰问题",
                    "字幕和口播一致，避免过度营销语气",
                    "结尾只给一个行动：做审计、听课程或预约演示",
                ],
            }
        )
    return {
        "project": "NarrowGate digital human launch package",
        "profile": DIGITAL_HUMAN_PROFILE,
        "scripts": scripts,
    }


def build_utm_links(assets: list[dict]) -> dict:
    links = {}
    for asset in assets:
        links.setdefault(asset["channel"], []).append(
            {
                "id": asset["id"],
                "day": asset["day"],
                "title": asset["title"],
                "url": asset["landing_url"],
            }
        )
    return {"campaign": CAMPAIGN, "base_url": BASE_URL, "links": links}


def build_week1_checklist(assets: list[dict]) -> dict:
    first_week = [asset for asset in assets if int(asset["day"]) <= 7]
    tasks = []
    for asset in first_week:
        tasks.extend(
            [
                {
                    "asset_id": asset["id"],
                    "day": asset["day"],
                    "channel": asset["channel"],
                    "task": "发布内容",
                    "owner": "运营",
                    "done": False,
                    "evidence": "发布链接",
                },
                {
                    "asset_id": asset["id"],
                    "day": asset["day"],
                    "channel": asset["channel"],
                    "task": "24小时数据回填",
                    "owner": "运营",
                    "done": False,
                    "evidence": "浏览、点赞、评论、收藏、线索数",
                },
            ]
        )
    return {
        "campaign": CAMPAIGN,
        "scope": "launch_week_1",
        "goal": "用首周7条跨渠道内容验证痛点、标题和转化链路。",
        "daily_rule": "每天发布1条内容，24小时后回填数据，周末只保留有效题材。",
        "tasks": tasks,
        "review_questions": [
            "哪一条内容带来了最多评论或私信？",
            "哪一个标题最适合继续复用？",
            "哪一个渠道带来的审计开始数最高？",
            "哪一条数字人脚本可以扩展成课程导览？",
        ],
    }


def main() -> None:
    campaign = json.loads((MARKETING_DIR / "launch_campaign_30d.json").read_text(encoding="utf-8"))
    assets = build_assets(campaign)
    publishing_package = {
        "project": "NarrowGate commercial launch",
        "campaign": CAMPAIGN,
        "base_url": BASE_URL,
        "channels": campaign.get("channels", []),
        "quality_gate": QUALITY_GATE,
        "items": assets,
    }
    outputs = {
        "publishing_assets.json": publishing_package,
        "digital_human_production.json": build_digital_human_package(assets),
        "utm_links.json": build_utm_links(assets),
        "week1_publish_checklist.json": build_week1_checklist(assets),
    }
    for filename, payload in outputs.items():
        write_json(MARKETING_DIR / filename, payload)
        write_json(DOCS_MARKETING_DIR / filename, payload)
    write_csv(MARKETING_DIR / "publishing_assets.csv", assets)
    write_csv(DOCS_MARKETING_DIR / "publishing_assets.csv", assets)
    print(f"Generated {len(assets)} publish-ready assets")


if __name__ == "__main__":
    main()
