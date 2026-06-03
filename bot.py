#!/usr/bin/env python3
"""
ZemenByte Telegram Bot
======================
Trilingual auto-posting bot — English, Amharic, Afaan Oromoo
Topics: AI, Crypto, Cybersecurity, Quantum, Innovation, Tech, Technology, DeepTech
"""

import logging
import os
from datetime import datetime, time

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
from config import Config
import api_server

# ── Logging ───────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    level=logging.INFO,
    handlers=[logging.FileHandler("zemenbyte.log"), logging.StreamHandler()]
)
logger = logging.getLogger("ZemenByte")

# ── Globals ───────────────────────────────────────────────────────────────
cfg       = Config()
engine    = ContentEngine(cfg)
scheduler = PostScheduler(cfg, engine)
analytics = AnalyticsTracker(cfg)
growth    = GrowthEngine(cfg)

# Language display names for UI
LANG_NAMES = {"en": "🇬🇧 English", "am": "🇪🇹 አማርኛ", "orm": "🟢 Afaan Oromoo"}


# ════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ════════════════════════════════════════════════════════════════════════════

async def refresh_members(app):
    try:
        count = await app.bot.get_chat_member_count(f"@{cfg.CHANNEL_USERNAME}")
        analytics.update_channel_stats(members=count)
        logger.info(f"Members: {count}")
    except Exception as e:
        logger.warning(f"Member count failed: {e}")


async def send_post(ctx, topic: str, lang: str = None):
    """Generate and send a post. Returns (post_text, lang_used)."""
    if lang is None:
        lang = engine.pick_language()
    post_text = engine.generate_post(topic, lang)
    await ctx.bot.send_message(
        chat_id=f"@{cfg.CHANNEL_USERNAME}",
        text=post_text,
        parse_mode=ParseMode.MARKDOWN
    )
    analytics.record_post(topic, lang)
    logger.info(f"Posted #{topic} [{lang}]")
    return post_text, lang


