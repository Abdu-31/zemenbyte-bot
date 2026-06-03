"""
growth_engine.py — Trilingual Growth Engine for ZemenByte
"""
import random
from config import Config

# ── English polls ─────────────────────────────────────────────────────────
POLLS_EN = [
    {"question": "Which tech field excites you most in 2025?",
     "options": ["🤖 AI", "⚛️ Quantum Computing", "🔐 Cybersecurity", "₿ Crypto/Web3"]},
    {"question": "What's the biggest threat to digital privacy?",
     "options": ["🏛 Governments", "🏢 Big Tech", "🤖 AI systems", "🦹 Cybercriminals"]},
    {"question": "Will AI replace most jobs in 10 years?",
     "options": ["✅ Yes, definitely", "🔄 It will create new ones", "😐 Partially", "❌ No"]},
    {"question": "Are you bullish on crypto in 2025?",
     "options": ["🚀 Super bullish", "📈 Mildly bullish", "😐 Neutral", "🐻 Bearish"]},
    {"question": "Best way to learn about AI trends?",
     "options": ["📱 Telegram channels", "🐦 Twitter/X", "📚 Research papers", "🎙 Podcasts"]},
    {"question": "Which will happen first?",
     "options": ["🧠 AGI achieved", "⚛️ Quantum supremacy", "🚗 Full self-driving", "🌕 Moon base"]},
]

# ── Amharic polls ─────────────────────────────────────────────────────────
POLLS_AM = [
    {"question": "በ2025 በጣም የሚያስደስትህ የቴክ ዘርፍ የቱ ነው?",
     "options": ["🤖 AI", "⚛️ ኳንተም ኮምፒዩቲንግ", "🔐 ሳይበር ደህንነት", "₿ ክሪፕቶ/Web3"]},
    {"question": "ቴክኖሎጂ ኢትዮጵያን ሊቀይር ይችላል ብለህ ታምናለህ?",
     "options": ["✅ አዎ፣ ሙሉ በሙሉ", "🤔 ከፊሉ ብቻ", "⏳ ጊዜ ይፈጃል", "❌ አይቀይርም"]},
    {"question": "AI የሰዎችን ሥራ ይወስዳል?",
     "options": ["✅ አዎ፣ ብዙ ሥራ", "🔄 አዲስ ሥራ ይፈጥራል", "😐 ምናልባት", "❌ አይወስድም"]},
    {"question": "ዲጂታል ፋይናንስ ኢትዮጵያ ውስጥ ይዳብራል?",
     "options": ["🚀 በጣም ፈጥኖ", "📈 ቀስ ብሎ", "😐 ምናልባት", "❌ አይሆንም"]},
    {"question": "ቁጥር አንድ የሳይበር ደህንነት ልምድህ ምንድን ነው?",
     "options": ["🔐 የ암호 አስተዳዳሪ", "📱 2FA", "🛡️ VPN", "🔄 ሶፍትዌር ማዘመን"]},
]

# ── Afaan Oromoo polls ────────────────────────────────────────────────────
POLLS_ORM = [
    {"question": "Damee teknooloojii kami bara 2025 si hawwata?",
     "options": ["🤖 AI", "⚛️ Kwantamii", "🔐 Nageenyaa Saayibarii", "₿ Crypto/Web3"]},
    {"question": "Teknooloojiin Oromiyaa ni jijjiiraa?",
     "options": ["✅ Eeyyee, guutummaatti", "🤔 Gara tokkoon", "⏳ Yeroo fudhata", "❌ Hin jijjiiru"]},
    {"question": "AI hojiiwwan namaa ni fudhata?",
     "options": ["✅ Eeyyee hedduu", "🔄 Haaraa uuma", "😐 Gara tokkoon", "❌ Hin fudhatu"]},
    {"question": "Maallaqni dijitaalaa Itoophiyaa keessatti ni babal'ata?",
     "options": ["🚀 Baay'ee saffisaan", "📈 Gara tokkoon", "😐 Lakkii", "❌ Hin babal'atu"]},
]

