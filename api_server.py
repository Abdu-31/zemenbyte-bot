"""
api_server.py — Lightweight REST API for the ZemenByte Mini App dashboard
Runs alongside the bot on a separate thread. Railway exposes PORT automatically.
"""

import json
import os
import threading
from datetime import date, datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# Shared references injected by bot.py at startup
_analytics = None
_scheduler = None
_engine    = None
_app       = None   # telegram Application
_cfg       = None


def init(analytics, scheduler, engine, app, cfg):
    global _analytics, _scheduler, _engine, _app, _cfg
    _analytics = analytics
    _scheduler = scheduler
    _engine    = engine
    _app       = app
    _cfg       = cfg


def _cors(handler):
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type, X-Admin-Token")


def _json_response(handler, data: dict, status: int = 200):
    body = json.dumps(data).encode()
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    _cors(handler)
    handler.end_headers()
    handler.wfile.write(body)


async def _fetch_real_members():
    """Fetch live member count from Telegram API."""
    try:
        chat = await _app.bot.get_chat(f"@{_cfg.CHANNEL_USERNAME}")
        count = await _app.bot.get_chat_member_count(f"@{_cfg.CHANNEL_USERNAME}")
        _analytics.update_channel_stats(members=count)
        return count
    except Exception as e:
        return _analytics._data.get("members", 0)


