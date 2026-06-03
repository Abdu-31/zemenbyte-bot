"""
growth_engine.py — Organic growth tools for ZemenByte
"""

import random
from config import Config


POLLS = [
    {
        "question": "Which tech field excites you most in 2025?",
        "options": ["🤖 Artificial Intelligence", "⚛️ Quantum Computing", "🔐 Cybersecurity", "₿ Crypto/Web3"]
    },
    {
        "question": "What's the biggest threat to digital privacy?",
        "options": ["🏛 Governments", "🏢 Big Tech", "🤖 AI systems", "🦹 Cybercriminals"]
    },
    {
        "question": "How many hours/day do you consume tech news?",
        "options": ["< 30 mins", "30–60 mins", "1–2 hours", "3+ hours"]
    },
    {
        "question": "Which will happen first?",
        "options": ["🧠 AGI achieved", "⚛️ Quantum supremacy", "🚗 Full self-driving", "🌕 Moon base"]
    },
    {
        "question": "Best way to learn about AI trends?",
        "options": ["📱 Telegram channels", "🐦 Twitter/X", "📚 Research papers", "🎙 Podcasts"]
    },
    {
        "question": "Are you bullish on crypto in 2025?",
        "options": ["🚀 Super bullish", "📈 Mildly bullish", "😐 Neutral", "🐻 Bearish"]
    },
    {
        "question": "What skill will matter most in 5 years?",
        "options": ["🤖 AI/ML engineering", "🔐 Cybersecurity", "⛓ Blockchain dev", "🧬 Biotech"]
    },
]

ENGAGEMENT_POSTS = [
    (
        "💬 *LET'S DEBATE:*\n\n"
        "AI will make software engineers obsolete within 10 years.\n\n"
        "🟢 Agree | 🔴 Disagree\n\n"
        "Drop your take below 👇 and tag a developer friend!\n\n"
        "#AI #SoftwareEngineering #FutureOfWork #ZemenByte"
    ),
    (
        "🤔 *THOUGHT OF THE DAY:*\n\n"
        "If you could have ONE superpower from technology right now, what would it be?\n\n"
        "• 🧠 Brain-computer interface\n"
        "• ⚛️ Quantum computation\n"
        "• 🔐 Unhackable security\n"
        "• 🤖 Personal AI assistant\n\n"
        "Comment below! 👇\n\n"
        "#TechSuperpower #Innovation #ZemenByte"
    ),
    (
        "📣 *SHARE YOUR KNOWLEDGE:*\n\n"
        "What's one tech tip or trick that changed how you work?\n\n"
        "Share it below — let's build a thread of pure value! 🧵\n\n"
        "#TechTips #Productivity #LearnFromEachOther #ZemenByte"
    ),
    (
        "🌍 *GLOBAL TECH COMMUNITY*\n\n"
        "Where are you reading this from? 📍\n\n"
        "Drop your country flag in the comments!\n"
        "Let's see how global our ZemenByte community really is 🌐\n\n"
        "#GlobalTech #Community #ZemenByte"
    ),
]

GIVEAWAY_TEMPLATES = [
    (
        "🎁 *GIVEAWAY — ZemenByte Community Reward*\n\n"
        "We're celebrating our growing community with a giveaway!\n\n"
        "🏆 *Prize:* [Your Prize Here]\n\n"
        "✅ *How to enter:*\n"
        "1️⃣ Follow @ZemenByte\n"
        "2️⃣ Share this post with 2 friends\n"
        "3️⃣ Comment your favorite tech topic\n\n"
        "⏰ Ends in 48 hours. Winner announced here!\n\n"
        "Good luck! 🍀\n\n"
        "#Giveaway #ZemenByte #TechCommunity"
    ),
]

PUSH_NOTIFICATIONS = [
    (
        "🔔 *HEY ZemenByte FAM!*\n\n"
        "Big content drop incoming this week! 🚀\n\n"
        "Make sure notifications are ON so you don't miss:\n"
        "• Deep-dive AI analysis\n"
        "• Crypto market insights\n"
        "• Cybersecurity alerts\n"
        "• Quantum computing breakthroughs\n\n"
        "Tap the 🔔 icon at the top of the channel to enable alerts!\n\n"
        "#ZemenByte #TechNews #StayInformed"
    ),
    (
        "📢 *CHANNEL UPDATE*\n\n"
        "Thank you for being part of the ZemenByte community! 🙏\n\n"
        "We post daily insights on:\n"
        "🤖 AI • ₿ Crypto • 🔐 Cyber • ⚛️ Quantum • 💡 Innovation • 💻 Tech\n\n"
        "Share this channel with someone who loves tech! 🔁\n\n"
        "#ZemenByte #ShareKnowledge"
    ),
]