# ── Engagement posts ──────────────────────────────────────────────────────
ENGAGEMENT_POSTS = [
    (
        "💬 *LET'S DEBATE:*\n\n"
        "AI will make software engineers obsolete within 10 years.\n\n"
        "🟢 Agree | 🔴 Disagree\n\n"
        "Drop your take below 👇\n\n"
        "#AI #FutureOfWork #ZemenByte"
    ),
    (
        "🤔 *THOUGHT OF THE DAY:*\n\n"
        "If you could have ONE tech superpower right now, what would it be?\n\n"
        "• 🧠 Brain-computer interface\n"
        "• ⚛️ Quantum computation\n"
        "• 🔐 Unhackable security\n"
        "• 🤖 Personal AI assistant\n\n"
        "Comment below! 👇\n\n"
        "#TechSuperpower #ZemenByte"
    ),
    (
        "🌍 *GLOBAL TECH COMMUNITY*\n\n"
        "Where are you reading this from? 📍\n\n"
        "Drop your country flag! 🇪🇹🇺🇸🇬🇧🇩🇪🇮🇳\n\n"
        "#GlobalTech #ZemenByte"
    ),
    (
        "🗣️ *ለዚህ ጥያቄ ምላሽ ስጥ:*\n\n"
        "ቴክኖሎጂ ኢትዮጵያን ሊቀይር ይችላል ብለህ ታምናለህ?\n\n"
        "✅ አዎ | ❌ አይቀይርም\n\n"
        "አስተያየትህን ፃፍ! 👇\n\n"
        "#ቴክኖሎጂ #ኢትዮጵያ #ZemenByte"
    ),
    (
        "💬 *Marii:*\n\n"
        "Teknooloojiin Oromiyaa ni jijjiiraa?\n\n"
        "✅ Eeyyee | ❌ Hin jijjiiru\n\n"
        "Yaada kee barreessi! 👇\n\n"
        "#Teknooloojii #Oromiyaa #ZemenByte"
    ),
]

GIVEAWAY_TEMPLATES = [
    (
        "🎁 *GIVEAWAY — ZemenByte Community*\n\n"
        "We're celebrating our growing community!\n\n"
        "🏆 Prize: [Your Prize Here]\n\n"
        "✅ To enter:\n"
        "1️⃣ Follow @ZemenByte\n"
        "2️⃣ Share with 2 friends\n"
        "3️⃣ Comment your favorite tech topic\n\n"
        "⏰ Ends in 48 hours!\n\n"
        "#Giveaway #ZemenByte"
    ),
]

PUSH_NOTIFICATIONS = [
    (
        "🔔 *HEY ZemenByte FAM!*\n\n"
        "Big content drop this week! 🚀\n\n"
        "🇬🇧 Enable notifications to stay updated!\n"
        "🇪🇹 ጥሩ ይዘት እያዘጋጀን ነን — ማሳወቂያ አንቃ!\n"
        "🟢 Ergaa haaraa dhufaa jira — beeksisa cufuu hin qabdu!\n\n"
        "#ZemenByte"
    ),
]


class GrowthEngine:
    def __init__(self, cfg: Config):
        self.cfg = cfg

    def create_poll(self, lang: str = None) -> dict:
        """Return a poll in the given language, or random language if None."""
        if lang == "am":
            return random.choice(POLLS_AM)
        elif lang == "orm":
            return random.choice(POLLS_ORM)
        elif lang == "en":
            return random.choice(POLLS_EN)
        # Random mix
        all_polls = POLLS_EN + POLLS_AM + POLLS_ORM
        return random.choice(all_polls)

    def create_engagement_post(self) -> str:
        return random.choice(ENGAGEMENT_POSTS)

    def create_giveaway_post(self) -> str:
        return random.choice(GIVEAWAY_TEMPLATES)

    def create_push_notification(self) -> str:
        return random.choice(PUSH_NOTIFICATIONS)

    def create_trilingual_announcement(self) -> str:
        return (
            "📢 *ZemenByte — Daily Tech for Everyone*\n\n"
            "🇬🇧 *English:* Daily insights on AI, Crypto, Cybersecurity, Quantum & Innovation!\n\n"
            "🇪🇹 *አማርኛ:* በ AI፣ ክሪፕቶ፣ ሳይበር ደህንነት እና ፈጠራ ላይ ዕለታዊ ዜናዎች!\n\n"
            "🟢 *Afaan Oromoo:* Oduu AI, Crypto, Nageenyaa Saayibarii fi Argannoo Guyyuu!\n\n"
            "📡 Follow @ZemenByte\n\n"
            "#ZemenByte #Ethiopia #Oromia #Technology #AI"
        )

    def create_milestone_post(self, members: int) -> str:
        return (
            f"🎉 *WE HIT {members:,} MEMBERS!*\n\n"
            f"🇬🇧 Thank you to every member of the ZemenByte community!\n"
            f"🇪🇹 ለZemenByte ቤተሰብ ሁሉ እናመሰግናለን!\n"
            f"🟢 Miseensota ZemenByte hundaaf galata!\n\n"
            f"Share @ZemenByte with a friend! 🚀\n\n"
            f"#ZemenByte #Milestone"
        )
