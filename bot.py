#!/usr/bin/env python3
"""
ZemenByte Telegram Bot
======================
Auto-posting, growth automation, and channel management bot
for the ZemenByte channel covering AI, Tech, Crypto, Cybersecurity,
Innovation, and Quantum Computing.
"""

import asyncio
import logging
import os
import json
import random
from datetime import datetime, time
from pathlib import Path

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ChatPermissions, BotCommand
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, JobQueue
)
from telegram.constants import ParseMode

from content_engine import ContentEngine
from scheduler import PostScheduler
from analytics import AnalyticsTracker
from growth_engine import GrowthEngine
from config import Config

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("zemenbyte.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ZemenByte")

# ── Global instances ──────────────────────────────────────────────────────────
cfg      = Config()
engine   = ContentEngine(cfg)
scheduler = PostScheduler(cfg, engine)
analytics = AnalyticsTracker(cfg)
growth   = GrowthEngine(cfg)


# ════════════════════════════════════════════════════════════════════════════
#  ADMIN COMMANDS
# ════════════════════════════════════════════════════════════════════════════

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Welcome message with admin dashboard."""
    user = update.effective_user
    if user.id not in cfg.ADMIN_IDS:
        await update.message.reply_text("👋 Welcome! Follow @ZemenByte for daily tech insights.")
        return

    keyboard = [
        [InlineKeyboardButton("📊 Dashboard",      callback_data="dashboard"),
         InlineKeyboardButton("📝 Post Now",        callback_data="post_now")],
        [InlineKeyboardButton("⚙️ Schedule",        callback_data="schedule"),
         InlineKeyboardButton("🌱 Growth Tools",    callback_data="growth")],
        [InlineKeyboardButton("📈 Analytics",       callback_data="analytics"),
         InlineKeyboardButton("🔧 Settings",        callback_data="settings")],
    ]
    markup = InlineKeyboardMarkup(keyboard)

    stats = analytics.get_quick_stats()
    text = (
        f"🤖 *ZemenByte Admin Panel*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📡 Channel: @{cfg.CHANNEL_USERNAME}\n"
        f"👥 Members: `{stats['members']:,}`\n"
        f"📬 Posts Today: `{stats['posts_today']}`\n"
        f"👁 Views (24h): `{stats['views_24h']:,}`\n"
        f"🔗 Shares (24h): `{stats['shares_24h']}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🟢 Scheduler: {'Running' if scheduler.is_running else 'Stopped'}\n"
        f"🕐 Next post: {scheduler.next_post_time()}\n"
    )
    await update.message.reply_text(text, reply_markup=markup, parse_mode=ParseMode.MARKDOWN)


async def cmd_post(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Manually trigger a post for a specific topic."""
    if update.effective_user.id not in cfg.ADMIN_IDS:
        return

    topics = ["AI", "Crypto", "Cybersecurity", "Quantum", "Innovation", "Tech"]
    keyboard = [[InlineKeyboardButton(f"#{t}", callback_data=f"post_topic_{t}")] for t in topics]
    keyboard.append([InlineKeyboardButton("🎲 Auto-select", callback_data="post_topic_AUTO")])
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("📝 *Choose a topic to post:*", reply_markup=markup,
                                    parse_mode=ParseMode.MARKDOWN)


async def cmd_stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Show full analytics report."""
    if update.effective_user.id not in cfg.ADMIN_IDS:
        return
    report = analytics.full_report()
    await update.message.reply_text(report, parse_mode=ParseMode.MARKDOWN)


async def cmd_schedule(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Show and manage post schedule."""
    if update.effective_user.id not in cfg.ADMIN_IDS:
        return
    schedule_text = scheduler.show_schedule()
    keyboard = [
        [InlineKeyboardButton("▶️ Start",  callback_data="sched_start"),
         InlineKeyboardButton("⏸ Pause",  callback_data="sched_pause")],
        [InlineKeyboardButton("🔄 Reset",  callback_data="sched_reset")],
    ]
    await update.message.reply_text(schedule_text, reply_markup=InlineKeyboardMarkup(keyboard),
                                    parse_mode=ParseMode.MARKDOWN)


