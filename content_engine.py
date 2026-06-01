"""
content_engine.py — ZemenByte Content Engine
Generates rich, on-brand posts for every topic.
"""

import random
from datetime import datetime
from typing import Optional
from config import Config


# ════════════════════════════════════════════════════════════════════════════
#  POST TEMPLATES (curated, varied, on-brand for ZemenByte)
# ════════════════════════════════════════════════════════════════════════════

POSTS = {
    "AI": [
        (
            "🤖 *AI INSIGHT OF THE DAY*\n\n"
            "Large Language Models are evolving beyond text generation — they're now reasoning "
            "agents capable of multi-step planning, code execution, and real-time web access.\n\n"
            "🔮 *What's next?* Autonomous AI agents that can manage complex workflows end-to-end "
            "without human intervention.\n\n"
            "💡 The question is no longer *'Can AI do this?'* — it's *'Should we let it?'*\n\n"
            "📌 Which AI advancement excites you the most? Drop a comment! 👇\n\n"
            "#AI #ArtificialIntelligence #LLM #MachineLearning #ZemenByte"
        ),
        (
            "⚡ *BREAKING: AI RESHAPING INDUSTRIES*\n\n"
            "From healthcare diagnostics to financial modeling — AI is no longer a future concept. "
            "It's the present reality.\n\n"
            "📊 *Key Stats:*\n"
            "• 77% of devices use AI in some form\n"
            "• AI market projected at $1.8T by 2030\n"
            "• 300M jobs will be impacted globally\n\n"
            "🧠 Stay informed. Stay ahead.\n\n"
            "#AITrends #FutureOfWork #TechNews #Innovation #ZemenByte"
        ),
        (
            "🧬 *AI × SCIENCE = UNSTOPPABLE*\n\n"
            "AlphaFold predicted protein structures for virtually every known protein.\n"
            "AI is now designing new drugs in *days* instead of years.\n\n"
            "🔬 The merger of AI and biology is one of the most profound shifts in human history.\n\n"
            "Are we entering a golden age of science? 🌟\n\n"
            "#AI #Biotech #AlphaFold #DrugDiscovery #ZemenByte"
        ),
        (
            "🚀 *GENERATIVE AI: WHERE WE'RE HEADED*\n\n"
            "Multimodal AI — understanding text, images, audio, and video simultaneously — "
            "is becoming the new standard.\n\n"
            "👁️ Models that *see*, *hear*, and *reason* simultaneously will transform:\n"
            "• Education 📚\n"
            "• Entertainment 🎬\n"
            "• Productivity 💼\n"
            "• Healthcare 🏥\n\n"
            "The AI revolution is just getting started.\n\n"
            "#GenerativeAI #Multimodal #GPT #Gemini #Claude #ZemenByte"
        ),
        (
            "💀 *AI ETHICS: THE DEBATE WE CAN'T IGNORE*\n\n"
            "As AI grows more powerful, questions of bias, transparency, and accountability "
            "become critical.\n\n"
            "⚖️ Key concerns:\n"
            "• Deepfakes & misinformation\n"
            "• Algorithmic bias in hiring/lending\n"
            "• AI in warfare & surveillance\n"
            "• Job displacement without safety nets\n\n"
            "💬 What ethical AI principle matters most to you?\n\n"
            "#AIEthics #ResponsibleAI #TechPolicy #ZemenByte"
        ),
    ],

    "Crypto": [
        (
            "📈 *CRYPTO MARKET PULSE*\n\n"
            "The crypto market never sleeps — and neither should your knowledge.\n\n"
            "🔑 *Key Concepts Every Crypto Holder Should Know:*\n"
            "• DeFi (Decentralized Finance)\n"
            "• Layer 2 scaling solutions\n"
            "• Liquid staking\n"
            "• Real-World Assets (RWA) on-chain\n\n"
            "💡 The next bull cycle will be driven by *utility*, not hype.\n\n"
            "#Crypto #Bitcoin #Ethereum #DeFi #Web3 #ZemenByte"
        ),
        (
            "₿ *BITCOIN: DIGITAL GOLD OR GLOBAL CURRENCY?*\n\n"
            "Bitcoin has survived bear markets, bans, and FUD for over 15 years.\n\n"
            "📌 *Why Bitcoin remains relevant:*\n"
            "✅ Fixed supply of 21 million\n"
            "✅ Fully decentralized\n"
            "✅ Nation-state level adoption\n"
            "✅ Hedge against inflation\n\n"
            "🌍 El Salvador, ETF approvals, and institutional stacking — BTC isn't going away.\n\n"
            "#Bitcoin #BTC #CryptoNews #HODL #ZemenByte"
        ),
        (
            "🔗 *WEB3: THE INTERNET REVOLUTION*\n\n"
            "Web1: Read\nWeb2: Read + Write\nWeb3: Read + Write + *Own*\n\n"
            "Blockchain-based ownership changes everything:\n"
            "• Your data is *yours*\n"
            "• Payments without banks\n"
            "• DAOs replacing corporations\n\n"
            "🏗️ We're building the infrastructure of the next digital economy.\n\n"
            "#Web3 #Blockchain #DeFi #DAO #Crypto #ZemenByte"
        ),
        (
            "⚠️ *CRYPTO SAFETY TIPS — DON'T GET REKT*\n\n"
            "Billions are lost to scams and hacks every year in crypto.\n\n"
            "🛡️ *Protect yourself:*\n"
            "🔐 Use a hardware wallet (Ledger, Trezor)\n"
            "🚫 Never share your seed phrase — EVER\n"
            "👀 Verify contract addresses on block explorers\n"
            "📧 Enable 2FA on all exchanges\n"
            "🕵️ Research before you ape in\n\n"
            "Stay safe out there, frens. 💪\n\n"
            "#CryptoSecurity #DYOR #Blockchain #ZemenByte"
        ),
    ],

    "Cybersecurity": [
        (
            "🔐 *CYBERSECURITY ALERT*\n\n"
            "Ransomware attacks increased by 95% last year — and no one is immune.\n\n"
            "🏢 Targets include:\n"
            "• Hospitals & healthcare systems\n"
            "• Critical infrastructure\n"
            "• SMEs and startups\n"
            "• Government agencies\n\n"
            "🛡️ *Your defense starts with awareness.*\n\n"
            "What's your #1 cybersecurity practice? Let us know! 👇\n\n"
            "#Cybersecurity #Ransomware #InfoSec #CyberDefense #ZemenByte"
        ),
        (
            "👁️ *ZERO TRUST: THE NEW SECURITY MODEL*\n\n"
            "Old model: *Trust but verify*\n"
            "Zero Trust model: *Never trust, always verify*\n\n"
            "In a world of remote work and cloud-first architecture, the perimeter is gone.\n\n"
            "🔑 Zero Trust pillars:\n"
            "• Verify every user & device\n"
            "• Least privilege access\n"
            "• Micro-segmentation\n"
            "• Continuous monitoring\n\n"
            "#ZeroTrust #CyberSecurity #CloudSecurity #InfoSec #ZemenByte"
        ),
        (
            "🤖 *AI-POWERED CYBERATTACKS ARE HERE*\n\n"
            "Hackers are now using AI to:\n"
            "• Generate convincing phishing emails\n"
            "• Automate vulnerability scanning\n"
            "• Bypass traditional security tools\n"
            "• Craft polymorphic malware\n\n"
            "⚔️ The arms race between AI attackers and AI defenders is on.\n\n"
            "Is your organization prepared?\n\n"
            "#AICyberSecurity #Phishing #Malware #CyberDefense #ZemenByte"
        ),
        (
            "🔑 *PASSWORD HYGIENE 101*\n\n"
            "Still using 'Password123'? 🚨\n\n"
            "✅ Use a password manager (Bitwarden, 1Password)\n"
            "✅ Enable MFA everywhere\n"
            "✅ Use passkeys where available\n"
            "✅ Never reuse passwords\n"
            "✅ Check HaveIBeenPwned.com regularly\n\n"
            "Your accounts are only as strong as your weakest password.\n\n"
            "#PasswordSecurity #MFA #CyberHygiene #InfoSec #ZemenByte"
        ),
    ],

    "Quantum": [
        (
            "⚛️ *QUANTUM COMPUTING: THE NEXT FRONTIER*\n\n"
            "Classical computers use bits (0 or 1).\n"
            "Quantum computers use *qubits* — which can be 0, 1, or *both simultaneously*.\n\n"
            "🌀 This superposition enables exponentially faster computation for:\n"
            "• Drug discovery\n"
            "• Cryptography\n"
            "• Climate modeling\n"
            "• Financial optimization\n\n"
            "We're approaching *quantum advantage* — the point where quantum beats classical.\n\n"
            "#QuantumComputing #Qubits #FutureTech #ZemenByte"
        ),
        (
            "🔓 *QUANTUM THREAT TO ENCRYPTION*\n\n"
            "Most of today's encryption (RSA, ECC) could be broken by a powerful enough "
            "quantum computer.\n\n"
            "⚠️ 'Harvest now, decrypt later' attacks are already happening.\n\n"
            "🛡️ The solution: *Post-Quantum Cryptography (PQC)*\n"
            "NIST has finalized new PQC standards — migration starts now.\n\n"
            "Is your data quantum-safe?\n\n"
            "#QuantumCryptography #PostQuantum #PQC #CyberSecurity #ZemenByte"
        ),
        (
            "🏆 *QUANTUM MILESTONES IN 2024-2025*\n\n"
            "• Google's Willow chip: solved a problem in 5 mins that would take classical "
            "computers 10 septillion years\n"
            "• IBM reached 1000+ qubit processors\n"
            "• Microsoft announced topological qubits\n\n"
            "🚀 We're witnessing quantum computing history in real time.\n\n"
            "#QuantumComputing #Google #IBM #Microsoft #ZemenByte"
        ),
    ],

    "Innovation": [
        (
            "💡 *INNOVATION SPOTLIGHT*\n\n"
            "The most disruptive technologies of this decade:\n\n"
            "1️⃣ Generative AI\n"
            "2️⃣ Spatial Computing (AR/VR)\n"
            "3️⃣ Biotech & synthetic biology\n"
            "4️⃣ Autonomous vehicles\n"
            "5️⃣ Brain-computer interfaces\n"
            "6️⃣ Fusion energy\n\n"
            "🔮 The convergence of these will reshape civilization.\n\n"
            "Which one will have the biggest impact? Vote below! 👇\n\n"
            "#Innovation #FutureTech #DeepTech #Startups #ZemenByte"
        ),
        (
            "🚗 *AUTONOMOUS VEHICLES: CLOSER THAN YOU THINK*\n\n"
            "Waymo is operating fully driverless taxis in multiple US cities.\n"
            "Tesla's FSD continues to improve with each software update.\n\n"
            "🌍 Impact when AVs go mainstream:\n"
            "• 90% reduction in traffic accidents\n"
            "• Transformed urban planning\n"
            "• New mobility-as-a-service economy\n\n"
            "#AutonomousVehicles #SelfDriving #Tesla #Waymo #Innovation #ZemenByte"
        ),
        (
            "🧠 *BRAIN-COMPUTER INTERFACES: SCIENCE FICTION BECOMES REAL*\n\n"
            "Neuralink's N1 chip is implanted in human patients.\n"
            "The first patient can control a computer cursor with their thoughts.\n\n"
            "🔮 Future possibilities:\n"
            "• Restoring movement for paralyzed patients\n"
            "• Memory enhancement\n"
            "• Direct brain-to-brain communication\n\n"
            "Are we ready for the ethical implications?\n\n"
            "#BCI #Neuralink #Neurotechnology #Innovation #ZemenByte"
        ),
    ],

    "Tech": [
        (
            "💻 *TECH TREND OF THE DAY*\n\n"
            "Edge computing is shifting data processing from centralized clouds to "
            "devices *at the edge* — closer to where data is generated.\n\n"
            "⚡ Benefits:\n"
            "• Ultra-low latency\n"
            "• Reduced bandwidth costs\n"
            "• Better privacy & security\n"
            "• Works offline\n\n"
            "IoT + 5G + Edge = the infrastructure of tomorrow's connected world.\n\n"
            "#EdgeComputing #IoT #5G #CloudComputing #ZemenByte"
        ),
        (
            "📱 *THE SMARTPHONE IS EVOLVING*\n\n"
            "AI-native smartphones are here — with dedicated Neural Processing Units "
            "running models on-device.\n\n"
            "🔮 What's coming:\n"
            "• Real-time AI translation\n"
            "• On-device health monitoring\n"
            "• Ambient computing (no screen needed)\n"
            "• AR glasses replacing phones by 2030?\n\n"
            "#Smartphone #AIPhone #Mobile #Tech #ZemenByte"
        ),
        (
            "☁️ *CLOUD COMPUTING: THE INVISIBLE BACKBONE*\n\n"
            "Without the cloud, there is no Netflix, no Zoom, no ChatGPT.\n\n"
            "🌐 The big three:\n"
            "• AWS: 31% market share\n"
            "• Azure: 25% market share\n"
            "• GCP: 11% market share\n\n"
            "🚀 Multi-cloud and sovereign cloud are the next big trends.\n\n"
            "#CloudComputing #AWS #Azure #GCP #DevOps #ZemenByte"
        ),
        (
            "🔧 *OPEN SOURCE IS EATING THE WORLD*\n\n"
            "Linux powers 96.4% of the world's top 1 million web servers.\n"
            "Android (Linux-based) runs 72% of smartphones.\n"
            "Meta, Google, Microsoft all contribute massively to open source.\n\n"
            "💪 Open source isn't charity — it's the foundation of the modern internet.\n\n"
            "#OpenSource #Linux #GitHub #DevOps #ZemenByte"
        ),
    ],
}

