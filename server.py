"""
server.py — Standalone Flask server for ZemenByte dashboard.
Serves dashboard HTML and proxies API calls to the bot.
Runs as a separate thread alongside the bot.
"""

import os
import asyncio
import threading
import logging
from datetime import datetime, date, timedelta
from flask import Flask, request, jsonify, make_response, Response

logger = logging.getLogger("ZemenByte.server")

# Global references — injected by bot.py
_analytics = None
_scheduler  = None  
_engine     = None
_growth     = None
_referral   = None
_cfg        = None
_tg_app     = None
_loop       = None

def init(analytics, scheduler, engine, growth, referral, app, cfg):
    global _analytics, _scheduler, _engine, _growth, _referral, _tg_app, _cfg
    _analytics = analytics
    _scheduler  = scheduler
    _engine     = engine
    _growth     = growth
    _referral   = referral
    _tg_app     = app
    _cfg        = cfg

def _run(coro):
    """Run async coroutine from sync Flask thread."""
    global _loop
    if _loop is None or not _loop.is_running():
        raise RuntimeError("Bot loop not ready")
    fut = asyncio.run_coroutine_threadsafe(coro, _loop)
    return fut.result(timeout=20)

def _auth():
    token = request.headers.get("X-Admin-Token", "")
    return token == os.getenv("DASHBOARD_SECRET", "zemenbyte2025")

# ── Flask app ─────────────────────────────────────────────────────────────
flask_app = Flask(__name__)

@flask_app.after_request
def cors(r):
    r.headers["Access-Control-Allow-Origin"]  = "*"
    r.headers["Access-Control-Allow-Headers"] = "Content-Type, X-Admin-Token"
    r.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return r

@flask_app.route("/", methods=["GET"])
def dashboard():
    """Serve dashboard HTML — same origin as API, no CORS."""
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()
        # Inject same-origin API config — no external URL needed
        html = html.replace(
            "const HARDCODED_API    = 'https://zemenbyte.up.railway.app';",
            "const HARDCODED_API    = '';"  # empty = same origin
        )
        resp = make_response(html)
        resp.headers["Content-Type"] = "text/html; charset=utf-8"
        return resp
    return jsonify({"service": "ZemenByte API", "status": "running ✅"})

@flask_app.route("/status")
def status():
    return jsonify({
        "service": "ZemenByte Bot API",
        "status":  "running ✅",
        "channel": f"@{_cfg.CHANNEL_USERNAME}" if _cfg else "loading",
        "ts":      datetime.utcnow().isoformat()
    })

@flask_app.route("/api/health")
def health():
    return jsonify({"status": "ok", "ts": datetime.utcnow().isoformat()})

@flask_app.route("/api/stats")
def stats():
    if not _analytics: return jsonify({"error": "not ready"}), 503
    today = date.today().isoformat()
    data  = _analytics._data
    posts_today = data["daily_posts"].get(today, 0)
    by_topic    = data.get("posts_by_topic", {})
    top_topics  = sorted(by_topic.items(), key=lambda x: x[1], reverse=True)
    last7 = [data["daily_posts"].get(
        (date.today()-timedelta(days=i)).isoformat(), 0) for i in range(6,-1,-1)]
    return jsonify({
        "members":           data.get("members", 0),
        "posts_today":       posts_today,
        "remaining":         max(0, _cfg.POSTS_PER_DAY - posts_today),
        "total_posts":       data.get("total_posts", 0),
        "topics":            top_topics,
        "scheduler_running": _scheduler.is_running if _scheduler else False,
        "next_post":         _scheduler.next_post_time() if _scheduler else "—",
        "channel":           _cfg.CHANNEL_USERNAME if _cfg else "",
        "posts_per_day":     _cfg.POSTS_PER_DAY if _cfg else 6,
        "post_hours":        _cfg.POST_HOURS if _cfg else [],
        "registered_users":  _referral.total_users() if _referral else 0,
        "total_referrals":   _referral.total_referrals() if _referral else 0,
        "last7":             last7,
    })

