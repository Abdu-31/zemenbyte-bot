#!/usr/bin/env python3
"""
ZemenByte Telegram Bot
======================
Auto-posting, growth automation, and channel management bot.
"""

import asyncio
import logging
import os
import json
import random
from datetime import datetime, time
from pathlib import Path

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
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


# ── Helper: fetch & store real member count ───────────────────────────────
async def refresh_members(app):
    try:
        count = await app.bot.get_chat_member_count(f"@{cfg.CHANNEL_USERNAME}")
        analytics.update_channel_stats(members=count)
        logger.info(f"Member count updated: {count}")
    except Exception as e:
        logger.warning(f"Could not fetch member count: {e}")


# ════════════════════════════════════════════════════════════════════════════
#  COMMANDS
# ════════════════════════════════════════════════════════════════════════════

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in cfg.ADMIN_IDS:
        await update.message.reply_text(
            "👋 Welcome! Follow @ZemenByte for daily tech insights."
        )
        return

    await refresh_members(ctx.application)
    stats = analytics.get_quick_stats()

    keyboard = [
        [InlineKeyboardButton("📊 Dashboard",   callback_data="dashboard"),
         InlineKeyboardButton("📝 Post Now",    callback_data="post_now")],
        [InlineKeyboardButton("⚙️ Schedule",    callback_data="schedule"),
         InlineKeyboardButton("🌱 Growth Tools",callback_data="growth")],
        [InlineKeyboardButton("📈 Analytics",   callback_data="analytics"),
         InlineKeyboardButton("🔧 Settings",    callback_data="settings")],
    ]
    text = (
        f"🤖 *ZemenByte Admin Panel*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📡 Channel: @{cfg.CHANNEL_USERNAME}\n"
        f"👥 Members: `{stats['members']:,}`\n"
        f"📬 Posts Today: `{stats['posts_today']}`\n"
        f"👁 Views (24h): `{stats['views_24h']:,}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🟢 Scheduler: {'Running' if scheduler.is_running else 'Stopped'}\n"
        f"🕐 Next post: {scheduler.next_post_time()}\n"
    )
    await update.message.reply_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )


