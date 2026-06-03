#!/usr/bin/env python3
"""
ZemenByte Telegram Bot — Final Production Version
==================================================
• Trilingual auto-posting (EN / አማርኛ / Afaan Oromoo)
• Referral system with points & badges
• Subscriber notifications (broadcast to all users)
• Single-port Flask API + Bot on same process
• Dashboard integration
"""

import asyncio
import logging
import os
import json
import threading
from datetime import datetime, time as dtime
from flask import Flask, request, jsonify

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, JobQueue
)
from telegram.constants import ParseMode

from content_engine import ContentEngine
from scheduler import PostScheduler
from analytics import AnalyticsTracker
from growth_engine import GrowthEngine
from referral import ReferralSystem
from config import Config

# ── Logging ───────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    level=logging.INFO,
    handlers=[logging.FileHandler("zemenbyte.log"), logging.StreamHandler()]
)
logger = logging.getLogger("ZemenByte")

# ── Init ──────────────────────────────────────────────────────────────────
cfg       = Config()
engine    = ContentEngine(cfg)
scheduler = PostScheduler(cfg, engine)
analytics = AnalyticsTracker(cfg)
growth    = GrowthEngine(cfg)
referral  = ReferralSystem(
    bot_username=os.getenv("BOT_USERNAME", "ZemenByteBot"),
    channel_username=cfg.CHANNEL_USERNAME
)

LANG_NAMES = {"en": "🇬🇧 English", "am": "🇪🇹 አማርኛ", "orm": "🟢 Afaan Oromoo"}

# Global app reference (set in main)
_tg_app   = None
_tg_loop  = None

# ════════════════════════════════════════════════════════════════════════════
#  FLASK API (runs on Railway's PORT, serves dashboard)
# ════════════════════════════════════════════════════════════════════════════

flask_app = Flask(__name__)

def _run_coro(coro):
    """Run a coroutine from Flask (sync) thread safely."""
    if _tg_loop is None:
        raise RuntimeError("Bot loop not ready")
    future = asyncio.run_coroutine_threadsafe(coro, _tg_loop)
    return future.result(timeout=20)

def _check_auth():
    token = request.headers.get("X-Admin-Token","")
    return token == os.getenv("DASHBOARD_SECRET", "zemenbyte2025")

@flask_app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"]  = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, X-Admin-Token"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response

@flask_app.route("/")
def root():
    return jsonify({
        "service":  "ZemenByte Bot API",
        "status":   "running ✅",
        "channel":  f"@{cfg.CHANNEL_USERNAME}",
        "users":    referral.total_users(),
        "ts":       datetime.utcnow().isoformat()
    })

@flask_app.route("/api/health")
def health():
    return jsonify({"status": "ok", "ts": datetime.utcnow().isoformat()})

@flask_app.route("/api/stats")
def stats():
    from datetime import date, timedelta
    today = date.today().isoformat()
    data  = analytics._data
    posts_today = data["daily_posts"].get(today, 0)
    by_topic    = data.get("posts_by_topic", {})
    top_topics  = sorted(by_topic.items(), key=lambda x: x[1], reverse=True)
    last7 = [data["daily_posts"].get(
        (date.today()-__import__('datetime').timedelta(days=i)).isoformat(),0)
        for i in range(6,-1,-1)]
    return jsonify({
        "members":           data.get("members", 0),
        "posts_today":       posts_today,
        "remaining":         max(0, cfg.POSTS_PER_DAY - posts_today),
        "total_posts":       data.get("total_posts", 0),
        "views_24h":         data.get("views_24h", 0),
        "topics":            top_topics,
        "scheduler_running": scheduler.is_running,
        "next_post":         scheduler.next_post_time(),
        "channel":           cfg.CHANNEL_USERNAME,
        "posts_per_day":     cfg.POSTS_PER_DAY,
        "post_hours":        cfg.POST_HOURS,
        "registered_users":  referral.total_users(),
        "total_referrals":   referral.total_referrals(),
        "last7":             last7,
    })

@flask_app.route("/api/preview")
def preview():
    topic   = engine.pick_topic()
    lang    = engine.pick_language()
    text    = engine.generate_post(topic, lang)
    return jsonify({"topic": topic, "lang": lang, "text": text})