async def cmd_growth(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Growth toolkit."""
    if update.effective_user.id not in cfg.ADMIN_IDS:
        return
    keyboard = [
        [InlineKeyboardButton("📣 Create Poll",       callback_data="growth_poll"),
         InlineKeyboardButton("🎁 Giveaway",          callback_data="growth_giveaway")],
        [InlineKeyboardButton("📊 Engagement Post",   callback_data="growth_engage"),
         InlineKeyboardButton("🔔 Push Notification", callback_data="growth_notify")],
        [InlineKeyboardButton("🤝 Collab Request",    callback_data="growth_collab")],
    ]
    await update.message.reply_text(
        "🌱 *Growth Engine*\nChoose a growth action:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )


async def cmd_preview(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Preview next scheduled post."""
    if update.effective_user.id not in cfg.ADMIN_IDS:
        return
    preview = engine.generate_post(engine.pick_topic())
    await update.message.reply_text(
        f"👁 *Preview — Next Post:*\n\n{preview}",
        parse_mode=ParseMode.MARKDOWN
    )


# ════════════════════════════════════════════════════════════════════════════
#  CALLBACK HANDLERS
# ════════════════════════════════════════════════════════════════════════════

async def callback_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # ── Dashboard ──
    if data == "dashboard":
        stats = analytics.full_report()
        await query.edit_message_text(stats, parse_mode=ParseMode.MARKDOWN)

    # ── Post now ──
    elif data == "post_now":
        topics = ["AI", "Crypto", "Cybersecurity", "Quantum", "Innovation", "Tech"]
        keyboard = [[InlineKeyboardButton(f"#{t}", callback_data=f"post_topic_{t}")] for t in topics]
        keyboard.append([InlineKeyboardButton("🎲 Auto", callback_data="post_topic_AUTO")])
        await query.edit_message_text("📝 *Choose topic:*", reply_markup=InlineKeyboardMarkup(keyboard),
                                       parse_mode=ParseMode.MARKDOWN)

    elif data.startswith("post_topic_"):
        topic = data.replace("post_topic_", "")
        if topic == "AUTO":
            topic = engine.pick_topic()
        post_text = engine.generate_post(topic)
        await ctx.bot.send_message(
            chat_id=f"@{cfg.CHANNEL_USERNAME}",
            text=post_text,
            parse_mode=ParseMode.MARKDOWN
        )
        analytics.record_post(topic)
        await query.edit_message_text(
            f"✅ *Posted to @{cfg.CHANNEL_USERNAME}!*\n\n📌 Topic: #{topic}",
            parse_mode=ParseMode.MARKDOWN
        )

    # ── Analytics ──
    elif data == "analytics":
        report = analytics.full_report()
        await query.edit_message_text(report, parse_mode=ParseMode.MARKDOWN)

    # ── Schedule ──
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
        await query.edit_message_text("🔄 Scheduler *reset* to defaults.", parse_mode=ParseMode.MARKDOWN)

    # ── Growth ──
    elif data == "growth":
        keyboard = [
            [InlineKeyboardButton("📣 Poll",     callback_data="growth_poll"),
             InlineKeyboardButton("🎁 Giveaway", callback_data="growth_giveaway")],
            [InlineKeyboardButton("📊 Engage",   callback_data="growth_engage"),
             InlineKeyboardButton("🔔 Notify",   callback_data="growth_notify")],
        ]
        await query.edit_message_text("🌱 *Growth Tools:*",
                                       reply_markup=InlineKeyboardMarkup(keyboard),
                                       parse_mode=ParseMode.MARKDOWN)

    elif data == "growth_poll":
        poll = growth.create_poll()
        await ctx.bot.send_poll(
            chat_id=f"@{cfg.CHANNEL_USERNAME}",
            question=poll["question"],
            options=poll["options"],
            is_anonymous=True
        )
        await query.edit_message_text("📣 *Poll published!*", parse_mode=ParseMode.MARKDOWN)

    elif data == "growth_giveaway":
        giveaway_text = growth.create_giveaway_post()
        await ctx.bot.send_message(
            chat_id=f"@{cfg.CHANNEL_USERNAME}",
            text=giveaway_text,
            parse_mode=ParseMode.MARKDOWN
        )
        await query.edit_message_text("🎁 *Giveaway post published!*", parse_mode=ParseMode.MARKDOWN)

    elif data == "growth_engage":
        engage_text = growth.create_engagement_post()
        await ctx.bot.send_message(
            chat_id=f"@{cfg.CHANNEL_USERNAME}",
            text=engage_text,
            parse_mode=ParseMode.MARKDOWN
        )
        await query.edit_message_text("📊 *Engagement post published!*", parse_mode=ParseMode.MARKDOWN)

    elif data == "growth_notify":
        notify_text = growth.create_push_notification()
        await ctx.bot.send_message(
            chat_id=f"@{cfg.CHANNEL_USERNAME}",
            text=notify_text,
            parse_mode=ParseMode.MARKDOWN
        )
        await query.edit_message_text("🔔 *Push notification sent!*", parse_mode=ParseMode.MARKDOWN)

    elif data == "settings":
        settings_text = (
            f"⚙️ *Settings*\n\n"
            f"Channel: @{cfg.CHANNEL_USERNAME}\n"
            f"Posts/day: {cfg.POSTS_PER_DAY}\n"
            f"Languages: {', '.join(cfg.LANGUAGES)}\n"
            f"Auto-engage: {'On' if cfg.AUTO_ENGAGE else 'Off'}\n"
            f"Hashtags: {'On' if cfg.USE_HASHTAGS else 'Off'}\n"
            f"Emojis: {'On' if cfg.USE_EMOJIS else 'Off'}\n"
        )
        await query.edit_message_text(settings_text, parse_mode=ParseMode.MARKDOWN)


# ════════════════════════════════════════════════════════════════════════════
#  SCHEDULED JOB CALLBACKS
# ════════════════════════════════════════════════════════════════════════════

async def auto_post_job(ctx: ContextTypes.DEFAULT_TYPE):
    """Called by JobQueue to auto-post content."""
    if not scheduler.is_running:
        return
    topic = engine.pick_topic()
    post_text = engine.generate_post(topic)
    try:
        await ctx.bot.send_message(
            chat_id=f"@{cfg.CHANNEL_USERNAME}",
            text=post_text,
            parse_mode=ParseMode.MARKDOWN
        )
        analytics.record_post(topic)
        logger.info(f"Auto-posted on topic: {topic}")
    except Exception as e:
        logger.error(f"Auto-post failed: {e}")


async def daily_summary_job(ctx: ContextTypes.DEFAULT_TYPE):
    """Send daily analytics summary to admins."""
    report = analytics.daily_summary()
    for admin_id in cfg.ADMIN_IDS:
        try:
            await ctx.bot.send_message(
                chat_id=admin_id,
                text=report,
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            logger.error(f"Summary to admin {admin_id} failed: {e}")


async def weekly_engagement_job(ctx: ContextTypes.DEFAULT_TYPE):
    """Weekly engagement booster — poll + engagement post."""
    poll = growth.create_poll()
    await ctx.bot.send_poll(
        chat_id=f"@{cfg.CHANNEL_USERNAME}",
        question=poll["question"],
        options=poll["options"],
        is_anonymous=True
    )
    engage = growth.create_engagement_post()
    await ctx.bot.send_message(
        chat_id=f"@{cfg.CHANNEL_USERNAME}",
        text=engage,
        parse_mode=ParseMode.MARKDOWN
    )
    logger.info("Weekly engagement posts sent.")


# ════════════════════════════════════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════════════════════════════════════

def main():
    token = cfg.BOT_TOKEN
    if not token or token == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌  Set BOT_TOKEN in config.py or as env var TELEGRAM_BOT_TOKEN")
        return

    app = Application.builder().token(token).build()

    # Register commands
    app.add_handler(CommandHandler("start",    start))
    app.add_handler(CommandHandler("post",     cmd_post))
    app.add_handler(CommandHandler("stats",    cmd_stats))
    app.add_handler(CommandHandler("schedule", cmd_schedule))
    app.add_handler(CommandHandler("growth",   cmd_growth))
    app.add_handler(CommandHandler("preview",  cmd_preview))
    app.add_handler(CallbackQueryHandler(callback_handler))

    # Schedule auto-posting jobs (every 4h by default → ~6 posts/day)
    jq: JobQueue = app.job_queue
    interval_seconds = int(86400 / cfg.POSTS_PER_DAY)
    jq.run_repeating(auto_post_job, interval=interval_seconds, first=60)

    # Daily summary at 23:55 UTC
    jq.run_daily(daily_summary_job, time=time(23, 55))

    # Weekly engagement every Monday at 10:00 UTC
    jq.run_daily(weekly_engagement_job, time=time(10, 0), days=(0,))  # Monday

    logger.info("🚀 ZemenByte bot started successfully!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