@flask_app.route("/api/preview")
def preview():
    if not _engine: return jsonify({"error": "not ready"}), 503
    topic = _engine.pick_topic()
    lang  = _engine.pick_language()
    text  = _engine.generate_post(topic, lang)
    return jsonify({"topic": topic, "lang": lang, "text": text})

@flask_app.route("/api/post", methods=["POST", "OPTIONS"])
def post_to_channel():
    if request.method == "OPTIONS": return jsonify({}), 200
    if not _auth(): return jsonify({"error": "Unauthorized"}), 401
    body  = request.get_json(silent=True) or {}
    topic = body.get("topic") or _engine.pick_topic()
    lang  = body.get("lang")  or _engine.pick_language()
    text  = _engine.generate_post(topic, lang)
    try:
        _run(_tg_app.bot.send_message(
            chat_id=f"@{_cfg.CHANNEL_USERNAME}",
            text=text, parse_mode="Markdown"
        ))
        _analytics.record_post(topic, lang)
        return jsonify({"ok": True, "topic": topic, "lang": lang, "text": text})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@flask_app.route("/api/poll", methods=["POST", "OPTIONS"])
def send_poll():
    if request.method == "OPTIONS": return jsonify({}), 200
    if not _auth(): return jsonify({"error": "Unauthorized"}), 401
    body = request.get_json(silent=True) or {}
    lang = body.get("lang", "en")
    poll = _growth.create_poll(lang)
    try:
        _run(_tg_app.bot.send_poll(
            chat_id=f"@{_cfg.CHANNEL_USERNAME}",
            question=poll["question"], options=poll["options"], is_anonymous=True
        ))
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@flask_app.route("/api/engage", methods=["POST", "OPTIONS"])
def send_engage():
    if request.method == "OPTIONS": return jsonify({}), 200
    if not _auth(): return jsonify({"error": "Unauthorized"}), 401
    try:
        text = _growth.create_engagement_post()
        _run(_tg_app.bot.send_message(
            chat_id=f"@{_cfg.CHANNEL_USERNAME}",
            text=text, parse_mode="Markdown"
        ))
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@flask_app.route("/api/notify", methods=["POST", "OPTIONS"])
def send_notify():
    if request.method == "OPTIONS": return jsonify({}), 200
    if not _auth(): return jsonify({"error": "Unauthorized"}), 401
    try:
        text = _growth.create_push_notification()
        _run(_tg_app.bot.send_message(
            chat_id=f"@{_cfg.CHANNEL_USERNAME}",
            text=text, parse_mode="Markdown"
        ))
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@flask_app.route("/api/scheduler/pause", methods=["POST", "OPTIONS"])
def pause_sched():
    if request.method == "OPTIONS": return jsonify({}), 200
    if not _auth(): return jsonify({"error": "Unauthorized"}), 401
    _scheduler.pause()
    return jsonify({"ok": True, "running": False})

@flask_app.route("/api/scheduler/resume", methods=["POST", "OPTIONS"])
def resume_sched():
    if request.method == "OPTIONS": return jsonify({}), 200
    if not _auth(): return jsonify({"error": "Unauthorized"}), 401
    _scheduler.resume()
    return jsonify({"ok": True, "running": True})

@flask_app.route("/api/refresh_members", methods=["POST", "OPTIONS"])
def refresh_members():
    if request.method == "OPTIONS": return jsonify({}), 200
    if not _auth(): return jsonify({"error": "Unauthorized"}), 401
    try:
        count = _run(_tg_app.bot.get_chat_member_count(f"@{_cfg.CHANNEL_USERNAME}"))
        _analytics.update_channel_stats(members=count)
        return jsonify({"ok": True, "members": count})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@flask_app.route("/api/broadcast", methods=["POST", "OPTIONS"])