@flask_app.route("/api/post", methods=["POST", "OPTIONS"])
def post_to_channel():
    if request.method == "OPTIONS": return jsonify({}), 200
    if not _check_auth(): return jsonify({"error":"Unauthorized"}), 401
    body  = request.get_json(silent=True) or {}
    topic = body.get("topic") or engine.pick_topic()
    lang  = body.get("lang")  or engine.pick_language()
    text  = engine.generate_post(topic, lang)
    try:
        _run_coro(_tg_app.bot.send_message(
            chat_id=f"@{cfg.CHANNEL_USERNAME}",
            text=text, parse_mode="Markdown"
        ))
        analytics.record_post(topic, lang)
        return jsonify({"ok": True, "topic": topic, "lang": lang, "text": text})
    except Exception as e:
        logger.error(f"Post failed: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500

@flask_app.route("/api/poll", methods=["POST", "OPTIONS"])
def send_poll():
    if request.method == "OPTIONS": return jsonify({}), 200
    if not _check_auth(): return jsonify({"error":"Unauthorized"}), 401
    body = request.get_json(silent=True) or {}
    lang = body.get("lang", "en")
    poll = growth.create_poll(lang)
    try:
        _run_coro(_tg_app.bot.send_poll(
            chat_id=f"@{cfg.CHANNEL_USERNAME}",
            question=poll["question"], options=poll["options"], is_anonymous=True
        ))
        return jsonify({"ok": True, "poll": poll})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@flask_app.route("/api/engage", methods=["POST", "OPTIONS"])
def send_engage():
    if request.method == "OPTIONS": return jsonify({}), 200
    if not _check_auth(): return jsonify({"error":"Unauthorized"}), 401
    try:
        text = growth.create_engagement_post()
        _run_coro(_tg_app.bot.send_message(
            chat_id=f"@{cfg.CHANNEL_USERNAME}",
            text=text, parse_mode="Markdown"
        ))
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@flask_app.route("/api/notify", methods=["POST", "OPTIONS"])
def send_notify():
    if request.method == "OPTIONS": return jsonify({}), 200
    if not _check_auth(): return jsonify({"error":"Unauthorized"}), 401
    try:
        text = growth.create_push_notification()
        _run_coro(_tg_app.bot.send_message(
            chat_id=f"@{cfg.CHANNEL_USERNAME}",
            text=text, parse_mode="Markdown"
        ))
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@flask_app.route("/api/scheduler/pause", methods=["POST", "OPTIONS"])
def pause_sched():
    if request.method == "OPTIONS": return jsonify({}), 200
    if not _check_auth(): return jsonify({"error":"Unauthorized"}), 401
    scheduler.pause()
    return jsonify({"ok": True, "running": False})

@flask_app.route("/api/scheduler/resume", methods=["POST", "OPTIONS"])
def resume_sched():
    if request.method == "OPTIONS": return jsonify({}), 200
    if not _check_auth(): return jsonify({"error":"Unauthorized"}), 401
    scheduler.resume()
    return jsonify({"ok": True, "running": True})

@flask_app.route("/api/refresh_members", methods=["POST", "OPTIONS"])
def refresh_members_api():
    if request.method == "OPTIONS": return jsonify({}), 200
    if not _check_auth(): return jsonify({"error":"Unauthorized"}), 401
    try:
        count = _run_coro(_tg_app.bot.get_chat_member_count(f"@{cfg.CHANNEL_USERNAME}"))
        analytics.update_channel_stats(members=count)
        return jsonify({"ok": True, "members": count})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@flask_app.route("/api/broadcast", methods=["POST", "OPTIONS"])
def broadcast_api():
    """Broadcast a custom message to ALL registered subscribers."""
    if request.method == "OPTIONS": return jsonify({}), 200
    if not _check_auth(): return jsonify({"error":"Unauthorized"}), 401
    body = request.get_json(silent=True) or {}
    text = body.get("text", "").strip()
    if not text:
        return jsonify({"error": "text is required"}), 400

    async def do_broadcast():
        users  = list(referral._data["users"].values())
        sent   = 0
        failed = 0
        for u in users:
            try:
                await _tg_app.bot.send_message(
                    chat_id=u["user_id"],
                    text=text, parse_mode="Markdown"
                )
                sent += 1
                await asyncio.sleep(0.05)  # rate limit
            except Exception:
                failed += 1
        return sent, failed

    try:
        sent, failed = _run_coro(do_broadcast())
        return jsonify({"ok": True, "sent": sent, "failed": failed})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@flask_app.route("/api/leaderboard")
def leaderboard_api():
    lb = referral.get_leaderboard(10)
    return jsonify({"ok": True, "leaderboard": [
        {"name": u.get("username") or u.get("first_name","User"),
         "invites": len(u["referrals"]),
         "points":  u["points"],
         "badges":  u.get("badges",[])}
        for u in lb
    ]})

def start_flask():
    port = int(os.getenv("PORT", "8080"))
    logger.info(f"🌐 Flask API on port {port}")
    flask_app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)