# ── Special content: weekly series ───────────────────────────────────────────

WEEKLY_SERIES = {
    "Monday": (
        "🗓️ *MONDAY MOTIVATION — Tech Edition*\n\n"
        "'The best way to predict the future is to invent it.' — Alan Kay\n\n"
        "Start your week by learning something new about tech. 🚀\n\n"
        "What are your tech goals this week? Drop them below! 👇\n\n"
        "#MondayMotivation #Tech #LearningEveryDay #ZemenByte"
    ),
    "Wednesday": (
        "🔍 *WEDNESDAY DEEP DIVE*\n\n"
        "Mid-week, mid-mind. Let's go deep on a concept that matters.\n\n"
        "Today's deep dive: *How does zero-knowledge proof work?*\n\n"
        "ZKPs let you prove you know something *without revealing what you know*. "
        "They're powering private blockchain transactions and next-gen authentication.\n\n"
        "🧩 Mind blown yet? 🤯\n\n"
        "#ZeroKnowledge #Cryptography #Blockchain #ZemenByte"
        ),
    "Friday": (
        "🎉 *FRIDAY TECH ROUNDUP*\n\n"
        "Another week, another leap forward in technology.\n\n"
        "📌 This week's highlights:\n"
        "• AI models getting smarter\n"
        "• Crypto markets finding direction\n"
        "• Quantum research breaking barriers\n"
        "• New vulnerabilities patched globally\n\n"
        "Have a great weekend — keep building, keep learning! 🙌\n\n"
        "#FridayRoundup #TechWeekly #ZemenByte"
    ),
}