def broadcast():
    if request.method == "OPTIONS": return jsonify({}), 200
    if not _auth(): return jsonify({"error": "Unauthorized"}), 401
    body = request.get_json(silent=True) or {}
    text = body.get("text", "").strip()
    post_to_channel = body.get("post_to_channel", False)
    if not text: return jsonify({"error": "text required"}), 400

    async def do_broadcast():
        sent = 0
        # 1. Post to channel if requested
        if post_to_channel:
            try:
                await _tg_app.bot.send_message(
                    chat_id=f"@{_cfg.CHANNEL_USERNAME}",
                    text=text, parse_mode="Markdown")
            except Exception as e:
                pass
        # 2. DM all registered bot users
        users = list(_referral._data["users"].values())
        for u in users:
            try:
                await _tg_app.bot.send_message(
                    chat_id=u["user_id"], text=text, parse_mode="Markdown")
                sent += 1
                await asyncio.sleep(0.05)
            except Exception: pass
        return sent

    try:
        sent = _run(do_broadcast())
        return jsonify({"ok": True, "sent": sent, "channel": post_to_channel})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@flask_app.route("/api/broadcast_newpost", methods=["POST", "OPTIONS"])
def broadcast_newpost():
    if request.method == "OPTIONS": return jsonify({}), 200
    if not _auth(): return jsonify({"error": "Unauthorized"}), 401
    topic = _engine.pick_topic()
    lang  = _engine.pick_language()
    text  = _engine.generate_post(topic, lang)

    async def do_all():
        await _tg_app.bot.send_message(
            chat_id=f"@{_cfg.CHANNEL_USERNAME}",
            text=text, parse_mode="Markdown")
        _analytics.record_post(topic, lang)
        users = list(_referral._data["users"].values())
        sent  = 0
        notif = f"🔔 *New post on @{_cfg.CHANNEL_USERNAME}!*\n\nTopic: #{topic}\n👉 t.me/{_cfg.CHANNEL_USERNAME}"
        for u in users:
            try:
                await _tg_app.bot.send_message(
                    chat_id=u["user_id"], text=notif, parse_mode="Markdown")
                sent += 1
                await asyncio.sleep(0.05)
            except Exception: pass
        return sent

    try:
        sent = _run(do_all())
        return jsonify({"ok": True, "topic": topic, "sent": sent})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@flask_app.route("/api/channel_reminder", methods=["POST", "OPTIONS"])
def channel_reminder():
    if request.method == "OPTIONS": return jsonify({}), 200
    if not _auth(): return jsonify({"error": "Unauthorized"}), 401
    msg = (
        f"📡 *ZemenByte — Daily Tech Channel*\n\n"
        f"🇬🇧 Stay updated on AI, Crypto, Cybersecurity & more!\n"
        f"🇪🇹 ዕለታዊ የቴክ ዜናዎች!\n"
        f"🟢 Oduu teknooloojii guyyuu!\n\n"
        f"📲 Start our bot for personal notifications:\n"
        f"👉 t.me/ZemenByteBot\n\n"
        f"📡 Channel: t.me/{_cfg.CHANNEL_USERNAME}"
    )
    async def do():
        # Post to channel
        await _tg_app.bot.send_message(
            chat_id=f"@{_cfg.CHANNEL_USERNAME}",
            text=msg, parse_mode="Markdown")
        # DM bot users
        users = list(_referral._data["users"].values())
        sent = 0
        for u in users:
            try:
                await _tg_app.bot.send_message(
                    chat_id=u["user_id"], text=msg, parse_mode="Markdown")
                sent += 1
                await asyncio.sleep(0.05)
            except Exception: pass
        return sent
    try:
        sent = _run(do())
        return jsonify({"ok": True, "sent": sent})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@flask_app.route("/api/referral_promo", methods=["POST", "OPTIONS"])
