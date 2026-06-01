"""
config.py — ZemenByte Bot Configuration
Edit this file OR set environment variables before running.
"""

import os
from dataclasses import dataclass, field
from typing import List


@dataclass
class Config:
    # ── Core ──────────────────────────────────────────────────────────────
    BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
    CHANNEL_USERNAME: str = os.getenv("CHANNEL_USERNAME", "ZemenByte")

    # List your Telegram numeric user IDs here (admins)
    ADMIN_IDS: List[int] = field(default_factory=lambda: [
        int(x) for x in os.getenv("ADMIN_IDS", "123456789").split(",") if x.strip()
    ])

    # ── Posting schedule ──────────────────────────────────────────────────
    POSTS_PER_DAY: int = int(os.getenv("POSTS_PER_DAY", "6"))
    # Preferred UTC posting hours (bot picks closest to these)
    POST_HOURS: List[int] = field(default_factory=lambda: [7, 10, 13, 16, 19, 22])

    # ── Topics & rotation ─────────────────────────────────────────────────
    TOPICS: List[str] = field(default_factory=lambda: [
        "AI", "Crypto", "Cybersecurity", "Quantum", "Innovation", "Tech"
    ])
    # Weighted rotation: higher number = more frequent
    TOPIC_WEIGHTS: List[float] = field(default_factory=lambda: [
        0.25, 0.20, 0.20, 0.10, 0.15, 0.10
    ])

    # ── Content flags ─────────────────────────────────────────────────────
    USE_EMOJIS: bool = True
    USE_HASHTAGS: bool = True
    AUTO_ENGAGE: bool = True
    LANGUAGES: List[str] = field(default_factory=lambda: ["en"])

    # ── Anthropic AI (optional — for Claude-powered posts) ─────────────
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    USE_AI_CONTENT: bool = bool(os.getenv("USE_AI_CONTENT", "false").lower() == "true")

    # ── Analytics persistence ─────────────────────────────────────────────
    ANALYTICS_FILE: str = "analytics_data.json"
    SCHEDULE_FILE: str  = "schedule_state.json"