async def cmd_post(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in cfg.ADMIN_IDS:
        return
    topics = cfg.TOPICS
    keyboard = [[InlineKeyboardButton(f"#{t}", callback_data=f"post_topic_{t}")] for t in topics]
    keyboard.append([InlineKeyboardButton("🎲 Auto-select", callback_data="post_topic_AUTO")])
    await update.message.reply_text(
        "📝 *Choose a topic to post:*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )


async def cmd_stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in cfg.ADMIN_IDS:
        return
    await refresh_members(ctx.application)
    await update.message.reply_text(analytics.full_report(), parse_mode=ParseMode.MARKDOWN)


async def cmd_schedule(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in cfg.ADMIN_IDS:
        return
    keyboard = [
        [InlineKeyboardButton("▶️ Start",  callback_data="sched_start"),
         InlineKeyboardButton("⏸ Pause",  callback_data="sched_pause")],
        [InlineKeyboardButton("🔄 Reset",  callback_data="sched_reset")],
    ]
    await update.message.reply_text(
        scheduler.show_schedule(),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )


async def cmd_growth(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in cfg.ADMIN_IDS:
        return
    keyboard = [
        [InlineKeyboardButton("📣 Create Poll",      callback_data="growth_poll"),
         InlineKeyboardButton("🎁 Giveaway",         callback_data="growth_giveaway")],
        [InlineKeyboardButton("📊 Engagement Post",  callback_data="growth_engage"),
         InlineKeyboardButton("🔔 Push Notification",callback_data="growth_notify")],
    ]
    await update.message.reply_text(
        "🌱 *Growth Engine* — Choose an action:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )


async def cmd_preview(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in cfg.ADMIN_IDS:
        return
    topic   = engine.pick_topic()
    preview = engine.generate_post(topic)
    await update.message.reply_text(
        f"👁 *Preview — Next Post (#{topic}):*\n\n{preview}",
        parse_mode=ParseMode.MARKDOWN
    )


# ════════════════════════════════════════════════════════════════════════════
#  CALLBACKS
# ════════════════════════════════════════════════════════════════════════════

async def callback_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data  = query.data

    if data == "dashboard":
        await refresh_members(ctx.application)
        await query.edit_message_text(analytics.full_report(), parse_mode=ParseMode.MARKDOWN)

    elif data == "post_now":
        keyboard = [[InlineKeyboardButton(f"#{t}", callback_data=f"post_topic_{t}")] for t in cfg.TOPICS]
        keyboard.append([InlineKeyboardButton("🎲 Auto", callback_data="post_topic_AUTO")])
        await query.edit_message_text(
            "📝 *Choose topic:*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )

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
            f"✅ *Posted!* Topic: #{topic}", parse_mode=ParseMode.MARKDOWN
        )

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
            [InlineKeyboardButton("📣 Poll",    callback_data="growth_poll"),
             InlineKeyboardButton("🎁 Giveaway",callback_data="growth_giveaway")],
            [InlineKeyboardButton("📊 Engage",  callback_data="growth_engage"),
             InlineKeyboardButton("🔔 Notify",  callback_data="growth_notify")],
        ]
        await query.edit_message_text(
            "🌱 *Growth Tools:*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )

    elif data == "growth_poll":
        poll = growth.create_poll()
        await ctx.bot.send_poll(
            chat_id=f"@{cfg.CHANNEL_USERNAME}",
            question=poll["question"], options=poll["options"], is_anonymous=True
        )
        await query.edit_message_text("📣 *Poll published!*", parse_mode=ParseMode.MARKDOWN)

    elif data == "growth_giveaway":
        await ctx.bot.send_message(
            chat_id=f"@{cfg.CHANNEL_USERNAME}",
            text=growth.create_giveaway_post(), parse_mode=ParseMode.MARKDOWN
        )
        await query.edit_message_text("🎁 *Giveaway post published!*", parse_mode=ParseMode.MARKDOWN)

    elif data == "growth_engage":
        await ctx.bot.send_message(
            chat_id=f"@{cfg.CHANNEL_USERNAME}",
            text=growth.create_engagement_post(), parse_mode=ParseMode.MARKDOWN
        )
        await query.edit_message_text("📊 *Engagement post published!*", parse_mode=ParseMode.MARKDOWN)

    elif data == "growth_notify":
        await ctx.bot.send_message(
            chat_id=f"@{cfg.CHANNEL_USERNAME}",
            text=growth.create_push_notification(), parse_mode=ParseMode.MARKDOWN
        )
        await query.edit_message_text("🔔 *Push notification sent!*", parse_mode=ParseMode.MARKDOWN)

    elif data == "settings":
        await query.edit_message_text(
            f"⚙️ *Settings*\n\n"
            f"Channel: @{cfg.CHANNEL_USERNAME}\n"
            f"Posts/day: {cfg.POSTS_PER_DAY}\n"
            f"Auto-engage: On\n"
            f"Hashtags: On\n",
            parse_mode=ParseMode.MARKDOWN
        )


# ════════════════════════════════════════════════════════════════════════════
#  SCHEDULED JOBS
# ════════════════════════════════════════════════════════════════════════════

async def auto_post_job(ctx: ContextTypes.DEFAULT_TYPE):
    if not scheduler.is_running:
        return
    topic     = engine.pick_topic()
    post_text = engine.generate_post(topic)
    try:
        await ctx.bot.send_message(
            chat_id=f"@{cfg.CHANNEL_USERNAME}",
            text=post_text, parse_mode=ParseMode.MARKDOWN
        )
        analytics.record_post(topic)
        logger.info(f"Auto-posted: #{topic}")
    except Exception as e:
        logger.error(f"Auto-post failed: {e}")


async def refresh_members_job(ctx: ContextTypes.DEFAULT_TYPE):
    await refresh_members(ctx.application)


async def daily_summary_job(ctx: ContextTypes.DEFAULT_TYPE):
    report = analytics.daily_summary()
    for admin_id in cfg.ADMIN_IDS:
        try:
            await ctx.bot.send_message(
                chat_id=admin_id, text=report, parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            logger.error(f"Summary failed for {admin_id}: {e}")


async def weekly_engagement_job(ctx: ContextTypes.DEFAULT_TYPE):
    poll = growth.create_poll()
    await ctx.bot.send_poll(
        chat_id=f"@{cfg.CHANNEL_USERNAME}",
        question=poll["question"], options=poll["options"], is_anonymous=True
    )
    await ctx.bot.send_message(
        chat_id=f"@{cfg.CHANNEL_USERNAME}",
        text=growth.create_engagement_post(), parse_mode=ParseMode.MARKDOWN
    )


# ════════════════════════════════════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════════════════════════════════════

def main():
    token = cfg.BOT_TOKEN
    if not token or token == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ Set BOT_TOKEN in env var TELEGRAM_BOT_TOKEN")
        return

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start",    start))
    app.add_handler(CommandHandler("post",     cmd_post))
    app.add_handler(CommandHandler("stats",    cmd_stats))
    app.add_handler(CommandHandler("schedule", cmd_schedule))
    app.add_handler(CommandHandler("growth",   cmd_growth))
    app.add_handler(CommandHandler("preview",  cmd_preview))
    app.add_handler(CallbackQueryHandler(callback_handler))

    jq: JobQueue = app.job_queue
    interval = int(86400 / cfg.POSTS_PER_DAY)
    jq.run_repeating(auto_post_job,       interval=interval, first=60)
    jq.run_repeating(refresh_members_job, interval=3600,     first=10)  # every hour
    jq.run_daily(daily_summary_job,   time=time(23, 55))
    jq.run_daily(weekly_engagement_job, time=time(10, 0), days=(0,))

    # Start REST API for Mini App dashboard
    api_server.start(analytics, scheduler, engine, app, cfg)

    logger.info("🚀 ZemenByte bot started!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
