"""
config.py — ZemenByte Bot Configuration
"""

import os
from dataclasses import dataclass, field
from typing import List


@dataclass
class Config:
    # ── Core ──────────────────────────────────────────────────────────────
    BOT_TOKEN:        str  = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
    CHANNEL_USERNAME: str  = os.getenv("CHANNEL_USERNAME", "ZemenByte")

    ADMIN_IDS: List[int] = field(default_factory=lambda: [
        int(x) for x in os.getenv("ADMIN_IDS", "7198677868").split(",") if x.strip()
    ])

    # ── Posting schedule ──────────────────────────────────────────────────
    POSTS_PER_DAY: int       = int(os.getenv("POSTS_PER_DAY", "6"))
    POST_HOURS:    List[int] = field(default_factory=lambda: [7, 10, 13, 16, 19, 22])

    # ── Topics & rotation ─────────────────────────────────────────────────
    # All 8 topics including new Technology and DeepTech
    TOPICS: List[str] = field(default_factory=lambda: [
        "AI", "Crypto", "Cybersecurity", "Quantum",
        "Innovation", "Tech", "Technology", "DeepTech"
    ])

    # Weighted rotation (must sum to 1.0)
    TOPIC_WEIGHTS: List[float] = field(default_factory=lambda: [
        0.22,   # AI
        0.15,   # Crypto
        0.15,   # Cybersecurity
        0.08,   # Quantum
        0.15,   # Innovation
        0.10,   # Tech
        0.10,   # Technology
        0.05,   # DeepTech
    ])

    # ── Language settings ─────────────────────────────────────────────────
    # Supported: "en" (English), "am" (Amharic), "orm" (Afaan Oromoo)
    LANGUAGES: List[str] = field(default_factory=lambda: ["en", "am", "orm"])

    # How often each language is used (must sum to 1.0)
    # Default: 50% English, 30% Amharic, 20% Afaan Oromoo
    LANGUAGE_WEIGHTS: List[float] = field(default_factory=lambda: [
        float(x) for x in os.getenv("LANGUAGE_WEIGHTS", "0.5,0.3,0.2").split(",")
    ])

    # ── Content flags ─────────────────────────────────────────────────────
    USE_EMOJIS:   bool = True
    USE_HASHTAGS: bool = True
    AUTO_ENGAGE:  bool = True

    # ── Analytics & state ─────────────────────────────────────────────────
    ANALYTICS_FILE: str = "analytics_data.json"
    SCHEDULE_FILE:  str = "schedule_state.json"

    # ── Dashboard secret ──────────────────────────────────────────────────
    DASHBOARD_SECRET: str = os.getenv("DASHBOARD_SECRET", "zemenbyte2025")