# ════════════════════════════════════════════════════════════════════════════
#  ADMIN COMMANDS
# ════════════════════════════════════════════════════════════════════════════

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in cfg.ADMIN_IDS:
        await update.message.reply_text(
            "👋 Welcome! Follow @ZemenByte for daily tech insights.\n"
            "ጥሩ መጣህ! @ZemenByte ተከተል።\n"
            "Baga nagaan dhuftan! @ZemenByte hordofaa."
        )
        return

    await refresh_members(ctx.application)
    stats = analytics.get_quick_stats()

    keyboard = [
        [InlineKeyboardButton("📊 Dashboard",    callback_data="dashboard"),
         InlineKeyboardButton("📝 Post Now",     callback_data="post_now")],
        [InlineKeyboardButton("🌍 Post Language",callback_data="post_lang"),
         InlineKeyboardButton("🌱 Growth Tools", callback_data="growth")],
        [InlineKeyboardButton("⚙️ Schedule",     callback_data="schedule"),
         InlineKeyboardButton("📈 Analytics",    callback_data="analytics")],
        [InlineKeyboardButton("🔧 Settings",     callback_data="settings")],
    ]
    text = (
        f"🤖 *ZemenByte Admin Panel*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📡 Channel: @{cfg.CHANNEL_USERNAME}\n"
        f"👥 Members: `{stats['members']:,}`\n"
        f"📬 Posts Today: `{stats['posts_today']}`\n"
        f"🌍 Languages: EN • አማርኛ • Oromoo\n"
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
    keyboard = [[InlineKeyboardButton(f"#{t}", callback_data=f"post_topic_{t}")] for t in cfg.TOPICS]
    keyboard.append([InlineKeyboardButton("🎲 Auto-select", callback_data="post_topic_AUTO")])
    await update.message.reply_text(
        "📝 *Choose a topic:*",
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
        [InlineKeyboardButton("📣 Poll (EN)",    callback_data="growth_poll_en"),
         InlineKeyboardButton("📣 Poll (አማርኛ)", callback_data="growth_poll_am")],
        [InlineKeyboardButton("📣 Poll (Oromoo)",callback_data="growth_poll_orm"),
         InlineKeyboardButton("🎁 Giveaway",     callback_data="growth_giveaway")],
        [InlineKeyboardButton("💬 Engage Post",  callback_data="growth_engage"),
         InlineKeyboardButton("🔔 Push Notify",  callback_data="growth_notify")],
        [InlineKeyboardButton("🌍 Trilingual Post", callback_data="growth_trilingual")],
    ]
    await update.message.reply_text(
        "🌱 *Growth Engine — Choose action:*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )


async def cmd_preview(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in cfg.ADMIN_IDS:
        return
    topic = engine.pick_topic()
    msgs = []
    for lang in ["en", "am", "orm"]:
        preview = engine.generate_post(topic, lang)
        msgs.append(f"*{LANG_NAMES[lang]}:*\n{preview}")
    await update.message.reply_text(
        f"👁 *Preview — #{topic}*\n\n" + "\n\n─────────\n\n".join(msgs),
        parse_mode=ParseMode.MARKDOWN
    )


# ════════════════════════════════════════════════════════════════════════════
#  CALLBACKS
# ════════════════════════════════════════════════════════════════════════════

async def callback_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data  = query.data

    # ── Dashboard ──
    if data == "dashboard":
        await refresh_members(ctx.application)
        await query.edit_message_text(analytics.full_report(), parse_mode=ParseMode.MARKDOWN)

    # ── Post Now (topic select) ──
    elif data == "post_now":
        keyboard = [[InlineKeyboardButton(f"#{t}", callback_data=f"post_topic_{t}")] for t in cfg.TOPICS]
        keyboard.append([InlineKeyboardButton("🎲 Auto", callback_data="post_topic_AUTO")])
        await query.edit_message_text(
            "📝 *Choose topic (auto language):*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )

    # ── Post with language selection ──
    elif data == "post_lang":
        keyboard = [
            [InlineKeyboardButton("🇬🇧 English",     callback_data="lang_en"),
             InlineKeyboardButton("🇪🇹 አማርኛ",       callback_data="lang_am")],
            [InlineKeyboardButton("🟢 Afaan Oromoo", callback_data="lang_orm")],
        ]
        await query.edit_message_text(
            "🌍 *Choose language to post in:*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )

    elif data.startswith("lang_"):
        lang = data.replace("lang_", "")
        keyboard = [[InlineKeyboardButton(f"#{t}", callback_data=f"postlang_{lang}_{t}")] for t in cfg.TOPICS]
        keyboard.append([InlineKeyboardButton("🎲 Auto Topic", callback_data=f"postlang_{lang}_AUTO")])
        await query.edit_message_text(
            f"📝 *{LANG_NAMES[lang]} — Choose topic:*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )

    elif data.startswith("postlang_"):
        parts = data.split("_", 2)
        lang  = parts[1]
        topic = parts[2]
        if topic == "AUTO":
            topic = engine.pick_topic()
        post_text = engine.generate_post(topic, lang)
        await ctx.bot.send_message(
            chat_id=f"@{cfg.CHANNEL_USERNAME}",
            text=post_text, parse_mode=ParseMode.MARKDOWN
        )
        analytics.record_post(topic, lang)
        await query.edit_message_text(
            f"✅ *Posted!*\nTopic: #{topic}\nLanguage: {LANG_NAMES[lang]}",
            parse_mode=ParseMode.MARKDOWN
        )

    # ── Auto topic post ──
    elif data.startswith("post_topic_"):
        topic = data.replace("post_topic_", "")
        if topic == "AUTO":
            topic = engine.pick_topic()
        lang = engine.pick_language()
        post_text = engine.generate_post(topic, lang)
        await ctx.bot.send_message(
            chat_id=f"@{cfg.CHANNEL_USERNAME}",
            text=post_text, parse_mode=ParseMode.MARKDOWN
        )
        analytics.record_post(topic, lang)
        await query.edit_message_text(
            f"✅ *Posted!*\nTopic: #{topic} | Language: {LANG_NAMES[lang]}",
            parse_mode=ParseMode.MARKDOWN
        )

    # ── Analytics ──
    elif data == "analytics":
        await refresh_members(ctx.application)
        await query.edit_message_text(analytics.full_report(), parse_mode=ParseMode.MARKDOWN)

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
        await query.edit_message_text("🔄 Scheduler *reset*.", parse_mode=ParseMode.MARKDOWN)

    # ── Growth ──
    elif data == "growth":
        keyboard = [
            [InlineKeyboardButton("📣 Poll EN",      callback_data="growth_poll_en"),
             InlineKeyboardButton("📣 Poll አማርኛ",   callback_data="growth_poll_am")],
            [InlineKeyboardButton("📣 Poll Oromoo",  callback_data="growth_poll_orm"),
             InlineKeyboardButton("🎁 Giveaway",     callback_data="growth_giveaway")],
            [InlineKeyboardButton("💬 Engage",       callback_data="growth_engage"),
             InlineKeyboardButton("🔔 Notify",       callback_data="growth_notify")],
            [InlineKeyboardButton("🌍 Trilingual",   callback_data="growth_trilingual")],
        ]
        await query.edit_message_text(
            "🌱 *Growth Tools:*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )

    elif data.startswith("growth_poll_"):
        lang = data.replace("growth_poll_", "")
        poll = growth.create_poll(lang)
        await ctx.bot.send_poll(
            chat_id=f"@{cfg.CHANNEL_USERNAME}",
            question=poll["question"], options=poll["options"], is_anonymous=True
        )
        await query.edit_message_text(
            f"📣 *Poll published!* ({LANG_NAMES.get(lang, lang)})",
            parse_mode=ParseMode.MARKDOWN
        )

    elif data == "growth_giveaway":
        await ctx.bot.send_message(
            chat_id=f"@{cfg.CHANNEL_USERNAME}",
            text=growth.create_giveaway_post(), parse_mode=ParseMode.MARKDOWN
        )
        await query.edit_message_text("🎁 *Giveaway published!*", parse_mode=ParseMode.MARKDOWN)

    elif data == "growth_engage":
        await ctx.bot.send_message(
            chat_id=f"@{cfg.CHANNEL_USERNAME}",
            text=growth.create_engagement_post(), parse_mode=ParseMode.MARKDOWN
        )
        await query.edit_message_text("💬 *Engagement post published!*", parse_mode=ParseMode.MARKDOWN)

    elif data == "growth_notify":
        await ctx.bot.send_message(
            chat_id=f"@{cfg.CHANNEL_USERNAME}",
            text=growth.create_push_notification(), parse_mode=ParseMode.MARKDOWN
        )
        await query.edit_message_text("🔔 *Push notification sent!*", parse_mode=ParseMode.MARKDOWN)

    elif data == "growth_trilingual":
        text = growth.create_trilingual_announcement()
        await ctx.bot.send_message(
            chat_id=f"@{cfg.CHANNEL_USERNAME}",
            text=text, parse_mode=ParseMode.MARKDOWN
        )
        await query.edit_message_text("🌍 *Trilingual announcement posted!*", parse_mode=ParseMode.MARKDOWN)

    elif data == "settings":
        lang_weights = dict(zip(cfg.LANGUAGES, cfg.LANGUAGE_WEIGHTS))
        await query.edit_message_text(
            f"⚙️ *Settings*\n\n"
            f"Channel: @{cfg.CHANNEL_USERNAME}\n"
            f"Posts/day: {cfg.POSTS_PER_DAY}\n"
            f"Topics: {len(cfg.TOPICS)}\n"
            f"Languages:\n"
            f"  🇬🇧 English: {int(lang_weights.get('en',0.5)*100)}%\n"
            f"  🇪🇹 አማርኛ: {int(lang_weights.get('am',0.3)*100)}%\n"
            f"  🟢 Afaan Oromoo: {int(lang_weights.get('orm',0.2)*100)}%\n",
            parse_mode=ParseMode.MARKDOWN
        )


# ════════════════════════════════════════════════════════════════════════════
#  SCHEDULED JOBS
# ════════════════════════════════════════════════════════════════════════════

async def auto_post_job(ctx: ContextTypes.DEFAULT_TYPE):
    """Auto-post with weighted language rotation."""
    if not scheduler.is_running:
        return
    topic = engine.pick_topic()
    lang  = engine.pick_language()
    try:
        post_text = engine.generate_post(topic, lang)
        await ctx.bot.send_message(
            chat_id=f"@{cfg.CHANNEL_USERNAME}",
            text=post_text, parse_mode=ParseMode.MARKDOWN
        )
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
            await ctx.bot.send_message(
                chat_id=admin_id, text=report, parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            logger.error(f"Summary failed for {admin_id}: {e}")


async def weekly_engagement_job(ctx: ContextTypes.DEFAULT_TYPE):
    """Post poll in each language on Mondays."""
    for lang in ["en", "am", "orm"]:
        try:
            poll = growth.create_poll(lang)
            await ctx.bot.send_poll(
                chat_id=f"@{cfg.CHANNEL_USERNAME}",
                question=poll["question"], options=poll["options"], is_anonymous=True
            )
        except Exception as e:
            logger.error(f"Weekly poll [{lang}] failed: {e}")


# ════════════════════════════════════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════════════════════════════════════

def main():
    token = cfg.BOT_TOKEN
    if not token or token == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ Set TELEGRAM_BOT_TOKEN env var")
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
    jq.run_repeating(auto_post_job,       interval=interval, first=30)
    jq.run_repeating(refresh_members_job, interval=3600,     first=10)
    jq.run_daily(daily_summary_job,     time=time(23, 55))
    jq.run_daily(weekly_engagement_job, time=time(10, 0), days=(0,))

    # Start REST API
    api_server.start(analytics, scheduler, engine, app, cfg)

    logger.info("🚀 ZemenByte bot started — EN | አማርኛ | Afaan Oromoo")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
