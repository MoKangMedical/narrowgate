#!/usr/bin/env python3
"""Check local Qwen TTS configuration without exposing secrets."""

from __future__ import annotations

import os
import shutil
import sys


REQUIRED_ENV = [
    "DASHSCOPE_API_KEY",
    "DASHSCOPE_BASE_URL",
    "QWEN_TTS_MODEL",
    "QWEN_TTS_VOICE",
    "QWEN_TTS_LANGUAGE",
]


def mask_secret(value: str) -> str:
    if not value:
        return "MISSING"
    if len(value) <= 8:
        return "***"
    return f"{value[:4]}...{value[-4:]}"


def main() -> int:
    try:
        import dashscope  # noqa: F401
    except Exception as exc:
        print(f"dashscope: MISSING ({exc})")
        return 1

    print("dashscope: OK")
    print(f"ffmpeg: {'OK ' + shutil.which('ffmpeg') if shutil.which('ffmpeg') else 'MISSING'}")

    missing = []
    for key in REQUIRED_ENV:
        value = os.getenv(key, "")
        if not value:
            missing.append(key)
        display = mask_secret(value) if key == "DASHSCOPE_API_KEY" else (value or "MISSING")
        print(f"{key}: {display}")

    instructions = os.getenv("QWEN_TTS_INSTRUCTIONS", "")
    print(f"QWEN_TTS_INSTRUCTIONS: {'OK' if instructions else 'MISSING'}")

    if missing:
        print("\nMissing required variables. Configure them in your shell or local .env before generating Qwen audio.")
        return 2

    base_url = os.getenv("DASHSCOPE_BASE_URL", "")
    if not base_url.startswith("https://dashscope"):
        print("\nDASHSCOPE_BASE_URL looks unusual. Use the Beijing or Singapore DashScope endpoint.")
        return 3

    print("\nQwen TTS local setup looks ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
