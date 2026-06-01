"""
scheduler.py — Post Schedule Manager
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from config import Config
from content_engine import ContentEngine


class PostScheduler:
    def __init__(self, cfg: Config, engine: ContentEngine):
        self.cfg = cfg
        self.engine = engine
        self.is_running = True
        self._state_file = Path(cfg.SCHEDULE_FILE)
        self._load_state()

    def _load_state(self):
        if self._state_file.exists():
            data = json.loads(self._state_file.read_text())
            self.is_running = data.get("running", True)
        else:
            self.is_running = True

    def _save_state(self):
        self._state_file.write_text(json.dumps({"running": self.is_running}))

    def pause(self):
        self.is_running = False
        self._save_state()

    def resume(self):
        self.is_running = True
        self._save_state()

    def reset(self):
        self.is_running = True
        self._save_state()

    def next_post_time(self) -> str:
        if not self.is_running:
            return "Paused ⏸"
        interval = 86400 // self.cfg.POSTS_PER_DAY
        next_ts = datetime.utcnow() + timedelta(seconds=interval)
        return next_ts.strftime("%H:%M UTC")

    def show_schedule(self) -> str:
        interval_h = 24 / self.cfg.POSTS_PER_DAY
        lines = [
            "📅 *Post Schedule*\n",
            f"Status:        {'▶️ Running' if self.is_running else '⏸ Paused'}",
            f"Posts/day:     {self.cfg.POSTS_PER_DAY}",
            f"Interval:      ~{interval_h:.1f} hours",
            f"Next post:     {self.next_post_time()}",
            "",
            "Preferred UTC hours:",
        ]
        for h in self.cfg.POST_HOURS:
            lines.append(f"  • {h:02d}:00")
        return "\n".join(lines)
