#!/usr/bin/env python3
"""
ZemenByte Telegram Bot — Pure Bot Version (No Dashboard/Flask)
==============================================================
All admin actions done directly via bot commands & inline buttons.
Trilingual: EN | አማርኛ | Afaan Oromoo
"""

import asyncio
import logging
import os
from datetime import datetime, time as dtime

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

logging.basicConfig(
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    level=logging.INFO,
    handlers=[logging.FileHandler("zemenbyte.log"), logging.StreamHandler()]
)
logger = logging.getLogger("ZemenByte")

cfg      = Config()
engine   = ContentEngine(cfg)
sched    = PostScheduler(cfg, engine)
analytics= AnalyticsTracker(cfg)
growth   = GrowthEngine(cfg)
referral = ReferralSystem(
    bot_username=os.getenv("BOT_USERNAME", "ZemenByteBot"),
    channel_username=cfg.CHANNEL_USERNAME
)

LANG_NAMES = {"en": "🇬🇧 English", "am": "🇪🇹 አማርኛ", "orm": "🟢 Afaan Oromoo"}

def is_admin(uid): return uid in cfg.ADMIN_IDS

async def refresh_members(app):
    try:
        count = await app.bot.get_chat_member_count(f"@{cfg.CHANNEL_USERNAME}")
        analytics.update_channel_stats(members=count)
        return count
    except Exception as e:
        logger.warning(f"Members: {e}")
        return analytics._data.get("members", 0)


# ════════════════════════════════════════════════════════════════════════════
#  ADMIN DASHBOARD — inline keyboard
# ════════════════════════════════════════════════════════════════════════════

async def show_dashboard(update_or_query, ctx, edit=False):
    await refresh_members(ctx.application)
    stats  = analytics.get_quick_stats()
    lw     = dict(zip(cfg.LANGUAGES, cfg.LANGUAGE_WEIGHTS))
    text   = (
        f"🤖 *ZemenByte Admin Panel*\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📡 @{cfg.CHANNEL_USERNAME}\n"
        f"👥 Members:    `{stats['members']:,}`\n"
        f"📬 Today:      `{stats['posts_today']}` / {cfg.POSTS_PER_DAY}\n"
        f"📊 Total:      `{analytics._data.get('total_posts',0)}`\n"
        f"👤 Subscribers:`{referral.total_users():,}`\n"
        f"🔗 Referrals:  `{referral.total_referrals():,}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🟢 Scheduler: {'Running ▶️' if sched.is_running else 'Paused ⏸'}\n"
        f"🕐 Next post: {sched.next_post_time()}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🌍 EN:{int(lw.get('en',0.5)*100)}% "
        f"አማ:{int(lw.get('am',0.3)*100)}% "
        f"Oro:{int(lw.get('orm',0.2)*100)}%"
    )
    keyboard = [
        [InlineKeyboardButton("📝 Post Now",        callback_data="post_now"),
         InlineKeyboardButton("🌍 Choose Language", callback_data="post_lang")],
        [InlineKeyboardButton("🌱 Growth Tools",    callback_data="growth"),
         InlineKeyboardButton("📢 Notify All",      callback_data="notify_menu")],
        [InlineKeyboardButton("⏰ Schedule",         callback_data="schedule"),
         InlineKeyboardButton("🏆 Referral Stats",  callback_data="ref_stats")],
        [InlineKeyboardButton("📊 Analytics",       callback_data="analytics"),
         InlineKeyboardButton("🔄 Refresh",         callback_data="dashboard")],
    ]
    markup = InlineKeyboardMarkup(keyboard)
    if edit:
        await update_or_query.edit_message_text(text, reply_markup=markup, parse_mode=ParseMode.MARKDOWN)
    else:
        await update_or_query.message.reply_text(text, reply_markup=markup, parse_mode=ParseMode.MARKDOWN)


# ════════════════════════════════════════════════════════════════════════════
#  PUBLIC COMMANDS
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
        await show_dashboard(update, ctx)
        return

    if referrer:
        await update.message.reply_text(
            referral.welcome_referred_user(u, referrer),
            parse_mode=ParseMode.MARKDOWN
        )
        try:
            count = referral.get_ref_count(referrer["user_id"])
            pts   = referral.get_points(referrer["user_id"])
            badges= " ".join(referral.get_badges(referrer["user_id"]))
            await ctx.bot.send_message(
                chat_id=referrer["user_id"],
                text=(
                    f"🎉 *New Referral!*\n\n"
                    f"Someone joined via your link!\n"
                    f"👥 Total: `{count}` | ⭐ Points: `{pts}`"
                    + (f"\n🎖 New badge: {badges}" if badges else "")
                ),
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
            f"📊 /mystats — Your referral stats",
            parse_mode=ParseMode.MARKDOWN
        )


