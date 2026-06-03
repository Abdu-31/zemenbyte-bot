"""
api_server.py — ZemenByte REST API
Fixed: uses bot's existing event loop instead of creating a new one.
"""

import json
import os
import threading
import asyncio
from datetime import date, datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

_analytics = None
_scheduler = None
_engine    = None
_app       = None
_cfg       = None
_loop      = None   # main event loop reference


def init(analytics, scheduler, engine, app, cfg, loop):
    global _analytics, _scheduler, _engine, _app, _cfg, _loop
    _analytics = analytics
    _scheduler = scheduler
    _engine    = engine
    _app       = app
    _cfg       = cfg
    _loop      = loop


def _run(coro):
    """Submit coroutine to the bot's main event loop and wait for result."""
    future = asyncio.run_coroutine_threadsafe(coro, _loop)
    return future.result(timeout=15)


def _cors(h):
    h.send_header("Access-Control-Allow-Origin", "*")
    h.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    h.send_header("Access-Control-Allow-Headers", "Content-Type, X-Admin-Token")


def _json(handler, data, status=200):
    body = json.dumps(data).encode()
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    _cors(handler)
    handler.end_headers()
    handler.wfile.write(body)


class Handler(BaseHTTPRequestHandler):

    def log_message(self, *args): pass

    def _auth(self):
        return self.headers.get("X-Admin-Token","") == os.getenv("DASHBOARD_SECRET","zemenbyte2025")

    def do_OPTIONS(self):
        self.send_response(204)
        _cors(self)
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path.rstrip("/")

        if path == "/api/stats":
            today = date.today().isoformat()
            data  = _analytics._data
            posts_today = data["daily_posts"].get(today, 0)
            remaining   = max(0, _cfg.POSTS_PER_DAY - posts_today)

            last7 = []
            for i in range(6, -1, -1):
                d = (date.today() - timedelta(days=i)).isoformat()
                last7.append(data["daily_posts"].get(d, 0))

            by_topic = data.get("posts_by_topic", {})
            top_topics = sorted(by_topic.items(), key=lambda x: x[1], reverse=True)

            _json(self, {
                "members":          data.get("members", 0),
                "posts_today":      posts_today,
                "remaining":        remaining,
                "total_posts":      data.get("total_posts", 0),
                "views_24h":        data.get("views_24h", 0),
                "shares_24h":       data.get("shares_24h", 0),
                "last7":            last7,
                "topics":           top_topics,
                "scheduler_running":_scheduler.is_running,
                "next_post":        _scheduler.next_post_time(),
                "channel":          _cfg.CHANNEL_USERNAME,
                "posts_per_day":    _cfg.POSTS_PER_DAY,
                "post_hours":       _cfg.POST_HOURS,
            })

        elif path == "/api/preview":
            topic   = _engine.pick_topic()
            lang    = _engine.pick_language()
            preview = _engine.generate_post(topic, lang)
            _json(self, {"topic": topic, "lang": lang, "text": preview})

        elif path == "/api/health":
            _json(self, {"status": "ok", "ts": datetime.utcnow().isoformat()})

        else:
            _json(self, {"error": "Not found"}, 404)

    def do_POST(self):
        if not self._auth():
            _json(self, {"error": "Unauthorized"}, 401)
            return

        path   = urlparse(self.path).path.rstrip("/")
        length = int(self.headers.get("Content-Length", 0))
        body   = json.loads(self.rfile.read(length)) if length else {}

        # ── /api/post ────────────────────────────────────────────────────
        if path == "/api/post":
            topic = body.get("topic") or _engine.pick_topic()
            lang  = body.get("lang")  or _engine.pick_language()
            text  = _engine.generate_post(topic, lang)
            try:
                _run(_app.bot.send_message(
                    chat_id=f"@{_cfg.CHANNEL_USERNAME}",
                    text=text,
                    parse_mode="Markdown"
                ))
                _analytics.record_post(topic, lang)
                _json(self, {"ok": True, "topic": topic, "lang": lang, "text": text})
            except Exception as e:
                _json(self, {"ok": False, "error": str(e)}, 500)

        # ── /api/poll ────────────────────────────────────────────────────
        elif path == "/api/poll":
            lang = body.get("lang", "en")
            poll = _analytics  # reuse growth
            try:
                from growth_engine import GrowthEngine
                g    = GrowthEngine(_cfg)
                poll = g.create_poll(lang)
                _run(_app.bot.send_poll(
                    chat_id=f"@{_cfg.CHANNEL_USERNAME}",
                    question=poll["question"],
                    options=poll["options"],
                    is_anonymous=True
                ))
                _json(self, {"ok": True, "poll": poll})
            except Exception as e:
                _json(self, {"ok": False, "error": str(e)}, 500)

        # ── /api/engage ──────────────────────────────────────────────────
        elif path == "/api/engage":
            try:
                from growth_engine import GrowthEngine
                g    = GrowthEngine(_cfg)
                text = g.create_engagement_post()
                _run(_app.bot.send_message(
                    chat_id=f"@{_cfg.CHANNEL_USERNAME}",
                    text=text, parse_mode="Markdown"
                ))
                _json(self, {"ok": True})
            except Exception as e:
                _json(self, {"ok": False, "error": str(e)}, 500)

        # ── /api/notify ──────────────────────────────────────────────────
        elif path == "/api/notify":
            try:
                from growth_engine import GrowthEngine
                g    = GrowthEngine(_cfg)
                text = g.create_push_notification()
                _run(_app.bot.send_message(
                    chat_id=f"@{_cfg.CHANNEL_USERNAME}",
                    text=text, parse_mode="Markdown"
                ))
                _json(self, {"ok": True})
            except Exception as e:
                _json(self, {"ok": False, "error": str(e)}, 500)

        # ── /api/scheduler/pause ─────────────────────────────────────────
        elif path == "/api/scheduler/pause":
            _scheduler.pause()
            _json(self, {"ok": True, "running": False})

        # ── /api/scheduler/resume ────────────────────────────────────────
        elif path == "/api/scheduler/resume":
            _scheduler.resume()
            _json(self, {"ok": True, "running": True})

        # ── /api/refresh_members ─────────────────────────────────────────
        elif path == "/api/refresh_members":
            try:
                count = _run(_app.bot.get_chat_member_count(f"@{_cfg.CHANNEL_USERNAME}"))
                _analytics.update_channel_stats(members=count)
                _json(self, {"ok": True, "members": count})
            except Exception as e:
                _json(self, {"ok": False, "error": str(e)}, 500)

        else:
            _json(self, {"error": "Not found"}, 404)


def start(analytics, scheduler, engine, app, cfg):
    """Start API in background thread, passing the running event loop."""
    loop = asyncio.get_event_loop()
    init(analytics, scheduler, engine, app, cfg, loop)

    port   = int(os.getenv("PORT", "8080"))
    server = HTTPServer(("0.0.0.0", port), Handler)

    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    print(f"✅ API server on port {port}")