# ════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ════════════════════════════════════════════════════════════════════════════

def is_admin(uid): return uid in cfg.ADMIN_IDS

async def refresh_members(app):
    try:
        count = await app.bot.get_chat_member_count(f"@{cfg.CHANNEL_USERNAME}")
        analytics.update_channel_stats(members=count)
    except Exception as e:
        logger.warning(f"Members: {e}")


# ════════════════════════════════════════════════════════════════════════════
#  PUBLIC BOT COMMANDS
# ════════════════════════════════════════════════════════════════════════════

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = ctx.args
    referred_by = None
    referrer    = None

    if args:
        ref_id = referral.resolve_code(args[0])
        if ref_id and ref_id != user.id:
            referred_by = ref_id
            referrer    = referral.get_user(ref_id)

    u = referral.register_user(
        user_id=user.id, username=user.username,
        first_name=user.first_name, referred_by=referred_by
    )

    if is_admin(user.id):
        await refresh_members(ctx.application)
        stats = analytics.get_quick_stats()
        keyboard = [
            [InlineKeyboardButton("📊 Dashboard",      callback_data="dashboard"),
             InlineKeyboardButton("📝 Post Now",       callback_data="post_now")],
            [InlineKeyboardButton("🌍 Post Language",  callback_data="post_lang"),
             InlineKeyboardButton("🌱 Growth Tools",   callback_data="growth")],
            [InlineKeyboardButton("📢 Notify All",     callback_data="notify_all"),
             InlineKeyboardButton("📈 Analytics",      callback_data="analytics")],
            [InlineKeyboardButton("🏆 Referral Stats", callback_data="admin_referral"),
             InlineKeyboardButton("⚙️ Schedule",       callback_data="schedule")],
        ]
        await update.message.reply_text(
            f"🤖 *ZemenByte Admin Panel*\n\n"
            f"👥 Members: `{stats['members']:,}`\n"
            f"📬 Posts Today: `{stats['posts_today']}`\n"
            f"👤 Subscribers: `{referral.total_users():,}`\n"
            f"🔗 Referrals: `{referral.total_referrals():,}`\n"
            f"🟢 Scheduler: {'Running' if scheduler.is_running else 'Stopped'}\n"
            f"🕐 Next: {scheduler.next_post_time()}",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    # Referred user
    if referrer:
        await update.message.reply_text(
            referral.welcome_referred_user(u, referrer),
            parse_mode=ParseMode.MARKDOWN
        )
        try:
            count = referral.get_ref_count(referrer["user_id"])
            pts   = referral.get_points(referrer["user_id"])
            await ctx.bot.send_message(
                chat_id=referrer["user_id"],
                text=f"🎉 *New Referral!*\n\nSomeone joined via your link!\n"
                     f"👥 Total: `{count}` | ⭐ Points: `{pts}`",
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception: pass
    else:
        name = user.first_name or "friend"
        await update.message.reply_text(
            f"👋 *Welcome to ZemenByte, {name}!*\n\n"
            f"📡 Daily insights on:\n"
            f"🤖 AI • ₿ Crypto • 🔐 Cybersecurity\n"
            f"⚛️ Quantum • 💡 Innovation • 💻 Tech\n\n"
            f"🇬🇧 English • 🇪🇹 አማርኛ • 🟢 Afaan Oromoo\n\n"
            f"📎 /referral — Your unique invite link\n"
            f"🏆 /leaderboard — Top inviters\n"
            f"📊 /mystats — Your stats",
            parse_mode=ParseMode.MARKDOWN
        )


async def cmd_referral(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    referral.register_user(user_id=user.id, username=user.username, first_name=user.first_name)
    card = referral.referral_card(user.id)
    link = referral.get_ref_link(user.id)
    keyboard = [[
        InlineKeyboardButton("📤 Share Link",   switch_inline_query=link),
        InlineKeyboardButton("🏆 Leaderboard",  callback_data="leaderboard"),
    ]]
    await update.message.reply_text(card,
        reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)


async def cmd_leaderboard(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    referral.register_user(user_id=user.id, username=user.username, first_name=user.first_name)
    keyboard = [[InlineKeyboardButton("🔗 My Link", callback_data="my_referral")]]
    await update.message.reply_text(referral.leaderboard_text(),
        reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)


async def cmd_mystats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    referral.register_user(user_id=user.id, username=user.username, first_name=user.first_name)
    card = referral.referral_card(user.id)
    keyboard = [[
        InlineKeyboardButton("📤 Share", switch_inline_query=referral.get_ref_link(user.id)),
        InlineKeyboardButton("🏆 Top",   callback_data="leaderboard"),
    ]]
    await update.message.reply_text(card,
        reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)


# ════════════════════════════════════════════════════════════════════════════
#  ADMIN COMMANDS
# ════════════════════════════════════════════════════════════════════════════

async def cmd_post(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    keyboard = [[InlineKeyboardButton(f"#{t}", callback_data=f"post_topic_{t}")] for t in cfg.TOPICS]
    keyboard.append([InlineKeyboardButton("🎲 Auto", callback_data="post_topic_AUTO")])
    await update.message.reply_text("📝 *Choose topic:*",
        reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)


async def cmd_notify_all(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Admin: /notify <message> — broadcast to all subscribers."""
    if not is_admin(update.effective_user.id): return
    text = " ".join(ctx.args) if ctx.args else ""
    if not text:
        await update.message.reply_text(
            "📢 Usage:\n`/notify Your message here`\n\n"
            "Or use the *Notify All* button in /start for a menu.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    await _do_broadcast(ctx, update.message, text)


async def _do_broadcast(ctx, reply_to, text: str):
    users = list(referral._data["users"].values())
    await reply_to.reply_text(f"📡 Broadcasting to {len(users)} subscribers...")
    sent = failed = 0
    for u in users:
        try:
            await ctx.bot.send_message(
                chat_id=u["user_id"], text=text, parse_mode=ParseMode.MARKDOWN
            )
            sent += 1
            await asyncio.sleep(0.05)
        except Exception:
            failed += 1
    await reply_to.reply_text(
        f"✅ *Broadcast Complete*\n\n"
        f"📨 Sent:   `{sent}`\n"
        f"❌ Failed: `{failed}`\n"
        f"👥 Total:  `{len(users)}`",
        parse_mode=ParseMode.MARKDOWN
    )


async def cmd_stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    await refresh_members(ctx.application)
    await update.message.reply_text(analytics.full_report(), parse_mode=ParseMode.MARKDOWN)


async def cmd_schedule(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    keyboard = [
        [InlineKeyboardButton("▶️ Start", callback_data="sched_start"),
         InlineKeyboardButton("⏸ Pause", callback_data="sched_pause")],
        [InlineKeyboardButton("🔄 Reset", callback_data="sched_reset")],
    ]
    await update.message.reply_text(scheduler.show_schedule(),
        reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)


async def cmd_growth(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    keyboard = [
        [InlineKeyboardButton("📣 Poll EN",       callback_data="growth_poll_en"),
         InlineKeyboardButton("📣 Poll አማርኛ",    callback_data="growth_poll_am")],
        [InlineKeyboardButton("📣 Poll Oromoo",   callback_data="growth_poll_orm"),
         InlineKeyboardButton("🌍 Trilingual",    callback_data="growth_trilingual")],
        [InlineKeyboardButton("💬 Engage",        callback_data="growth_engage"),
         InlineKeyboardButton("🎁 Giveaway",      callback_data="growth_giveaway")],
        [InlineKeyboardButton("📢 Notify All",    callback_data="notify_all")],
    ]
    await update.message.reply_text("🌱 *Growth Engine:*",
        reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)


async def cmd_preview(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    topic   = engine.pick_topic()
    lang    = engine.pick_language()
    preview = engine.generate_post(topic, lang)
    await update.message.reply_text(
        f"👁 *Preview — #{topic} {LANG_NAMES[lang]}:*\n\n{preview}",
        parse_mode=ParseMode.MARKDOWN
    )


# ════════════════════════════════════════════════════════════════════════════
#  CALLBACKS
# ════════════════════════════════════════════════════════════════════════════

async def callback_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data  = query.data

    # ── Public ──
    if data == "leaderboard":
        await query.edit_message_text(referral.leaderboard_text(), parse_mode=ParseMode.MARKDOWN)
        return

    if data == "my_referral":
        uid = query.from_user.id
        referral.register_user(uid, query.from_user.username, query.from_user.first_name)
        await query.edit_message_text(referral.referral_card(uid), parse_mode=ParseMode.MARKDOWN)
        return

    # ── Admin only ──
    if not is_admin(query.from_user.id):
        await query.answer("⛔ Admin only", show_alert=True)
        return

    if data == "dashboard":
        await refresh_members(ctx.application)
        await query.edit_message_text(analytics.full_report(), parse_mode=ParseMode.MARKDOWN)

    elif data == "analytics":
        await refresh_members(ctx.application)
        await query.edit_message_text(analytics.full_report(), parse_mode=ParseMode.MARKDOWN)

    elif data == "admin_referral":
        extra = (f"\n\n📊 *Referral Stats*\n"
                 f"👤 Subscribers: `{referral.total_users():,}`\n"
                 f"🔗 Referrals: `{referral.total_referrals():,}`")
        await query.edit_message_text(
            referral.leaderboard_text() + extra, parse_mode=ParseMode.MARKDOWN)

    elif data == "notify_all":
        keyboard = [
            [InlineKeyboardButton("📰 New Post Alert",   callback_data="broadcast_newpost"),
             InlineKeyboardButton("🏆 Referral Promo",   callback_data="broadcast_referral")],
            [InlineKeyboardButton("🔔 Channel Reminder", callback_data="broadcast_reminder"),
             InlineKeyboardButton("✍️ Custom Message",   callback_data="broadcast_custom")],
        ]
        await query.edit_message_text(
            "📢 *Notify All Subscribers*\n\nChoose message type:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )

    elif data == "broadcast_newpost":
        topic = engine.pick_topic()
        lang  = engine.pick_language()
        text  = engine.generate_post(topic, lang)
        # Post to channel
        await ctx.bot.send_message(chat_id=f"@{cfg.CHANNEL_USERNAME}",
            text=text, parse_mode=ParseMode.MARKDOWN)
        analytics.record_post(topic, lang)
        # Notify subscribers
        users = list(referral._data["users"].values())
        notif = (
            f"🔔 *New Post on @{cfg.CHANNEL_USERNAME}!*\n\n"
            f"Topic: #{topic}\n\n"
            f"👉 Read it: t.me/{cfg.CHANNEL_USERNAME}"
        )
        sent = 0
        for u in users:
            try:
                await ctx.bot.send_message(chat_id=u["user_id"],
                    text=notif, parse_mode=ParseMode.MARKDOWN)
                sent += 1
                await asyncio.sleep(0.05)
            except Exception: pass
        await query.edit_message_text(
            f"✅ Posted + notified {sent} subscribers!", parse_mode=ParseMode.MARKDOWN)

    elif data == "broadcast_referral":
        msg = (
            "🔗 *ZemenByte Referral Program* 🎁\n\n"
            "Invite friends & earn points!\n\n"
            "🇬🇧 Get your link → /referral\n"
            "🇪🇹 ሊንክህን ውሰድ → /referral\n"
            "🟢 Hidhata kee fudhachuuf → /referral\n\n"
            "🏆 Top inviters win prizes!\n"
            "👉 /leaderboard"
        )
        users = list(referral._data["users"].values())
        sent  = 0
        for u in users:
            try:
                await ctx.bot.send_message(chat_id=u["user_id"],
                    text=msg, parse_mode=ParseMode.MARKDOWN)
                sent += 1
                await asyncio.sleep(0.05)
            except Exception: pass
        await query.edit_message_text(
            f"✅ Referral promo sent to {sent} users!", parse_mode=ParseMode.MARKDOWN)

    elif data == "broadcast_reminder":
        msg = (
            f"📡 *Hey! Don't miss today's posts on @{cfg.CHANNEL_USERNAME}*\n\n"
            f"🇬🇧 Daily AI, Crypto, Cyber & Tech updates!\n"
            f"🇪🇹 ዕለታዊ የቴክ ዜናዎች!\n"
            f"🟢 Oduu teknooloojii guyyuu!\n\n"
            f"👉 t.me/{cfg.CHANNEL_USERNAME}"
        )
        users = list(referral._data["users"].values())
        sent  = 0
        for u in users:
            try:
                await ctx.bot.send_message(chat_id=u["user_id"],
                    text=msg, parse_mode=ParseMode.MARKDOWN)
                sent += 1
                await asyncio.sleep(0.05)
            except Exception: pass
        await query.edit_message_text(
            f"✅ Reminder sent to {sent} users!", parse_mode=ParseMode.MARKDOWN)

    elif data == "broadcast_custom":
        await query.edit_message_text(
            "✍️ *Send a custom broadcast:*\n\n"
            "Use the command:\n`/notify Your message here`\n\n"
            "Supports Markdown formatting.",
            parse_mode=ParseMode.MARKDOWN
        )

    elif data == "post_now":
        keyboard = [[InlineKeyboardButton(f"#{t}", callback_data=f"post_topic_{t}")] for t in cfg.TOPICS]
        keyboard.append([InlineKeyboardButton("🎲 Auto", callback_data="post_topic_AUTO")])
        await query.edit_message_text("📝 *Choose topic:*",
            reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)

    elif data == "post_lang":
        keyboard = [
            [InlineKeyboardButton("🇬🇧 English",     callback_data="lang_en"),
             InlineKeyboardButton("🇪🇹 አማርኛ",       callback_data="lang_am")],
            [InlineKeyboardButton("🟢 Afaan Oromoo", callback_data="lang_orm")],
        ]
        await query.edit_message_text("🌍 *Choose language:*",
            reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)

    elif data.startswith("lang_"):
        lang     = data.replace("lang_", "")
        keyboard = [[InlineKeyboardButton(f"#{t}", callback_data=f"postlang_{lang}_{t}")] for t in cfg.TOPICS]
        keyboard.append([InlineKeyboardButton("🎲 Auto", callback_data=f"postlang_{lang}_AUTO")])
        await query.edit_message_text(f"📝 *{LANG_NAMES[lang]} — Topic:*",
            reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)

    elif data.startswith("postlang_"):
        parts = data.split("_", 2)
        lang  = parts[1]
        topic = parts[2]
        if topic == "AUTO": topic = engine.pick_topic()
        text = engine.generate_post(topic, lang)
        await ctx.bot.send_message(chat_id=f"@{cfg.CHANNEL_USERNAME}",
            text=text, parse_mode=ParseMode.MARKDOWN)
        analytics.record_post(topic, lang)
        await query.edit_message_text(
            f"✅ Posted! #{topic} | {LANG_NAMES[lang]}", parse_mode=ParseMode.MARKDOWN)

    elif data.startswith("post_topic_"):
        topic = data.replace("post_topic_", "")
        if topic == "AUTO": topic = engine.pick_topic()
        lang  = engine.pick_language()
        text  = engine.generate_post(topic, lang)
        await ctx.bot.send_message(chat_id=f"@{cfg.CHANNEL_USERNAME}",
            text=text, parse_mode=ParseMode.MARKDOWN)
        analytics.record_post(topic, lang)
        await query.edit_message_text(
            f"✅ Posted! #{topic} | {LANG_NAMES[lang]}", parse_mode=ParseMode.MARKDOWN)

    elif data == "schedule":
        await query.edit_message_text(scheduler.show_schedule(), parse_mode=ParseMode.MARKDOWN)
    elif data == "sched_start":
        scheduler.resume()
        await query.edit_message_text("▶️ Scheduler *started*.", parse_mode=ParseMode.MARKDOWN)
    elif data == "sched_pause":
        scheduler.pause()
        await query.edit_message_text("⏸ Scheduler *paused*.", parse_mode=ParseMode.MARKDOWN)
    elif data == "sched_reset":
        scheduler.reset()
        await query.edit_message_text("🔄 Scheduler *reset*.", parse_mode=ParseMode.MARKDOWN)

    elif data == "growth":
        keyboard = [
            [InlineKeyboardButton("📣 Poll EN",      callback_data="growth_poll_en"),
             InlineKeyboardButton("📣 Poll አማርኛ",   callback_data="growth_poll_am")],
            [InlineKeyboardButton("📣 Poll Oromoo",  callback_data="growth_poll_orm"),
             InlineKeyboardButton("🌍 Trilingual",   callback_data="growth_trilingual")],
            [InlineKeyboardButton("💬 Engage",       callback_data="growth_engage"),
             InlineKeyboardButton("🎁 Giveaway",     callback_data="growth_giveaway")],
            [InlineKeyboardButton("📢 Notify All",   callback_data="notify_all")],
        ]
        await query.edit_message_text("🌱 *Growth Tools:*",
            reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)

    elif data.startswith("growth_poll_"):
        lang = data.replace("growth_poll_", "")
        poll = growth.create_poll(lang)
        await ctx.bot.send_poll(chat_id=f"@{cfg.CHANNEL_USERNAME}",
            question=poll["question"], options=poll["options"], is_anonymous=True)
        await query.edit_message_text(
            f"📣 Poll published! ({LANG_NAMES.get(lang,lang)})", parse_mode=ParseMode.MARKDOWN)

    elif data == "growth_trilingual":
        await ctx.bot.send_message(chat_id=f"@{cfg.CHANNEL_USERNAME}",
            text=growth.create_trilingual_announcement(), parse_mode=ParseMode.MARKDOWN)
        await query.edit_message_text("🌍 Trilingual post published!", parse_mode=ParseMode.MARKDOWN)

    elif data == "growth_engage":
        await ctx.bot.send_message(chat_id=f"@{cfg.CHANNEL_USERNAME}",
            text=growth.create_engagement_post(), parse_mode=ParseMode.MARKDOWN)
        await query.edit_message_text("💬 Engagement post published!", parse_mode=ParseMode.MARKDOWN)

    elif data == "growth_giveaway":
        await ctx.bot.send_message(chat_id=f"@{cfg.CHANNEL_USERNAME}",
            text=growth.create_giveaway_post(), parse_mode=ParseMode.MARKDOWN)
        await query.edit_message_text("🎁 Giveaway published!", parse_mode=ParseMode.MARKDOWN)


# ════════════════════════════════════════════════════════════════════════════
#  SCHEDULED JOBS
# ════════════════════════════════════════════════════════════════════════════

async def auto_post_job(ctx: ContextTypes.DEFAULT_TYPE):
    if not scheduler.is_running: return
    topic = engine.pick_topic()
    lang  = engine.pick_language()
    try:
        text = engine.generate_post(topic, lang)
        await ctx.bot.send_message(chat_id=f"@{cfg.CHANNEL_USERNAME}",
            text=text, parse_mode=ParseMode.MARKDOWN)
        analytics.record_post(topic, lang)
        logger.info(f"Auto-posted: #{topic} [{lang}]")

        # Auto-notify all subscribers about new post
        if cfg.AUTO_NOTIFY_SUBSCRIBERS:
            users = list(referral._data["users"].values())
            notif = (
                f"🔔 *New post on @{cfg.CHANNEL_USERNAME}!*\n\n"
                f"Topic: #{topic}\n"
                f"👉 t.me/{cfg.CHANNEL_USERNAME}"
            )
            for u in users:
                try:
                    await ctx.bot.send_message(chat_id=u["user_id"],
                        text=notif, parse_mode=ParseMode.MARKDOWN)
                    await asyncio.sleep(0.05)
                except Exception: pass

    except Exception as e:
        logger.error(f"Auto-post failed: {e}")


async def refresh_members_job(ctx: ContextTypes.DEFAULT_TYPE):
    await refresh_members(ctx.application)


async def daily_summary_job(ctx: ContextTypes.DEFAULT_TYPE):
    report = analytics.daily_summary()
    for admin_id in cfg.ADMIN_IDS:
        try:
            await ctx.bot.send_message(chat_id=admin_id,
                text=report, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logger.error(f"Summary: {e}")


async def weekly_engagement_job(ctx: ContextTypes.DEFAULT_TYPE):
    for lang in ["en", "am", "orm"]:
        try:
            poll = growth.create_poll(lang)
            await ctx.bot.send_poll(chat_id=f"@{cfg.CHANNEL_USERNAME}",
                question=poll["question"], options=poll["options"], is_anonymous=True)
            await asyncio.sleep(2)
        except Exception as e:
            logger.error(f"Poll [{lang}]: {e}")


async def weekly_referral_reminder(ctx: ContextTypes.DEFAULT_TYPE):
    lb    = referral.get_leaderboard(3)
    medals= ["🥇","🥈","🥉"]
    top   = "\n".join(
        f"{medals[i]} {u.get('username') and '@'+u['username'] or u.get('first_name','User')} — {len(u['referrals'])} invites"
        for i,u in enumerate(lb)
    ) or "Be the first!"
    msg = (
        f"🏆 *Weekly Referral Update*\n\n"
        f"*Top Inviters:*\n{top}\n\n"
        f"📎 /referral — Get your link\n"
        f"📊 /mystats — Your stats"
    )
    for u in list(referral._data["users"].values()):
        try:
            await ctx.bot.send_message(chat_id=u["user_id"],
                text=msg, parse_mode=ParseMode.MARKDOWN)
            await asyncio.sleep(0.05)
        except Exception: pass


# ════════════════════════════════════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════════════════════════════════════

def main():
    global _tg_app, _tg_loop

    token = cfg.BOT_TOKEN
    if not token or token == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ Set TELEGRAM_BOT_TOKEN")
        return

    # Start Flask in background thread FIRST
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()

    # Build Telegram app
    _tg_app = Application.builder().token(token).build()

    # Public commands
    _tg_app.add_handler(CommandHandler("start",       start))
    _tg_app.add_handler(CommandHandler("referral",    cmd_referral))
    _tg_app.add_handler(CommandHandler("leaderboard", cmd_leaderboard))
    _tg_app.add_handler(CommandHandler("mystats",     cmd_mystats))

    # Admin commands
    _tg_app.add_handler(CommandHandler("post",        cmd_post))
    _tg_app.add_handler(CommandHandler("stats",       cmd_stats))
    _tg_app.add_handler(CommandHandler("schedule",    cmd_schedule))
    _tg_app.add_handler(CommandHandler("growth",      cmd_growth))
    _tg_app.add_handler(CommandHandler("preview",     cmd_preview))
    _tg_app.add_handler(CommandHandler("notify",      cmd_notify_all))

    _tg_app.add_handler(CallbackQueryHandler(callback_handler))

    jq: JobQueue = _tg_app.job_queue
    jq.run_repeating(auto_post_job,           interval=int(86400/cfg.POSTS_PER_DAY), first=30)
    jq.run_repeating(refresh_members_job,     interval=3600, first=10)
    jq.run_daily(daily_summary_job,           time=dtime(23, 55))
    jq.run_daily(weekly_engagement_job,       time=dtime(10, 0),  days=(0,))
    jq.run_daily(weekly_referral_reminder,    time=dtime(18, 0),  days=(2,))

    # Capture the running event loop AFTER polling starts
    async def post_init(app):
        global _tg_loop
        _tg_loop = asyncio.get_running_loop()
        logger.info(f"✅ Event loop captured: {_tg_loop}")

    _tg_app.post_init = post_init

    logger.info("🚀 ZemenByte bot starting...")
    _tg_app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