class GrowthEngine:
    def __init__(self, cfg: Config):
        self.cfg = cfg

    def create_poll(self) -> dict:
        return random.choice(POLLS)

    def create_engagement_post(self) -> str:
        return random.choice(ENGAGEMENT_POSTS)

    def create_giveaway_post(self) -> str:
        return random.choice(GIVEAWAY_TEMPLATES)

    def create_push_notification(self) -> str:
        return random.choice(PUSH_NOTIFICATIONS)

    def create_milestone_post(self, members: int) -> str:
        return (
            f"🎉 *WE HIT {members:,} MEMBERS!*\n\n"
            f"This is only the beginning. 🚀\n\n"
            f"Thank you to every single member of the ZemenByte community "
            f"for being part of this journey.\n\n"
            f"More exclusive content, deeper insights, and bigger surprises ahead.\n\n"
            f"Share this channel with a friend who deserves to stay ahead of tech! 👇\n\n"
            f"#ZemenByte #Milestone #TechCommunity #ThankYou"
        )

    def create_collab_message(self, channel_name: str) -> str:
        return (
            f"👋 Hey @{channel_name} team!\n\n"
            f"I run *ZemenByte* — a daily tech channel covering AI, Crypto, "
            f"Cybersecurity, Quantum Computing, and Innovation.\n\n"
            f"I'd love to explore a cross-promotion or content collaboration. "
            f"Our communities would likely overlap well!\n\n"
            f"Would you be open to a quick chat? 🙏"
        )


# ── Trilingual polls ──────────────────────────────────────────────────────

POLLS_AM = [
    {
        "question": "በ2025 በጣም የሚያስደስትህ የቴክ ዘርፍ የቱ ነው?",
        "options": ["🤖 AI", "⚛️ ኳንተም ኮምፒዩቲንግ", "🔐 ሳይበር ደህንነት", "₿ ክሪፕቶ/Web3"]
    },
    {
        "question": "ቴክኖሎጂ ኢትዮጵያን ሊቀይር ይችላል ብለህ ታምናለህ?",
        "options": ["✅ አዎ፣ ሙሉ በሙሉ", "🤔 ከፊሉ", "⏳ ጊዜ ይፈጃል", "❌ አይቀይርም"]
    },
    {
        "question": "AI የሰዎችን ሥራ ይወስዳል?",
        "options": ["✅ አዎ፣ ብዙ ሥራ", "🔄 አዲስ ሥራ ይፈጥራል", "😐 ምናልባት", "❌ አይወስድም"]
    },
]

POLLS_ORM = [
    {
        "question": "Damee teknooloojii kami bara 2025 si hawwata?",
        "options": ["🤖 AI", "⚛️ Kwantamii", "🔐 Nageenyaa Saayibarii", "₿ Crypto/Web3"]
    },
    {
        "question": "Teknooloojiin Oromiyaa ni jijjiiraa?",
        "options": ["✅ Eeyyee, guutummaatti", "🤔 Gara tokkoon", "⏳ Yeroo fudhata", "❌ Hin jijjiiru"]
    },
]


class GrowthEngineMultilingual(GrowthEngine):
    """Extended growth engine with multilingual support."""

    def create_poll(self, lang: str = None) -> dict:
        import random as _random
        if lang == "am":
            return _random.choice(POLLS_AM)
        elif lang == "orm":
            return _random.choice(POLLS_ORM)
        # Default: mix languages randomly
        all_polls = POLLS + POLLS_AM + POLLS_ORM
        return _random.choice(all_polls)

    def create_trilingual_announcement(self) -> str:
        return (
            "📢 *ZemenByte Channel Announcement*\n\n"
            "🇬🇧 *English:* Daily tech insights on AI, Crypto, Cybersecurity & more!\n\n"
            "🇪🇹 *አማርኛ:* በቴክኖሎጂ፣ AI፣ ክሪፕቶ እና የሳይበር ደህንነት ላይ ዕለታዊ ዜናዎችን እናቀርባለን!\n\n"
            "🟢 *Afaan Oromoo:* Oduu teknooloojii, AI, Crypto fi nageenyaa saayibarii guyyuu!\n\n"
            "📡 Follow @ZemenByte | ZemenByte hordofaa | ZemenByte hordofaa\n\n"
            "#ZemenByte #Ethiopia #Oromia #Technology"
        )