class Handler(BaseHTTPRequestHandler):

    def log_message(self, *args):
        pass  # silence default access log

    def do_OPTIONS(self):
        self.send_response(204)
        _cors(self)
        self.end_headers()

    def _check_auth(self) -> bool:
        token = self.headers.get("X-Admin-Token", "")
        return token == os.getenv("DASHBOARD_SECRET", "zemenbyte2025")

    def do_GET(self):
        parsed = urlparse(self.path)
        path   = parsed.path.rstrip("/")

        # ── /api/stats ── real data ──────────────────────────────────────
        if path == "/api/stats":
            today = date.today().isoformat()
            data  = _analytics._data
            posts_today = data["daily_posts"].get(today, 0)
            posts_per_day = _cfg.POSTS_PER_DAY
            remaining = max(0, posts_per_day - posts_today)

            # last 7 days for sparkline
            last7 = []
            for i in range(6, -1, -1):
                d = (date.today() - timedelta(days=i)).isoformat()
                last7.append(data["daily_posts"].get(d, 0))

            by_topic = data.get("posts_by_topic", {})
            top_topics = sorted(by_topic.items(), key=lambda x: x[1], reverse=True)

            _json_response(self, {
                "members":      data.get("members", 0),
                "posts_today":  posts_today,
                "remaining":    remaining,
                "total_posts":  data.get("total_posts", 0),
                "views_24h":    data.get("views_24h", 0),
                "shares_24h":   data.get("shares_24h", 0),
                "last7":        last7,
                "topics":       top_topics,
                "scheduler_running": _scheduler.is_running,
                "next_post":    _scheduler.next_post_time(),
                "channel":      _cfg.CHANNEL_USERNAME,
                "posts_per_day": posts_per_day,
            })

        # ── /api/preview ─────────────────────────────────────────────────
        elif path == "/api/preview":
            topic   = _engine.pick_topic()
            preview = _engine.generate_post(topic)
            _json_response(self, {"topic": topic, "text": preview})

        # ── /api/schedule ────────────────────────────────────────────────
        elif path == "/api/schedule":
            _json_response(self, {
                "running":      _scheduler.is_running,
                "posts_per_day": _cfg.POSTS_PER_DAY,
                "post_hours":   _cfg.POST_HOURS,
                "next_post":    _scheduler.next_post_time(),
            })

        # ── /api/health ──────────────────────────────────────────────────
        elif path == "/api/health":
            _json_response(self, {"status": "ok", "ts": datetime.utcnow().isoformat()})

        else:
            _json_response(self, {"error": "Not found"}, 404)

    def do_POST(self):
        if not self._check_auth():
            _json_response(self, {"error": "Unauthorized"}, 401)
            return

        parsed = urlparse(self.path)
        path   = parsed.path.rstrip("/")
        length = int(self.headers.get("Content-Length", 0))
        body   = json.loads(self.rfile.read(length)) if length else {}

        import asyncio

        # ── /api/post ────────────────────────────────────────────────────
        if path == "/api/post":
            topic = body.get("topic") or _engine.pick_topic()
            text  = _engine.generate_post(topic)

            async def do_post():
                await _app.bot.send_message(
                    chat_id=f"@{_cfg.CHANNEL_USERNAME}",
                    text=text,
                    parse_mode="Markdown"
                )
                _analytics.record_post(topic)

            try:
                loop = asyncio.new_event_loop()
                loop.run_until_complete(do_post())
                loop.close()
                _json_response(self, {"ok": True, "topic": topic, "text": text})
            except Exception as e:
                _json_response(self, {"ok": False, "error": str(e)}, 500)

        # ── /api/poll ────────────────────────────────────────────────────
        elif path == "/api/poll":
            from growth_engine import GrowthEngine
            growth = GrowthEngine(_cfg)
            poll   = growth.create_poll()

            async def do_poll():
                await _app.bot.send_poll(
                    chat_id=f"@{_cfg.CHANNEL_USERNAME}",
                    question=poll["question"],
                    options=poll["options"],
                    is_anonymous=True
                )

            try:
                loop = asyncio.new_event_loop()
                loop.run_until_complete(do_poll())
                loop.close()
                _json_response(self, {"ok": True, "poll": poll})
            except Exception as e:
                _json_response(self, {"ok": False, "error": str(e)}, 500)

        # ── /api/engage ──────────────────────────────────────────────────
        elif path == "/api/engage":
            from growth_engine import GrowthEngine
            growth = GrowthEngine(_cfg)
            text   = growth.create_engagement_post()

            async def do_engage():
                await _app.bot.send_message(
                    chat_id=f"@{_cfg.CHANNEL_USERNAME}",
                    text=text, parse_mode="Markdown"
                )

            try:
                loop = asyncio.new_event_loop()
                loop.run_until_complete(do_engage())
                loop.close()
                _json_response(self, {"ok": True})
            except Exception as e:
                _json_response(self, {"ok": False, "error": str(e)}, 500)

        # ── /api/notify ──────────────────────────────────────────────────
        elif path == "/api/notify":
            from growth_engine import GrowthEngine
            growth = GrowthEngine(_cfg)
            text   = growth.create_push_notification()

            async def do_notify():
                await _app.bot.send_message(
                    chat_id=f"@{_cfg.CHANNEL_USERNAME}",
                    text=text, parse_mode="Markdown"
                )

            try:
                loop = asyncio.new_event_loop()
                loop.run_until_complete(do_notify())
                loop.close()
                _json_response(self, {"ok": True})
            except Exception as e:
                _json_response(self, {"ok": False, "error": str(e)}, 500)

        # ── /api/scheduler/pause & resume ────────────────────────────────
        elif path == "/api/scheduler/pause":
            _scheduler.pause()
            _json_response(self, {"ok": True, "running": False})

        elif path == "/api/scheduler/resume":
            _scheduler.resume()
            _json_response(self, {"ok": True, "running": True})

        # ── /api/refresh_members ─────────────────────────────────────────
        elif path == "/api/refresh_members":
            async def do_refresh():
                return await _fetch_real_members()
            loop = asyncio.new_event_loop()
            count = loop.run_until_complete(do_refresh())
            loop.close()
            _json_response(self, {"ok": True, "members": count})

        else:
            _json_response(self, {"error": "Not found"}, 404)


def start(analytics, scheduler, engine, app, cfg):
    """Start API server in a background thread."""
    init(analytics, scheduler, engine, app, cfg)
    port = int(os.getenv("API_PORT", os.getenv("PORT", "8080")))
    server = HTTPServer(("0.0.0.0", port), Handler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    print(f"✅ API server running on port {port}")