class ContentEngine:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self._topic_history: list = []

    def pick_topic(self) -> str:
        """Weighted random topic, avoiding immediate repeats."""
        topics  = self.cfg.TOPICS
        weights = self.cfg.TOPIC_WEIGHTS
        # Reduce weight of last-used topic
        if self._topic_history:
            last = self._topic_history[-1]
            if last in topics:
                idx = topics.index(last)
                w = list(weights)
                w[idx] *= 0.2
                total = sum(w)
                weights = [x/total for x in w]
        chosen = random.choices(topics, weights=weights, k=1)[0]
        self._topic_history.append(chosen)
        if len(self._topic_history) > 10:
            self._topic_history.pop(0)
        return chosen

    def generate_post(self, topic: str) -> str:
        """Return a formatted post string for the given topic."""
        # Check for weekly series override
        day = datetime.utcnow().strftime("%A")
        if day in WEEKLY_SERIES and random.random() < 0.15:
            return WEEKLY_SERIES[day]

        posts = POSTS.get(topic, POSTS["Tech"])
        post  = random.choice(posts)

        # Append timestamp footer
        ts = datetime.utcnow().strftime("%d %b %Y • %H:%M UTC")
        footer = f"\n\n📡 _ZemenByte | {ts}_"
        return post + footer

    def generate_breaking_news(self, headline: str, body: str, topic: str) -> str:
        emoji_map = {
            "AI": "🤖", "Crypto": "₿", "Cybersecurity": "🔐",
            "Quantum": "⚛️", "Innovation": "💡", "Tech": "💻"
        }
        e = emoji_map.get(topic, "📰")
        ts = datetime.utcnow().strftime("%d %b %Y • %H:%M UTC")
        return (
            f"{e} *BREAKING: {headline.upper()}*\n\n"
            f"{body}\n\n"
            f"📡 _ZemenByte | {ts}_\n\n"
            f"#{topic} #Breaking #ZemenByte"
        )

    def generate_thread(self, topic: str, points: list) -> list[str]:
        """Generate a numbered thread as a list of messages."""
        thread = []
        header = (
            f"🧵 *THREAD: {topic.upper()}*\n\n"
            f"A breakdown you need to read. 👇 (1/{len(points)+1})"
        )
        thread.append(header)
        for i, point in enumerate(points, start=2):
            thread.append(f"({i}/{len(points)+1}) {point}")
        thread.append(
            f"({len(points)+1}/{len(points)+1}) That's a wrap! 🎯\n\n"
            f"Follow @{self.cfg.CHANNEL_USERNAME} for more insights.\n\n"
            f"#{''.join(topic.split())} #ZemenByte"
        )
        return thread