def referral_promo():
    if request.method == "OPTIONS": return jsonify({}), 200
    if not _auth(): return jsonify({"error": "Unauthorized"}), 401
    msg = (
        "🔗 *ZemenByte Referral Program* 🎁\n\n"
        "Invite friends & earn points + badges!\n\n"
        "🏅 Badges:\n"
        "🌱 1 invite → Starter\n"
        "⭐ 5 invites → Rising Star\n"
        "🔥 10 invites → Influencer\n"
        "💎 25 invites → Diamond\n"
        "👑 50 invites → ZemenByte Legend\n\n"
        "🇬🇧 Start @ZemenByteBot → send /referral\n"
        "🇪🇹 @ZemenByteBot ጀምር → /referral ላክ\n"
        "🟢 @ZemenByteBot jalqabi → /referral ergi\n\n"
        "🏆 Leaderboard → /leaderboard"
    )
    async def do():
        # Post to channel
        await _tg_app.bot.send_message(
            chat_id=f"@{_cfg.CHANNEL_USERNAME}",
            text=msg, parse_mode="Markdown")
        # DM bot users
        users = list(_referral._data["users"].values())
        sent = 0
        for u in users:
            try:
                await _tg_app.bot.send_message(
                    chat_id=u["user_id"], text=msg, parse_mode="Markdown")
                sent += 1
                await asyncio.sleep(0.05)
            except Exception: pass
        return sent
    try:
        sent = _run(do())
        return jsonify({"ok": True, "sent": sent})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@flask_app.route("/api/channel_reminder", methods=["POST","OPTIONS"])
def channel_reminder():
    if request.method == "OPTIONS": return jsonify({}), 200
    if not _auth(): return jsonify({"error":"Unauthorized"}), 401
    msg = f"📡 *ZemenByte — Daily Tech*\n\n🇬🇧 AI, Crypto, Cyber updates daily!\n🇪🇹 ዕለታዊ የቴክ ዜናዎች!\n🟢 Oduu teknooloojii guyyuu!\n\n📲 t.me/ZemenByteBot\n📡 t.me/{_cfg.CHANNEL_USERNAME}"
    async def do():
        await _tg_app.bot.send_message(chat_id=f"@{_cfg.CHANNEL_USERNAME}", text=msg, parse_mode="Markdown")
        users = list(_referral._data["users"].values())
        sent = 0
        for u in users:
            try:
                await _tg_app.bot.send_message(chat_id=u["user_id"], text=msg, parse_mode="Markdown")
                sent += 1
                await asyncio.sleep(0.05)
            except Exception: pass
        return sent
    try:
        sent = _run(do())
        return jsonify({"ok": True, "sent": sent})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@flask_app.route("/api/referral_promo", methods=["POST","OPTIONS"])
def referral_promo():
    if request.method == "OPTIONS": return jsonify({}), 200
    if not _auth(): return jsonify({"error":"Unauthorized"}), 401
    msg = "🔗 *ZemenByte Referral Program* 🎁\n\nInvite friends & earn badges!\n🌱1→⭐5→🔥10→💎25→👑50\n\n👉 Start @ZemenByteBot → /referral\n🏆 /leaderboard"
    async def do():
        await _tg_app.bot.send_message(chat_id=f"@{_cfg.CHANNEL_USERNAME}", text=msg, parse_mode="Markdown")
        users = list(_referral._data["users"].values())
        sent = 0
        for u in users:
            try:
                await _tg_app.bot.send_message(chat_id=u["user_id"], text=msg, parse_mode="Markdown")
                sent += 1
                await asyncio.sleep(0.05)
            except Exception: pass
        return sent
    try:
        sent = _run(do())
        return jsonify({"ok": True, "sent": sent})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500
@flask_app.route("/api/leaderboard")
def leaderboard():
    if not _referral: return jsonify([])
    lb = _referral.get_leaderboard(10)
    return jsonify({"ok": True, "leaderboard": [
        {"name":    u.get("username") or u.get("first_name", "User"),
         "invites": len(u["referrals"]),
         "points":  u["points"],
         "badges":  u.get("badges", [])}
        for u in lb
    ]})


def start(analytics, scheduler, engine, growth, referral, app, cfg, loop):
    """Start Flask in a background daemon thread."""
    global _loop
    _loop = loop
    init(analytics, scheduler, engine, growth, referral, app, cfg)
    port = int(os.getenv("PORT", "8080"))
    t = threading.Thread(
        target=lambda: flask_app.run(
            host="0.0.0.0", port=port, debug=False, use_reloader=False),
        daemon=True
    )
    t.start()
    logger.info(f"✅ Dashboard server on port {port}")
