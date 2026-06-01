# 🤖 ZemenByte Telegram Bot

> **Automated channel management, daily posting, and organic growth for @ZemenByte**

---

## 🚀 Features

| Feature | Description |
|---|---|
| ⏰ **Auto-Posting** | Publishes 6 posts/day on a configurable schedule |
| 🧠 **Smart Content** | Rich, on-brand posts for AI, Crypto, Cyber, Quantum, Innovation, Tech |
| 📊 **Analytics** | Tracks posts, topics, views, and member growth |
| 🌱 **Growth Engine** | Polls, engagement posts, giveaways, push notifications |
| 📅 **Weekly Series** | Monday Motivation, Wednesday Deep Dive, Friday Roundup |
| 🎛 **Admin Dashboard** | Full control panel via inline keyboard |
| 🔔 **Daily Summary** | Automated end-of-day report to admins |

---

## 📦 Setup (5 minutes)

### 1. Create your bot

1. Open Telegram → message **@BotFather**
2. Send `/newbot` and follow prompts
3. Copy your **Bot Token**

### 2. Get your Channel & Admin IDs

- **Channel username**: e.g. `ZemenByte` (without @)
- **Your admin ID**: message @userinfobot to get your numeric ID

### 3. Make your bot an admin

1. Go to your channel settings
2. Administrators → Add Administrator
3. Search your bot's name
4. Grant: Post Messages, Edit Messages, Delete Messages

### 4. Install & configure

```bash
# Clone / download the bot files
cd zemenbyte_bot

# Install dependencies
pip install -r requirements.txt

# Set environment variables (recommended)
export TELEGRAM_BOT_TOKEN="7123456789:AAF..."
export CHANNEL_USERNAME="ZemenByte"
export ADMIN_IDS="123456789"          # Your numeric Telegram ID
export POSTS_PER_DAY="6"

# OR edit config.py directly
```

### 5. Run the bot

```bash
python bot.py
```

---

## ⚙️ Configuration (`config.py`)

| Variable | Default | Description |
|---|---|---|
| `BOT_TOKEN` | required | Telegram bot token from @BotFather |
| `CHANNEL_USERNAME` | `ZemenByte` | Channel username (no @) |
| `ADMIN_IDS` | required | Comma-separated admin user IDs |
| `POSTS_PER_DAY` | `6` | Number of auto-posts per day |
| `POST_HOURS` | 7,10,13,16,19,22 | Preferred UTC posting hours |
| `USE_EMOJIS` | `True` | Add emojis to posts |
| `USE_HASHTAGS` | `True` | Add hashtags to posts |

---

## 🎛 Admin Commands

| Command | Description |
|---|---|
| `/start` | Open admin dashboard |
| `/post` | Manually trigger a post (pick topic) |
| `/stats` | View full analytics report |
| `/schedule` | View & control posting schedule |
| `/growth` | Access growth tools |
| `/preview` | Preview next auto-post |

---

## 📅 Auto-Post Schedule

The bot posts **6 times per day** by default (~every 4 hours), rotating across topics:

| Topic | Frequency |
|---|---|
| 🤖 AI | 25% |
| ₿ Crypto | 20% |
| 🔐 Cybersecurity | 20% |
| 💡 Innovation | 15% |
| 💻 Tech | 10% |
| ⚛️ Quantum Computing | 10% |

**Special posts:**
- 🗓 Monday Motivation (weekly)
- 🔍 Wednesday Deep Dive (weekly)
- 🎉 Friday Roundup (weekly)

---

## 🌱 Growth Tools

### Polls
Engagement-driving polls published to the channel. 7 built-in templates covering tech opinions, crypto sentiment, and more.

### Engagement Posts
Discussion starters that invite comments, debates, and shares.

### Giveaways
Templated giveaway posts to boost shares and followers.

### Push Notifications
Periodic reminders for members to enable notifications.

### Milestones
Automated celebration posts when member counts hit milestones.

---

## 📊 Analytics

The bot tracks locally:
- Total posts published
- Posts by topic
- Daily post counts
- 7-day average

For real-time member stats, integrate the Telegram Bot API's `getChatMembersCount` endpoint (call `analytics.update_channel_stats()` in a periodic job).

---

## 🔧 Running 24/7 (Production)

### Option A: systemd (Linux VPS)

```ini
# /etc/systemd/system/zemenbyte.service
[Unit]
Description=ZemenByte Telegram Bot
After=network.target

[Service]
WorkingDirectory=/opt/zemenbyte_bot
ExecStart=/usr/bin/python3 bot.py
Restart=always
RestartSec=10
Environment="TELEGRAM_BOT_TOKEN=your_token"
Environment="CHANNEL_USERNAME=ZemenByte"
Environment="ADMIN_IDS=123456789"

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable zemenbyte
sudo systemctl start zemenbyte
sudo systemctl status zemenbyte
```

### Option B: Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "bot.py"]
```

```bash
docker build -t zemenbyte-bot .
docker run -d \
  -e TELEGRAM_BOT_TOKEN=your_token \
  -e CHANNEL_USERNAME=ZemenByte \
  -e ADMIN_IDS=123456789 \
  --name zemenbyte \
  --restart unless-stopped \
  zemenbyte-bot
```

### Option C: Railway / Render / Fly.io
Set environment variables in dashboard and deploy directly.

---

## 📁 File Structure

```
zemenbyte_bot/
├── bot.py              # Main bot entry point
├── config.py           # Configuration
├── content_engine.py   # Post generation & templates
├── scheduler.py        # Schedule management
├── analytics.py        # Analytics tracking
├── growth_engine.py    # Growth tools (polls, giveaways, etc.)
├── requirements.txt    # Python dependencies
├── README.md           # This file
├── analytics_data.json # Auto-created: analytics store
├── schedule_state.json # Auto-created: scheduler state
└── zemenbyte.log       # Auto-created: bot logs
```

---

## 💡 Tips for Organic Growth

1. **Post consistently** — 4–6x/day at peak hours (7–9am, 12–2pm, 6–9pm local time)
2. **Use polls** — 3x higher engagement than plain text posts
3. **Trending topics** — monitor Twitter/X for breaking AI/crypto news and post within 1 hour
4. **Cross-promote** — message similar channels for shoutout exchanges
5. **Pin important posts** — keep your best content visible to new members
6. **Engage comments** — reply to comments to boost algorithm visibility
7. **Milestone posts** — celebrate every 1000 new members

---

*Built for @ZemenByte | ZemenByte Telegram Bot v1.0*
