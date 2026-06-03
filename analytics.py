"""
analytics.py — ZemenByte Analytics (tracks topics + languages)
"""

import json
from datetime import datetime, date, timedelta
from pathlib import Path
from config import Config

LANG_NAMES = {"en": "🇬🇧 English", "am": "🇪🇹 አማርኛ", "orm": "🟢 Afaan Oromoo"}

class AnalyticsTracker:
    def __init__(self, cfg: Config):
        self.cfg   = cfg
        self._file = Path(cfg.ANALYTICS_FILE)
        self._data = self._load()

    def _load(self) -> dict:
        if self._file.exists():
            return json.loads(self._file.read_text())
        return {
            "total_posts": 0,
            "posts_by_topic": {},
            "posts_by_lang": {"en": 0, "am": 0, "orm": 0},
            "daily_posts": {},
            "members": 0,
            "views_24h": 0,
            "shares_24h": 0,
        }

    def _save(self):
        self._file.write_text(json.dumps(self._data, indent=2))

    def record_post(self, topic: str, lang: str = "en"):
        today = date.today().isoformat()
        self._data["total_posts"] += 1
        self._data["posts_by_topic"][topic] = self._data["posts_by_topic"].get(topic, 0) + 1
        if "posts_by_lang" not in self._data:
            self._data["posts_by_lang"] = {"en": 0, "am": 0, "orm": 0}
        self._data["posts_by_lang"][lang] = self._data["posts_by_lang"].get(lang, 0) + 1
        self._data["daily_posts"][today]  = self._data["daily_posts"].get(today, 0) + 1
        self._save()

    def update_channel_stats(self, members=0, views=0, shares=0):
        if members: self._data["members"]   = members
        if views:   self._data["views_24h"] = views
        if shares:  self._data["shares_24h"]= shares
        self._save()

    def get_quick_stats(self) -> dict:
        today = date.today().isoformat()
        return {
            "members":     self._data.get("members", 0),
            "posts_today": self._data["daily_posts"].get(today, 0),
            "views_24h":   self._data.get("views_24h", 0),
            "shares_24h":  self._data.get("shares_24h", 0),
        }

    def full_report(self) -> str:
        today      = date.today().isoformat()
        posts_today= self._data["daily_posts"].get(today, 0)
        total      = self._data["total_posts"]
        by_topic   = self._data.get("posts_by_topic", {})
        by_lang    = self._data.get("posts_by_lang", {})

        top_topics = sorted(by_topic.items(), key=lambda x: x[1], reverse=True)[:4]
        topic_lines= "\n".join(f"  #{t}: {c} posts" for t, c in top_topics) or "  None yet"

        last7 = [self._data["daily_posts"].get(
            (date.today()-timedelta(days=i)).isoformat(), 0) for i in range(6,-1,-1)]
        avg7  = sum(last7)/7

        en_c  = by_lang.get("en",  0)
        am_c  = by_lang.get("am",  0)
        orm_c = by_lang.get("orm", 0)

        return (
            f"📊 *ZemenByte Analytics*\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"👥 Members:       `{self._data.get('members',0):,}`\n"
            f"👁 Views (24h):   `{self._data.get('views_24h',0):,}`\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"📬 Posts today:   `{posts_today}`\n"
            f"📬 Total posts:   `{total}`\n"
            f"📈 Avg/day (7d):  `{avg7:.1f}`\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"🌍 *By Language:*\n"
            f"  🇬🇧 English:     `{en_c}`\n"
            f"  🇪🇹 አማርኛ:       `{am_c}`\n"
            f"  🟢 Afaan Oromoo: `{orm_c}`\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"🏆 *Top Topics:*\n{topic_lines}\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"📅 _{date.today().strftime('%d %B %Y')}_"
        )

    def daily_summary(self) -> str:
        today      = date.today().isoformat()
        posts_today= self._data["daily_posts"].get(today, 0)
        by_topic   = self._data.get("posts_by_topic", {})
        by_lang    = self._data.get("posts_by_lang", {})
        top_topic  = max(by_topic, key=by_topic.get) if by_topic else "N/A"
        top_lang   = max(by_lang,  key=by_lang.get)  if by_lang  else "en"
        return (
            f"🌙 *Daily Summary — ZemenByte*\n\n"
            f"📬 Posts today:    `{posts_today}`\n"
            f"🏆 Top topic:      `#{top_topic}`\n"
            f"🌍 Top language:   {LANG_NAMES.get(top_lang, top_lang)}\n"
            f"📊 Total all-time: `{self._data['total_posts']}`\n\n"
            f"Good work today! 🚀"
        )