async def cmd_referral(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    referral.register_user(user_id=user.id, username=user.username, first_name=user.first_name)
    card = referral.referral_card(user.id)
    link = referral.get_ref_link(user.id)
    keyboard = [[
        InlineKeyboardButton("📤 Share Link",  switch_inline_query=link),
        InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard"),
    ]]
    await update.message.reply_text(card,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN)


async def cmd_leaderboard(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    referral.register_user(user_id=user.id, username=user.username, first_name=user.first_name)
    keyboard = [[InlineKeyboardButton("🔗 My Link", callback_data="my_referral")]]
    await update.message.reply_text(referral.leaderboard_text(),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN)


async def cmd_mystats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    referral.register_user(user_id=user.id, username=user.username, first_name=user.first_name)
    card = referral.referral_card(user.id)
    keyboard = [[
        InlineKeyboardButton("📤 Share", switch_inline_query=referral.get_ref_link(user.id)),
        InlineKeyboardButton("🏆 Top",   callback_data="leaderboard"),
    ]]
    await update.message.reply_text(card,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN)


# ════════════════════════════════════════════════════════════════════════════
#  ADMIN COMMANDS
# ════════════════════════════════════════════════════════════════════════════

async def cmd_post(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    keyboard = [[InlineKeyboardButton(f"#{t}", callback_data=f"post_topic_{t}")] for t in cfg.TOPICS]
    keyboard.append([InlineKeyboardButton("🎲 Auto", callback_data="post_topic_AUTO")])
    await update.message.reply_text("📝 *Choose topic:*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN)


async def cmd_stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    await refresh_members(ctx.application)
    await update.message.reply_text(analytics.full_report(), parse_mode=ParseMode.MARKDOWN)


async def cmd_notify(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Admin: /notify <message>"""
    if not is_admin(update.effective_user.id): return
    text = " ".join(ctx.args) if ctx.args else ""
    if not text:
        await update.message.reply_text(
            "📢 *Usage:* `/notify Your message here`\n\n"
            "Supports Markdown. Sends to all registered subscribers.",
            parse_mode=ParseMode.MARKDOWN)
        return
    await _broadcast(ctx, update.message, text)


async def cmd_preview(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    topic   = engine.pick_topic()
    lang    = engine.pick_language()
    preview = engine.generate_post(topic, lang)
    await update.message.reply_text(
        f"👁 *Preview — #{topic} {LANG_NAMES[lang]}:*\n\n{preview}",
        parse_mode=ParseMode.MARKDOWN)


async def cmd_schedule(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    keyboard = [
        [InlineKeyboardButton("▶️ Resume", callback_data="sched_start"),
         InlineKeyboardButton("⏸ Pause",  callback_data="sched_pause")],
        [InlineKeyboardButton("🔄 Reset",  callback_data="sched_reset")],
    ]
    await update.message.reply_text(sched.show_schedule(),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN)


# ════════════════════════════════════════════════════════════════════════════
#  BROADCAST HELPER
# ════════════════════════════════════════════════════════════════════════════

async def _broadcast(ctx, reply_msg, text: str):
    users = list(referral._data["users"].values())
    status_msg = await reply_msg.reply_text(f"📡 Sending to {len(users)} subscribers...")
    sent = failed = 0
    for u in users:
        try:
            await ctx.bot.send_message(
                chat_id=u["user_id"], text=text, parse_mode=ParseMode.MARKDOWN)
            sent += 1
            await asyncio.sleep(0.05)
        except Exception:
            failed += 1
    await status_msg.edit_text(
        f"✅ *Broadcast Complete*\n\n"
        f"📨 Sent:   `{sent}`\n"
        f"❌ Failed: `{failed}`",
        parse_mode=ParseMode.MARKDOWN)


# ════════════════════════════════════════════════════════════════════════════
#  CALLBACKS
# ════════════════════════════════════════════════════════════════════════════

async def callback_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data  = query.data
    uid   = query.from_user.id

    # ── Public ──────────────────────────────────────────────────────────
    if data == "leaderboard":
        await query.edit_message_text(referral.leaderboard_text(), parse_mode=ParseMode.MARKDOWN)
        return

    if data == "my_referral":
        referral.register_user(uid, query.from_user.username, query.from_user.first_name)
        await query.edit_message_text(referral.referral_card(uid), parse_mode=ParseMode.MARKDOWN)
        return

    # ── Admin only ───────────────────────────────────────────────────────
    if not is_admin(uid):
        await query.answer("⛔ Admin only", show_alert=True)
        return

    # Dashboard refresh
    if data == "dashboard":
        await show_dashboard(query, ctx, edit=True)

    elif data == "analytics":
        await refresh_members(ctx.application)
        await query.edit_message_text(analytics.full_report(), parse_mode=ParseMode.MARKDOWN)

    # ── Post Now ─────────────────────────────────────────────────────────
    elif data == "post_now":
        keyboard = [[InlineKeyboardButton(f"#{t}", callback_data=f"post_topic_{t}")] for t in cfg.TOPICS]
        keyboard.append([InlineKeyboardButton("🎲 Auto", callback_data="post_topic_AUTO")])
        keyboard.append([InlineKeyboardButton("« Back", callback_data="dashboard")])
        await query.edit_message_text("📝 *Choose topic (auto language):*",
            reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)

    elif data.startswith("post_topic_"):
        topic = data.replace("post_topic_", "")
        if topic == "AUTO": topic = engine.pick_topic()
        lang  = engine.pick_language()
        text  = engine.generate_post(topic, lang)
        await ctx.bot.send_message(chat_id=f"@{cfg.CHANNEL_USERNAME}",
            text=text, parse_mode=ParseMode.MARKDOWN)
        analytics.record_post(topic, lang)
        await query.edit_message_text(
            f"✅ *Posted!*\n\nTopic: #{topic}\nLang: {LANG_NAMES[lang]}\n\n_Tap /start to return to dashboard._",
            parse_mode=ParseMode.MARKDOWN)

    # ── Post by language ─────────────────────────────────────────────────
    elif data == "post_lang":
        keyboard = [
            [InlineKeyboardButton("🇬🇧 English",     callback_data="lang_en"),
             InlineKeyboardButton("🇪🇹 አማርኛ",       callback_data="lang_am")],
            [InlineKeyboardButton("🟢 Afaan Oromoo", callback_data="lang_orm")],
            [InlineKeyboardButton("« Back",          callback_data="dashboard")],
        ]
        await query.edit_message_text("🌍 *Choose language:*",
            reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)

    elif data.startswith("lang_"):
        lang = data.replace("lang_", "")
        keyboard = [[InlineKeyboardButton(f"#{t}", callback_data=f"postlang_{lang}_{t}")] for t in cfg.TOPICS]
        keyboard.append([InlineKeyboardButton("🎲 Auto", callback_data=f"postlang_{lang}_AUTO")])
        keyboard.append([InlineKeyboardButton("« Back", callback_data="post_lang")])
        await query.edit_message_text(f"📝 *{LANG_NAMES[lang]} — Choose topic:*",
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
            f"✅ *Posted!*\n\nTopic: #{topic}\nLang: {LANG_NAMES[lang]}\n\n_Tap /start to return to dashboard._",
            parse_mode=ParseMode.MARKDOWN)

    # ── Schedule ─────────────────────────────────────────────────────────
    elif data == "schedule":
        keyboard = [
            [InlineKeyboardButton("▶️ Resume", callback_data="sched_start"),
             InlineKeyboardButton("⏸ Pause",  callback_data="sched_pause")],
            [InlineKeyboardButton("🔄 Reset",  callback_data="sched_reset"),
             InlineKeyboardButton("« Back",    callback_data="dashboard")],
        ]
        await query.edit_message_text(sched.show_schedule(),
            reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)

    elif data == "sched_start":
        sched.resume()
        await query.edit_message_text("▶️ Scheduler *resumed*.\n\n_Tap /start for dashboard._",
            parse_mode=ParseMode.MARKDOWN)

    elif data == "sched_pause":
        sched.pause()
        await query.edit_message_text("⏸ Scheduler *paused*.\n\n_Tap /start for dashboard._",
            parse_mode=ParseMode.MARKDOWN)

    elif data == "sched_reset":
        sched.reset()
        await query.edit_message_text("🔄 Scheduler *reset*.\n\n_Tap /start for dashboard._",
            parse_mode=ParseMode.MARKDOWN)

    # ── Growth ───────────────────────────────────────────────────────────
    elif data == "growth":
        keyboard = [
            [InlineKeyboardButton("📣 Poll 🇬🇧",      callback_data="growth_poll_en"),
             InlineKeyboardButton("📣 Poll 🇪🇹",      callback_data="growth_poll_am")],
            [InlineKeyboardButton("📣 Poll 🟢",       callback_data="growth_poll_orm"),
             InlineKeyboardButton("🌍 Trilingual",    callback_data="growth_trilingual")],
            [InlineKeyboardButton("💬 Engage Post",   callback_data="growth_engage"),
             InlineKeyboardButton("🎁 Giveaway",      callback_data="growth_giveaway")],
            [InlineKeyboardButton("« Back",           callback_data="dashboard")],
        ]
        await query.edit_message_text("🌱 *Growth Tools:*",
            reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)

    elif data.startswith("growth_poll_"):
        lang = data.replace("growth_poll_", "")
        poll = growth.create_poll(lang)
        await ctx.bot.send_poll(chat_id=f"@{cfg.CHANNEL_USERNAME}",
            question=poll["question"], options=poll["options"], is_anonymous=True)
        await query.edit_message_text(
            f"📣 *Poll published!* {LANG_NAMES.get(lang,'')}\n\n_Tap /start for dashboard._",
            parse_mode=ParseMode.MARKDOWN)

    elif data == "growth_trilingual":
        await ctx.bot.send_message(chat_id=f"@{cfg.CHANNEL_USERNAME}",
            text=growth.create_trilingual_announcement(), parse_mode=ParseMode.MARKDOWN)
        await query.edit_message_text("🌍 *Trilingual post published!*\n\n_Tap /start for dashboard._",
            parse_mode=ParseMode.MARKDOWN)

    elif data == "growth_engage":
        await ctx.bot.send_message(chat_id=f"@{cfg.CHANNEL_USERNAME}",
            text=growth.create_engagement_post(), parse_mode=ParseMode.MARKDOWN)
        await query.edit_message_text("💬 *Engagement post published!*\n\n_Tap /start for dashboard._",
            parse_mode=ParseMode.MARKDOWN)

    elif data == "growth_giveaway":
        await ctx.bot.send_message(chat_id=f"@{cfg.CHANNEL_USERNAME}",
            text=growth.create_giveaway_post(), parse_mode=ParseMode.MARKDOWN)
        await query.edit_message_text("🎁 *Giveaway published!*\n\n_Tap /start for dashboard._",
            parse_mode=ParseMode.MARKDOWN)

    # ── Notify All ───────────────────────────────────────────────────────
    elif data == "notify_menu":
        keyboard = [
            [InlineKeyboardButton("📡 Channel Reminder", callback_data="bcast_reminder"),
             InlineKeyboardButton("🔗 Referral Promo",   callback_data="bcast_referral")],
            [InlineKeyboardButton("🆕 New Post + Notify",callback_data="bcast_newpost")],
            [InlineKeyboardButton("« Back",              callback_data="dashboard")],
        ]
        await query.edit_message_text(
            f"📢 *Notify All Subscribers*\n\n"
            f"👤 Registered: `{referral.total_users():,}` users\n\n"
            f"Choose message type:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN)

    elif data == "bcast_reminder":
        msg = (
            f"📡 *ZemenByte — Daily Tech Channel*\n\n"
            f"🇬🇧 Stay updated on AI, Crypto, Cybersecurity & more!\n"
            f"🇪🇹 ዕለታዊ የቴክ ዜናዎች!\n"
            f"🟢 Oduu teknooloojii guyyuu!\n\n"
            f"📲 Start our bot for personal notifications:\n"
            f"👉 t.me/ZemenByteBot\n\n"
            f"📡 Channel: t.me/{cfg.CHANNEL_USERNAME}"
        )
        await query.edit_message_text("📡 Broadcasting reminder...", parse_mode=ParseMode.MARKDOWN)
        # Post to channel first
        try:
            await ctx.bot.send_message(
                chat_id=f"@{cfg.CHANNEL_USERNAME}", text=msg, parse_mode=ParseMode.MARKDOWN)
        except Exception: pass
        # DM all registered users
        users = list(referral._data["users"].values())
        sent  = 0
        for u in users:
            try:
                await ctx.bot.send_message(chat_id=u["user_id"], text=msg, parse_mode=ParseMode.MARKDOWN)
                sent += 1
                await asyncio.sleep(0.05)
            except Exception: pass
        await query.edit_message_text(
            f"✅ Posted to channel + notified `{sent}` users!\n\n_Tap /start for dashboard._",
            parse_mode=ParseMode.MARKDOWN)

    elif data == "bcast_referral":
        msg = (
            "🔗 *ZemenByte Referral Program* 🎁\n\n"
            "Invite friends & earn points + badges!\n\n"
            "🏅 Badges: 🌱 Starter → ⭐ Rising Star → 🔥 Influencer → 💎 Diamond → 👑 Legend\n\n"
            "🇬🇧 Get your link → Start @ZemenByteBot → /referral\n"
            "🇪🇹 ሊንክ ውሰድ → @ZemenByteBot ጀምር → /referral\n"
            "🟢 Hidhata fudhadhu → @ZemenByteBot jalqabi → /referral\n\n"
            "🏆 Leaderboard → /leaderboard"
        )
        await query.edit_message_text("🔗 Broadcasting referral promo...", parse_mode=ParseMode.MARKDOWN)
        # Post to channel first
        try:
            await ctx.bot.send_message(
                chat_id=f"@{cfg.CHANNEL_USERNAME}", text=msg, parse_mode=ParseMode.MARKDOWN)
        except Exception: pass
        # DM all registered users
        users = list(referral._data["users"].values())
        sent  = 0
        for u in users:
            try:
                await ctx.bot.send_message(chat_id=u["user_id"], text=msg, parse_mode=ParseMode.MARKDOWN)
                sent += 1
                await asyncio.sleep(0.05)
            except Exception: pass
        await query.edit_message_text(
            f"✅ Posted to channel + notified `{sent}` users!\n\n_Tap /start for dashboard._",
            parse_mode=ParseMode.MARKDOWN)

    elif data == "bcast_newpost":
        topic = engine.pick_topic()
        lang  = engine.pick_language()
        text  = engine.generate_post(topic, lang)
        await ctx.bot.send_message(chat_id=f"@{cfg.CHANNEL_USERNAME}",
            text=text, parse_mode=ParseMode.MARKDOWN)
        analytics.record_post(topic, lang)
        await query.edit_message_text(f"📨 Notifying subscribers about #{topic}...",
            parse_mode=ParseMode.MARKDOWN)
        users = list(referral._data["users"].values())
        sent  = 0
        notif = (
            f"🔔 *New post on @{cfg.CHANNEL_USERNAME}!*\n\n"
            f"Topic: #{topic}\n"
            f"👉 t.me/{cfg.CHANNEL_USERNAME}"
        )
        for u in users:
            try:
                await ctx.bot.send_message(chat_id=u["user_id"], text=notif, parse_mode=ParseMode.MARKDOWN)
                sent += 1
                await asyncio.sleep(0.05)
            except Exception: pass
        await query.edit_message_text(
            f"✅ Posted #{topic} + notified `{sent}` subscribers!\n\n_Tap /start for dashboard._",
            parse_mode=ParseMode.MARKDOWN)

    # ── Referral stats ───────────────────────────────────────────────────
    elif data == "ref_stats":
        lb    = referral.leaderboard_text()
        extra = (
            f"\n\n📊 *System Stats*\n"
            f"👤 Registered: `{referral.total_users():,}`\n"
            f"🔗 Total referrals: `{referral.total_referrals():,}`"
        )
        keyboard = [[InlineKeyboardButton("« Back", callback_data="dashboard")]]
        await query.edit_message_text(lb + extra,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN)


# ════════════════════════════════════════════════════════════════════════════
#  SCHEDULED JOBS
# ════════════════════════════════════════════════════════════════════════════

async def auto_post_job(ctx: ContextTypes.DEFAULT_TYPE):
    if not sched.is_running: return
    topic = engine.pick_topic()
    lang  = engine.pick_language()
    try:
        text = engine.generate_post(topic, lang)
        await ctx.bot.send_message(chat_id=f"@{cfg.CHANNEL_USERNAME}",
            text=text, parse_mode=ParseMode.MARKDOWN)
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
    lb     = referral.get_leaderboard(3)
    medals = ["🥇","🥈","🥉"]
    top    = "\n".join(
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



async def cmd_remind(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Post channel reminder to channel + DM all bot users."""
    if not is_admin(update.effective_user.id): return
    msg = (
        f"📡 *ZemenByte — Daily Tech Channel*\n\n"
        f"🇬🇧 AI, Crypto, Cybersecurity & more — every day!\n"
        f"🇪🇹 ዕለታዊ የቴክ ዜናዎች!\n"
        f"🟢 Oduu teknooloojii guyyuu!\n\n"
        f"📲 Personal notifications → Start @ZemenByteBot\n"
        f"📡 Channel → t.me/{cfg.CHANNEL_USERNAME}"
    )
    # Post to channel
    await ctx.bot.send_message(
        chat_id=f"@{cfg.CHANNEL_USERNAME}",
        text=msg, parse_mode=ParseMode.MARKDOWN)
    # Broadcast to bot users
    await _broadcast(ctx, update.message, msg)


async def cmd_referral_promo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Post referral promo to channel + DM all bot users."""
    if not is_admin(update.effective_user.id): return
    msg = (
        "🔗 *ZemenByte Referral Program* 🎁\n\n"
        "Invite friends & earn points + badges!\n\n"
        "🏅 *Badge Levels:*\n"
        "🌱 1 invite → Starter\n"
        "⭐ 5 invites → Rising Star\n"
        "🔥 10 invites → Influencer\n"
        "💎 25 invites → Diamond\n"
        "👑 50 invites → ZemenByte Legend\n\n"
        "🇬🇧 Start @ZemenByteBot → /referral\n"
        "🇪🇹 @ZemenByteBot ጀምር → /referral\n"
        "🟢 @ZemenByteBot jalqabi → /referral\n\n"
        "🏆 See top inviters → /leaderboard"
    )
    # Post to channel
    await ctx.bot.send_message(
        chat_id=f"@{cfg.CHANNEL_USERNAME}",
        text=msg, parse_mode=ParseMode.MARKDOWN)
    # Broadcast to bot users
    await _broadcast(ctx, update.message, msg)

def main():
    token = cfg.BOT_TOKEN
    if not token or token == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ Set TELEGRAM_BOT_TOKEN")
        return

    app = Application.builder().token(token).build()

    # Public
    app.add_handler(CommandHandler("start",       start))
    app.add_handler(CommandHandler("referral",    cmd_referral))
    app.add_handler(CommandHandler("leaderboard", cmd_leaderboard))
    app.add_handler(CommandHandler("mystats",     cmd_mystats))

    # Admin
    app.add_handler(CommandHandler("post",        cmd_post))
    app.add_handler(CommandHandler("stats",       cmd_stats))
    app.add_handler(CommandHandler("schedule",    cmd_schedule))
    app.add_handler(CommandHandler("notify",      cmd_notify))
    app.add_handler(CommandHandler("remind",      cmd_remind))
    app.add_handler(CommandHandler("refpromo",    cmd_referral_promo))
    app.add_handler(CommandHandler("preview",     cmd_preview))

    app.add_handler(CallbackQueryHandler(callback_handler))

    jq: JobQueue = app.job_queue
    jq.run_repeating(auto_post_job,         interval=int(86400/cfg.POSTS_PER_DAY), first=30)
    jq.run_repeating(refresh_members_job,   interval=3600,  first=10)
    jq.run_daily(daily_summary_job,         time=dtime(23, 55))
    jq.run_daily(weekly_engagement_job,     time=dtime(10, 0), days=(0,))
    jq.run_daily(weekly_referral_reminder,  time=dtime(18, 0), days=(2,))

    # Capture event loop and start dashboard server
    async def post_init(application):
        import server
        loop = asyncio.get_running_loop()
        server.start(analytics, sched, engine, growth, referral, application, cfg, loop)
        logger.info("✅ Dashboard server started")

    app.post_init = post_init

    logger.info("🚀 ZemenByte bot started — pure bot + dashboard mode!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
