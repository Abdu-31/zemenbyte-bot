#!/usr/bin/env python3
"""
ZemenByte Telegram Bot
======================
Trilingual + Referral System
EN | አማርኛ | Afaan Oromoo
"""

import asyncio
import logging
import os
from datetime import datetime, time

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, JobQueue, MessageHandler, filters
)
from telegram.constants import ParseMode

from content_engine import ContentEngine
from scheduler import PostScheduler
from analytics import AnalyticsTracker
from growth_engine import GrowthEngine
from referral import ReferralSystem
from config import Config
import api_server

logging.basicConfig(
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    level=logging.INFO,
    handlers=[logging.FileHandler("zemenbyte.log"), logging.StreamHandler()]
)
logger = logging.getLogger("ZemenByte")

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


# ════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ════════════════════════════════════════════════════════════════════════════

async def refresh_members(app):
    try:
        count = await app.bot.get_chat_member_count(f"@{cfg.CHANNEL_USERNAME}")
        analytics.update_channel_stats(members=count)
    except Exception as e:
        logger.warning(f"Member count: {e}")


def is_admin(user_id: int) -> bool:
    return user_id in cfg.ADMIN_IDS


# ════════════════════════════════════════════════════════════════════════════
#  PUBLIC COMMANDS (all subscribers)
# ════════════════════════════════════════════════════════════════════════════

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = ctx.args  # referral code passed as ?start=<code>

    referred_by = None
    referrer    = None

    # Resolve referral code
    if args:
        code = args[0]
        ref_id = referral.resolve_code(code)
        if ref_id and ref_id != user.id:
            referred_by = ref_id
            referrer    = referral.get_user(ref_id)

    # Register user
    u = referral.register_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        referred_by=referred_by
    )

    # Admin dashboard
    if is_admin(user.id):
        await refresh_members(ctx.application)
        stats = analytics.get_quick_stats()
        keyboard = [
            [InlineKeyboardButton("📊 Dashboard",     callback_data="dashboard"),
             InlineKeyboardButton("📝 Post Now",      callback_data="post_now")],
            [InlineKeyboardButton("🌍 Post Language", callback_data="post_lang"),
             InlineKeyboardButton("🌱 Growth Tools",  callback_data="growth")],
            [InlineKeyboardButton("⚙️ Schedule",      callback_data="schedule"),
             InlineKeyboardButton("📈 Analytics",     callback_data="analytics")],
            [InlineKeyboardButton("🏆 Referral Stats",callback_data="admin_referral"),
             InlineKeyboardButton("🔧 Settings",      callback_data="settings")],
        ]
        text = (
            f"🤖 *ZemenByte Admin Panel*\n\n"
            f"👥 Members: `{stats['members']:,}`\n"
            f"📬 Posts Today: `{stats['posts_today']}`\n"
            f"🔗 Total Referrals: `{referral.total_referrals():,}`\n"
            f"👤 Registered Users: `{referral.total_users():,}`\n"
            f"🟢 Scheduler: {'Running' if scheduler.is_running else 'Stopped'}\n"
            f"🕐 Next: {scheduler.next_post_time()}\n"
        )
        await update.message.reply_text(
            text, reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    # Welcome message for referred user
    if referrer:
        welcome = referral.welcome_referred_user(u, referrer)
        await update.message.reply_text(welcome, parse_mode=ParseMode.MARKDOWN)
        # Notify referrer they got a new referral
        try:
            ref_count = referral.get_ref_count(referrer["user_id"])
            pts       = referral.get_points(referrer["user_id"])
            badges    = referral.get_badges(referrer["user_id"])
            badge_str = " ".join(badges) if badges else ""
            await ctx.bot.send_message(
                chat_id=referrer["user_id"],
                text=(
                    f"🎉 *New Referral!*\n\n"
                    f"Someone just joined ZemenByte through your link!\n\n"
                    f"👥 Total invites: `{ref_count}`\n"
                    f"⭐ Points: `{pts}`\n"
                    f"{('🎖 New badge: ' + badge_str) if badge_str else ''}\n\n"
                    f"Keep sharing! 🚀"
                ),
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception:
            pass
    else:
        # Normal welcome
        name = user.first_name or "friend"
        await update.message.reply_text(
            f"👋 *Welcome to ZemenByte, {name}!*\n\n"
            f"📡 Daily insights on:\n"
            f"🤖 AI • ₿ Crypto • 🔐 Cybersecurity\n"
            f"⚛️ Quantum • 💡 Innovation • 💻 Tech\n\n"
            f"🇬🇧 English • 🇪🇹 አማርኛ • 🟢 Afaan Oromoo\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"📎 Get your referral link → /referral\n"
            f"🏆 See top inviters → /leaderboard\n"
            f"📊 Your stats → /mystats",
            parse_mode=ParseMode.MARKDOWN
        )


async def cmd_referral(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Give user their referral link."""
    user = update.effective_user
    # Auto-register if not yet
    referral.register_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name
    )
    card = referral.referral_card(user.id)
    link = referral.get_ref_link(user.id)

    keyboard = [[
        InlineKeyboardButton("📤 Share Link", switch_inline_query=link),
        InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard"),
    ]]
    await update.message.reply_text(
        card,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )


async def cmd_leaderboard(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Show public leaderboard."""
    user = update.effective_user
    referral.register_user(user_id=user.id, username=user.username, first_name=user.first_name)
    lb_text = referral.leaderboard_text()
    keyboard = [[InlineKeyboardButton("🔗 My Referral Link", callback_data="my_referral")]]
    await update.message.reply_text(
        lb_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )


async def cmd_mystats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Show user's personal referral stats."""
    user = update.effective_user
    referral.register_user(user_id=user.id, username=user.username, first_name=user.first_name)
    card = referral.referral_card(user.id)
    keyboard = [[
        InlineKeyboardButton("📤 Share My Link", switch_inline_query=referral.get_ref_link(user.id)),
        InlineKeyboardButton("🏆 Leaderboard",   callback_data="leaderboard"),
    ]]
    await update.message.reply_text(
        card,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )


# ════════════════════════════════════════════════════════════════════════════
#  ADMIN COMMANDS
# ════════════════════════════════════════════════════════════════════════════

async def cmd_post(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    keyboard = [[InlineKeyboardButton(f"#{t}", callback_data=f"post_topic_{t}")] for t in cfg.TOPICS]
    keyboard.append([InlineKeyboardButton("🎲 Auto", callback_data="post_topic_AUTO")])
    await update.message.reply_text("📝 *Choose topic:*",
        reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)


async def cmd_stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    await refresh_members(ctx.application)
    await update.message.reply_text(analytics.full_report(), parse_mode=ParseMode.MARKDOWN)


async def cmd_broadcast_referral(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Admin: broadcast referral campaign to all registered users."""
    if not is_admin(update.effective_user.id): return
    users  = list(referral._data["users"].values())
    sent   = 0
    failed = 0
    msg = (
        "🔗 *ZemenByte Referral Program*\n\n"
        "Invite friends and earn points! 🎁\n\n"
        "🇬🇧 Get your unique link → /referral\n"
        "🇪🇹 የሪፈራል ሊንክህን ውሰድ → /referral\n"
        "🟢 Hidhata kee fudhadhu → /referral\n\n"
        "🏆 Top inviters win prizes!\n\n"
        "👉 /referral | /leaderboard"
    )
    await update.message.reply_text(f"📡 Broadcasting to {len(users)} users...")
    for u in users:
        try:
            await ctx.bot.send_message(
                chat_id=u["user_id"], text=msg, parse_mode=ParseMode.MARKDOWN
            )
            sent += 1
        except Exception:
            failed += 1
    await update.message.reply_text(
        f"✅ Broadcast complete!\n✅ Sent: {sent}\n❌ Failed: {failed}"
    )


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
        [InlineKeyboardButton("📣 Poll EN",      callback_data="growth_poll_en"),
         InlineKeyboardButton("📣 Poll አማርኛ",   callback_data="growth_poll_am")],
        [InlineKeyboardButton("📣 Poll Oromoo",  callback_data="growth_poll_orm"),
         InlineKeyboardButton("🌍 Trilingual",   callback_data="growth_trilingual")],
        [InlineKeyboardButton("💬 Engage Post",  callback_data="growth_engage"),
         InlineKeyboardButton("🔔 Push Notify",  callback_data="growth_notify")],
        [InlineKeyboardButton("🎁 Giveaway",     callback_data="growth_giveaway"),
         InlineKeyboardButton("📢 Broadcast Ref",callback_data="growth_broadcast_ref")],
    ]
    await update.message.reply_text("🌱 *Growth Engine:*",
        reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)


async def cmd_preview(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    topic = engine.pick_topic()
    lang  = engine.pick_language()
    preview = engine.generate_post(topic, lang)
    await update.message.reply_text(
        f"👁 *Preview — #{topic} [{LANG_NAMES[lang]}]:*\n\n{preview}",
        parse_mode=ParseMode.MARKDOWN
    )


# ════════════════════════════════════════════════════════════════════════════
#  CALLBACKS
# ════════════════════════════════════════════════════════════════════════════

async def callback_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data  = query.data

    # ── Public callbacks ──
    if data == "leaderboard":
        await query.edit_message_text(
            referral.leaderboard_text(), parse_mode=ParseMode.MARKDOWN
        )

    elif data == "my_referral":
        user_id = query.from_user.id
        referral.register_user(user_id=user_id, username=query.from_user.username,
                               first_name=query.from_user.first_name)
        await query.edit_message_text(
            referral.referral_card(user_id), parse_mode=ParseMode.MARKDOWN
        )

    # ── Admin only callbacks ──
    elif not is_admin(query.from_user.id):
        await query.answer("⛔ Admin only", show_alert=True)
        return

    elif data == "dashboard":
        await refresh_members(ctx.application)
        await query.edit_message_text(analytics.full_report(), parse_mode=ParseMode.MARKDOWN)

    elif data == "admin_referral":
        lb = referral.leaderboard_text()
        extra = (
            f"\n\n📊 *Referral System Stats*\n"
            f"👤 Registered users: `{referral.total_users():,}`\n"
            f"🔗 Total referrals:  `{referral.total_referrals():,}`"
        )
        await query.edit_message_text(lb + extra, parse_mode=ParseMode.MARKDOWN)

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
        await query.edit_message_text(f"📝 *{LANG_NAMES[lang]} — Choose topic:*",
            reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)

    elif data.startswith("postlang_"):
        parts = data.split("_", 2)
        lang  = parts[1]
        topic = parts[2]
        if topic == "AUTO": topic = engine.pick_topic()
        post_text = engine.generate_post(topic, lang)
        await ctx.bot.send_message(chat_id=f"@{cfg.CHANNEL_USERNAME}",
            text=post_text, parse_mode=ParseMode.MARKDOWN)
        analytics.record_post(topic, lang)
        await query.edit_message_text(
            f"✅ Posted! #{topic} | {LANG_NAMES[lang]}", parse_mode=ParseMode.MARKDOWN)

    elif data.startswith("post_topic_"):
        topic = data.replace("post_topic_", "")
        if topic == "AUTO": topic = engine.pick_topic()
        lang      = engine.pick_language()
        post_text = engine.generate_post(topic, lang)
        await ctx.bot.send_message(chat_id=f"@{cfg.CHANNEL_USERNAME}",
            text=post_text, parse_mode=ParseMode.MARKDOWN)
        analytics.record_post(topic, lang)
        await query.edit_message_text(
            f"✅ Posted! #{topic} | {LANG_NAMES[lang]}", parse_mode=ParseMode.MARKDOWN)

    elif data == "analytics":
        await refresh_members(ctx.application)
        await query.edit_message_text(analytics.full_report(), parse_mode=ParseMode.MARKDOWN)

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
            [InlineKeyboardButton("📣 Poll EN",       callback_data="growth_poll_en"),
             InlineKeyboardButton("📣 Poll አማርኛ",    callback_data="growth_poll_am")],
            [InlineKeyboardButton("📣 Poll Oromoo",   callback_data="growth_poll_orm"),
             InlineKeyboardButton("🌍 Trilingual",    callback_data="growth_trilingual")],
            [InlineKeyboardButton("💬 Engage",        callback_data="growth_engage"),
             InlineKeyboardButton("🔔 Notify",        callback_data="growth_notify")],
            [InlineKeyboardButton("🎁 Giveaway",      callback_data="growth_giveaway"),
             InlineKeyboardButton("📢 Broadcast Ref", callback_data="growth_broadcast_ref")],
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

    elif data == "growth_notify":
        await ctx.bot.send_message(chat_id=f"@{cfg.CHANNEL_USERNAME}",
            text=growth.create_push_notification(), parse_mode=ParseMode.MARKDOWN)
        await query.edit_message_text("🔔 Push notification sent!", parse_mode=ParseMode.MARKDOWN)

    elif data == "growth_giveaway":
        await ctx.bot.send_message(chat_id=f"@{cfg.CHANNEL_USERNAME}",
            text=growth.create_giveaway_post(), parse_mode=ParseMode.MARKDOWN)
        await query.edit_message_text("🎁 Giveaway published!", parse_mode=ParseMode.MARKDOWN)

    elif data == "growth_broadcast_ref":
        users  = list(referral._data["users"].values())
        msg    = (
            "🔗 *ZemenByte Referral Program*\n\n"
            "Invite friends and earn points! 🎁\n\n"
            "🇬🇧 Get your link → /referral\n"
            "🇪🇹 ሊንክህን ውሰድ → /referral\n"
            "🟢 Hidhata kee fudhachuuf → /referral\n\n"
            "🏆 Top inviters win prizes!\n"
            "👉 /leaderboard"
        )
        sent = 0
        for u in users:
            try:
                await ctx.bot.send_message(chat_id=u["user_id"],
                    text=msg, parse_mode=ParseMode.MARKDOWN)
                sent += 1
            except Exception:
                pass
        await query.edit_message_text(
            f"📢 Referral broadcast sent to {sent} users!", parse_mode=ParseMode.MARKDOWN)

    elif data == "settings":
        lw = dict(zip(cfg.LANGUAGES, cfg.LANGUAGE_WEIGHTS))
        await query.edit_message_text(
            f"⚙️ *Settings*\n\n"
            f"Channel: @{cfg.CHANNEL_USERNAME}\n"
            f"Posts/day: {cfg.POSTS_PER_DAY}\n"
            f"Topics: {len(cfg.TOPICS)}\n"
            f"🇬🇧 English: {int(lw.get('en',0.5)*100)}%\n"
            f"🇪🇹 አማርኛ: {int(lw.get('am',0.3)*100)}%\n"
            f"🟢 Afaan Oromoo: {int(lw.get('orm',0.2)*100)}%\n",
            parse_mode=ParseMode.MARKDOWN
        )


# ════════════════════════════════════════════════════════════════════════════
#  SCHEDULED JOBS
# ════════════════════════════════════════════════════════════════════════════

async def auto_post_job(ctx: ContextTypes.DEFAULT_TYPE):
    if not scheduler.is_running: return
    topic = engine.pick_topic()
    lang  = engine.pick_language()
    try:
        post_text = engine.generate_post(topic, lang)
        await ctx.bot.send_message(chat_id=f"@{cfg.CHANNEL_USERNAME}",
            text=post_text, parse_mode=ParseMode.MARKDOWN)
        analytics.record_post(topic, lang)
        logger.info(f"Auto-posted: #{topic} [{lang}]")
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
            logger.error(f"Summary to {admin_id}: {e}")


async def weekly_referral_reminder_job(ctx: ContextTypes.DEFAULT_TYPE):
    """Every Wednesday: remind all registered users about referral program."""
    users = list(referral._data["users"].values())
    lb    = referral.get_leaderboard(3)
    top   = ""
    medals = ["🥇","🥈","🥉"]
    for i, u in enumerate(lb):
        name  = u.get("username") and f"@{u['username']}" or u.get("first_name","User")
        top  += f"{medals[i]} {name} — {len(u['referrals'])} invites\n"

    msg = (
        f"🏆 *ZemenByte Weekly Referral Update*\n\n"
        f"*Top Inviters This Week:*\n{top if top else 'Be the first!'}\n\n"
        f"📎 Get your link → /referral\n"
        f"📊 Check stats → /mystats"
    )
    for u in users:
        try:
            await ctx.bot.send_message(chat_id=u["user_id"],
                text=msg, parse_mode=ParseMode.MARKDOWN)
        except Exception:
            pass


async def weekly_engagement_job(ctx: ContextTypes.DEFAULT_TYPE):
    for lang in ["en", "am", "orm"]:
        try:
            poll = growth.create_poll(lang)
            await ctx.bot.send_poll(chat_id=f"@{cfg.CHANNEL_USERNAME}",
                question=poll["question"], options=poll["options"], is_anonymous=True)
        except Exception as e:
            logger.error(f"Poll [{lang}]: {e}")


# ════════════════════════════════════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════════════════════════════════════

def main():
    token = cfg.BOT_TOKEN
    if not token or token == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ Set TELEGRAM_BOT_TOKEN")
        return

    app = Application.builder().token(token).build()

    # Public commands
    app.add_handler(CommandHandler("start",       start))
    app.add_handler(CommandHandler("referral",    cmd_referral))
    app.add_handler(CommandHandler("leaderboard", cmd_leaderboard))
    app.add_handler(CommandHandler("mystats",     cmd_mystats))

    # Admin commands
    app.add_handler(CommandHandler("post",      cmd_post))
    app.add_handler(CommandHandler("stats",     cmd_stats))
    app.add_handler(CommandHandler("schedule",  cmd_schedule))
    app.add_handler(CommandHandler("growth",    cmd_growth))
    app.add_handler(CommandHandler("preview",   cmd_preview))
    app.add_handler(CommandHandler("broadcast", cmd_broadcast_referral))

    app.add_handler(CallbackQueryHandler(callback_handler))

    jq: JobQueue = app.job_queue
    jq.run_repeating(auto_post_job,              interval=int(86400/cfg.POSTS_PER_DAY), first=30)
    jq.run_repeating(refresh_members_job,        interval=3600, first=10)
    jq.run_daily(daily_summary_job,              time=time(23, 55))
    jq.run_daily(weekly_engagement_job,          time=time(10, 0), days=(0,))   # Monday
    jq.run_daily(weekly_referral_reminder_job,   time=time(18, 0), days=(2,))   # Wednesday

    logger.info("🚀 ZemenByte bot started — Referral system active!")

    async def post_init(application):
        """Called after the event loop starts — safe to pass loop now."""
        loop = asyncio.get_event_loop()
        api_server.init(analytics, scheduler, engine, application, cfg, loop)
        port   = int(os.getenv("PORT", "8080"))
        from http.server import HTTPServer
        from api_server import Handler
        server = HTTPServer(("0.0.0.0", port), Handler)
        import threading
        t = threading.Thread(target=server.serve_forever, daemon=True)
        t.start()
        logger.info(f"✅ API server started on port {port}")

    app.post_init = post_init
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
