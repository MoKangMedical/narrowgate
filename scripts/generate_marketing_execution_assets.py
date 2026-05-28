#!/usr/bin/env python3
"""Generate publish-ready marketing operation assets for NarrowGate."""

from __future__ import annotations

import csv
import json
from datetime import date, datetime, time, timedelta
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MARKETING_DIR = PROJECT_ROOT / "data" / "marketing"
DOCS_MARKETING_DIR = PROJECT_ROOT / "docs" / "data" / "marketing"
BASE_URL = "https://narrowgatemind.top"
CAMPAIGN = "narrowgate_launch_30d"
LAUNCH_START_DATE = date(2026, 6, 1)
TIMEZONE = "Asia/Shanghai"


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


CHANNEL_OPERATIONS = {
    "xiaohongshu": {
        "label": "小红书",
        "account": "小红书｜窄门 NarrowGate（待绑定）",
        "owner": "内容运营",
        "support_owner": "设计/长图",
        "publish_time": time(21, 30),
        "asset_required": ["封面图", "长图正文", "首评引导", "UTM链接"],
        "metric_target": "收藏率>6%，评论>=8，官网点击>=20",
    },
    "douyin": {
        "label": "抖音",
        "account": "抖音｜窄门 NarrowGate（待绑定）",
        "owner": "短视频运营",
        "support_owner": "剪辑/字幕",
        "publish_time": time(19, 30),
        "asset_required": ["9:16视频", "强钩子字幕", "封面标题", "置顶评论"],
        "metric_target": "3秒留存>55%，评论>=10，主页点击>=25",
    },
    "digital_human": {
        "label": "数字人",
        "account": "数字人｜窄门导师（待绑定）",
        "owner": "数字人制作",
        "support_owner": "音频/后期",
        "publish_time": time(12, 20),
        "asset_required": ["数字人口播视频", "中文字幕", "金色关键词", "课程/审计CTA"],
        "metric_target": "完播率>30%，私信/线索>=3，脚本可复用",
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


def write_rows_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            normalized = {}
            for field in fieldnames:
                value = row.get(field, "")
                if isinstance(value, list):
                    value = "；".join(str(item) for item in value)
                normalized[field] = value
            writer.writerow(normalized)


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


def _sentence_chunks(text: str) -> list[str]:
    normalized = text.replace("\n", "。").replace("！", "。").replace("？", "。")
    chunks = [chunk.strip(" 。") for chunk in normalized.split("。") if chunk.strip(" 。#")]
    return chunks[:6] or [text.strip()]


def build_digital_human_storyboards(assets: list[dict]) -> dict:
    storyboards = []
    for asset in assets:
        if asset["channel"] != "digital_human":
            continue
        chunks = _sentence_chunks(asset["caption"])
        hook = chunks[0]
        insight = chunks[1] if len(chunks) > 1 else asset["hook"]
        action = chunks[2] if len(chunks) > 2 else asset["cta"]
        cta = asset["cta"]
        storyboards.append(
            {
                "id": asset["id"],
                "title": asset["title"],
                "aspect_ratio": "9:16",
                "duration_seconds": 42,
                "voice": DIGITAL_HUMAN_PROFILE["voice_style"],
                "visual_identity": DIGITAL_HUMAN_PROFILE["visual_style"],
                "landing_url": asset["landing_url"],
                "scenes": [
                    {
                        "time": "00:00-00:03",
                        "purpose": "强钩子",
                        "visual": "黑底金色窄门线条亮起，数字人平静看向镜头。",
                        "subtitle": hook,
                        "voiceover": hook,
                        "camera": "中近景，轻微推近。",
                    },
                    {
                        "time": "00:03-00:16",
                        "purpose": "命名真实问题",
                        "visual": "左侧浮现关键词，右侧保留数字人半身。",
                        "subtitle": insight,
                        "voiceover": insight,
                        "camera": "固定镜头，字幕逐行出现。",
                    },
                    {
                        "time": "00:16-00:32",
                        "purpose": "给出最小行动",
                        "visual": "画面出现一张极简行动卡，金色边框。",
                        "subtitle": action,
                        "voiceover": action,
                        "camera": "行动卡轻微上移，数字人保持慢速口播。",
                    },
                    {
                        "time": "00:32-00:42",
                        "purpose": "单一转化动作",
                        "visual": "出现窄门平台名、网址和课程/审计入口。",
                        "subtitle": cta,
                        "voiceover": cta,
                        "camera": "收束到金色门线，淡出。",
                    },
                ],
                "production_checklist": [
                    "第一帧必须能读出问题句",
                    "字幕不超过两行，关键词用金色",
                    "口播语速慢，避免兴奋式营销",
                    "结尾只保留一个转化动作",
                ],
            }
        )
    return {
        "project": "NarrowGate digital human storyboards",
        "profile": DIGITAL_HUMAN_PROFILE,
        "storyboards": storyboards,
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


def build_week1_publish_scripts(assets: list[dict]) -> tuple[dict, str]:
    first_week = [asset for asset in assets if int(asset["day"]) <= 7]
    items = []
    lines = [
        "# 窄门首周逐条发布话术",
        "",
        "用于第一周实际发布。每条包含标题/开场、正文或口播、评论区引导、发布后回填项。",
        "",
    ]
    for asset in first_week:
        channel_label = {
            "xiaohongshu": "小红书",
            "douyin": "抖音",
            "digital_human": "数字人",
        }.get(asset["channel"], asset["channel"])
        comment_prompt = "你现在最想逃开的那件事是什么？"
        if asset["channel"] == "douyin":
            comment_prompt = "评论一个字：门，我把7天行动清单发你。"
        if asset["channel"] == "digital_human":
            comment_prompt = "今天只回答一个问题：我在等准备好，还是在等不用害怕？"
        item = {
            "id": asset["id"],
            "day": asset["day"],
            "channel": asset["channel"],
            "channel_label": channel_label,
            "title": asset["title"],
            "opening": asset["hook"],
            "publish_copy": asset["caption"],
            "cover_text": asset["hook"][:28],
            "comment_prompt": comment_prompt,
            "landing_url": asset["landing_url"],
            "after_publish_metrics": ["views", "likes", "comments", "favorites", "shares", "leads"],
        }
        items.append(item)
        lines.extend(
            [
                f"## Day {asset['day']} · {channel_label}",
                "",
                f"**标题/开场**：{asset['title']}",
                "",
                f"**封面文案**：{item['cover_text']}",
                "",
                "**发布正文/口播**：",
                "",
                asset["caption"],
                "",
                f"**评论区引导**：{comment_prompt}",
                "",
                f"**追踪链接**：{asset['landing_url']}",
                "",
                "**发布后24小时回填**：浏览、点赞、评论、收藏、转发、线索数。",
                "",
            ]
        )
    return (
        {
            "campaign": CAMPAIGN,
            "scope": "launch_week_1_publish_scripts",
            "items": items,
        },
        "\n".join(lines).rstrip() + "\n",
    )


def build_launch_production_calendar(assets: list[dict], days: int = 14) -> tuple[dict, str]:
    scheduled_assets = [asset for asset in assets if int(asset["day"]) <= days]
    calendar = []
    for asset in scheduled_assets:
        ops = CHANNEL_OPERATIONS[asset["channel"]]
        publish_date = LAUNCH_START_DATE + timedelta(days=int(asset["day"]) - 1)
        publish_at = datetime.combine(publish_date, ops["publish_time"])
        production_deadline = publish_at - timedelta(hours=6)
        review_at = publish_at + timedelta(days=1)
        calendar.append(
            {
                "asset_id": asset["id"],
                "day": asset["day"],
                "date": publish_date.isoformat(),
                "weekday": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][publish_date.weekday()],
                "channel": asset["channel"],
                "channel_label": ops["label"],
                "account": ops["account"],
                "owner": ops["owner"],
                "support_owner": ops["support_owner"],
                "publish_at": publish_at.isoformat(timespec="minutes"),
                "production_deadline": production_deadline.isoformat(timespec="minutes"),
                "review_at": review_at.isoformat(timespec="minutes"),
                "timezone": TIMEZONE,
                "title": asset["title"],
                "asset_required": ops["asset_required"],
                "landing_url": asset["landing_url"],
                "metric_target": ops["metric_target"],
                "status": "scheduled",
                "pre_publish_checklist": [
                    "封面/第一帧在3秒内读懂",
                    "正文或口播不承诺疗效、不制造恐吓",
                    "评论区引导只保留一个动作",
                    "发布后24小时回填浏览、互动、评论、收藏、线索",
                ],
            }
        )
    markdown_lines = [
        "# 窄门14天发布作战表",
        "",
        f"- 启动日期：{LAUNCH_START_DATE.isoformat()}",
        f"- 时区：{TIMEZONE}",
        "- 用途：把小红书、抖音、数字人内容从素材库推进到账号、负责人、发布时间和复盘动作。",
        "",
        "| 天 | 日期 | 渠道 | 账号 | 负责人 | 发布时间 | 素材 | 指标目标 |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for item in calendar:
        markdown_lines.append(
            "| {day} | {date} {weekday} | {channel_label} | {account} | {owner}/{support_owner} | {publish_at} | {title} | {metric_target} |".format(
                **item
            )
        )
    markdown_lines.extend(
        [
            "",
            "## 每日闭环",
            "",
            "1. 发布前6小时锁定封面、脚本、字幕、链接。",
            "2. 发布后30分钟检查链接、评论区引导和平台审核状态。",
            "3. 发布后24小时回填数据到增长执行台。",
            "4. 每周保留高评论、高收藏、高线索题材，扩写成数字人口播或小红书长图。",
            "",
        ]
    )
    payload = {
        "campaign": CAMPAIGN,
        "scope": "launch_first_14_days",
        "start_date": LAUNCH_START_DATE.isoformat(),
        "timezone": TIMEZONE,
        "purpose": "明确小红书、抖音、数字人的账号、负责人、发布时间、素材要求和复盘指标。",
        "calendar": calendar,
    }
    return payload, "\n".join(markdown_lines)


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
        "digital_human_storyboards.json": build_digital_human_storyboards(assets),
        "utm_links.json": build_utm_links(assets),
        "week1_publish_checklist.json": build_week1_checklist(assets),
    }
    week1_scripts, week1_markdown = build_week1_publish_scripts(assets)
    production_calendar, production_calendar_markdown = build_launch_production_calendar(assets)
    outputs["week1_publish_scripts.json"] = week1_scripts
    outputs["launch_production_calendar.json"] = production_calendar
    for filename, payload in outputs.items():
        write_json(MARKETING_DIR / filename, payload)
        write_json(DOCS_MARKETING_DIR / filename, payload)
    for base_dir in (MARKETING_DIR, DOCS_MARKETING_DIR):
        (base_dir / "week1_publish_scripts.md").write_text(week1_markdown, encoding="utf-8")
        (base_dir / "launch_production_calendar.md").write_text(production_calendar_markdown, encoding="utf-8")
    write_csv(MARKETING_DIR / "publishing_assets.csv", assets)
    write_csv(DOCS_MARKETING_DIR / "publishing_assets.csv", assets)
    calendar_fields = [
        "asset_id",
        "day",
        "date",
        "weekday",
        "channel_label",
        "account",
        "owner",
        "support_owner",
        "publish_at",
        "production_deadline",
        "review_at",
        "title",
        "asset_required",
        "metric_target",
        "status",
        "landing_url",
    ]
    write_rows_csv(MARKETING_DIR / "launch_production_calendar.csv", production_calendar["calendar"], calendar_fields)
    write_rows_csv(DOCS_MARKETING_DIR / "launch_production_calendar.csv", production_calendar["calendar"], calendar_fields)
    print(f"Generated {len(assets)} publish-ready assets")


if __name__ == "__main__":
    main()
