"""
content_engine.py — ZemenByte Content Engine
Trilingual: English, Amharic (አማርኛ), Afaan Oromoo
Topics: AI, Crypto, Cybersecurity, Quantum, Innovation, Tech, Technology, DeepTech
"""

import random
from datetime import datetime
from typing import Optional
from config import Config


# ════════════════════════════════════════════════════════════════════════════
#  ENGLISH POSTS
# ════════════════════════════════════════════════════════════════════════════

POSTS_EN = {

    "AI": [
        (
            "🤖 *AI INSIGHT OF THE DAY*\n\n"
            "Large Language Models are evolving beyond text — they're now reasoning agents "
            "capable of multi-step planning, code execution, and real-time web access.\n\n"
            "🔮 *What's next?* Autonomous AI agents managing complex workflows end-to-end.\n\n"
            "💡 The question is no longer *'Can AI do this?'* — it's *'Should we let it?'*\n\n"
            "📌 Which AI advancement excites you most? 👇\n\n"
            "#AI #ArtificialIntelligence #LLM #MachineLearning #ZemenByte"
        ),
        (
            "⚡ *AI IS RESHAPING EVERY INDUSTRY*\n\n"
            "From healthcare diagnostics to financial modeling — AI is no longer a future concept.\n\n"
            "📊 *Key Stats:*\n"
            "• 77% of devices use AI in some form\n"
            "• AI market projected at $1.8T by 2030\n"
            "• 300M jobs will be impacted globally\n\n"
            "🧠 Stay informed. Stay ahead.\n\n"
            "#AITrends #FutureOfWork #TechNews #ZemenByte"
        ),
        (
            "🧬 *AI × SCIENCE = UNSTOPPABLE*\n\n"
            "AlphaFold predicted protein structures for virtually every known protein.\n"
            "AI is now designing new drugs in *days* instead of years.\n\n"
            "🔬 The merger of AI and biology is one of the most profound shifts in human history.\n\n"
            "#AI #Biotech #AlphaFold #DrugDiscovery #ZemenByte"
        ),
    ],

    "Crypto": [
        (
            "₿ *BITCOIN: DIGITAL GOLD OR GLOBAL CURRENCY?*\n\n"
            "Bitcoin has survived bear markets, bans, and FUD for over 15 years.\n\n"
            "📌 *Why Bitcoin remains relevant:*\n"
            "✅ Fixed supply of 21 million\n"
            "✅ Fully decentralized\n"
            "✅ Nation-state level adoption\n"
            "✅ Hedge against inflation\n\n"
            "#Bitcoin #BTC #CryptoNews #HODL #ZemenByte"
        ),
        (
            "🔗 *WEB3: THE INTERNET REVOLUTION*\n\n"
            "Web1: Read\nWeb2: Read + Write\nWeb3: Read + Write + *Own*\n\n"
            "Blockchain-based ownership changes everything:\n"
            "• Your data is *yours*\n"
            "• Payments without banks\n"
            "• DAOs replacing corporations\n\n"
            "#Web3 #Blockchain #DeFi #DAO #Crypto #ZemenByte"
        ),
        (
            "⚠️ *CRYPTO SAFETY TIPS — DON'T GET REKT*\n\n"
            "Billions are lost to scams and hacks every year.\n\n"
            "🛡️ *Protect yourself:*\n"
            "🔐 Use a hardware wallet (Ledger, Trezor)\n"
            "🚫 Never share your seed phrase — EVER\n"
            "👀 Verify contract addresses\n"
            "📧 Enable 2FA on all exchanges\n\n"
            "#CryptoSecurity #DYOR #Blockchain #ZemenByte"
        ),
    ],

    "Cybersecurity": [
        (
            "🔐 *CYBERSECURITY ALERT*\n\n"
            "Ransomware attacks increased by 95% last year — and no one is immune.\n\n"
            "🏢 Targets include hospitals, infrastructure, SMEs & governments.\n\n"
            "🛡️ *Your defense starts with awareness.*\n\n"
            "What's your #1 cybersecurity practice? 👇\n\n"
            "#Cybersecurity #Ransomware #InfoSec #ZemenByte"
        ),
        (
            "👁️ *ZERO TRUST: THE NEW SECURITY MODEL*\n\n"
            "Old model: *Trust but verify*\n"
            "Zero Trust: *Never trust, always verify*\n\n"
            "🔑 Zero Trust pillars:\n"
            "• Verify every user & device\n"
            "• Least privilege access\n"
            "• Continuous monitoring\n\n"
            "#ZeroTrust #CyberSecurity #CloudSecurity #ZemenByte"
        ),
    ],

    "Quantum": [
        (
            "⚛️ *QUANTUM COMPUTING: THE NEXT FRONTIER*\n\n"
            "Classical computers use bits (0 or 1).\n"
            "Quantum computers use *qubits* — 0, 1, or *both simultaneously*.\n\n"
            "🌀 This enables exponentially faster computation for:\n"
            "• Drug discovery • Cryptography • Climate modeling\n\n"
            "We're approaching *quantum advantage*.\n\n"
            "#QuantumComputing #Qubits #FutureTech #ZemenByte"
        ),
        (
            "🔓 *QUANTUM THREAT TO ENCRYPTION*\n\n"
            "Most encryption (RSA, ECC) could be broken by a powerful enough quantum computer.\n\n"
            "⚠️ 'Harvest now, decrypt later' attacks are already happening.\n\n"
            "🛡️ The solution: *Post-Quantum Cryptography (PQC)*\n\n"
            "#QuantumCryptography #PostQuantum #PQC #ZemenByte"
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
            "🔮 Their convergence will reshape civilization.\n\n"
            "Which will have the biggest impact? 👇\n\n"
            "#Innovation #FutureTech #DeepTech #ZemenByte"
        ),
        (
            "🧠 *BRAIN-COMPUTER INTERFACES: SCIENCE FICTION BECOMES REAL*\n\n"
            "Neuralink's N1 chip is implanted in human patients.\n"
            "The first patient can control a computer cursor with their thoughts.\n\n"
            "🔮 Future: restoring movement, memory enhancement, brain-to-brain communication.\n\n"
            "#BCI #Neuralink #Neurotechnology #Innovation #ZemenByte"
        ),
        (
            "🚗 *AUTONOMOUS VEHICLES: CLOSER THAN YOU THINK*\n\n"
            "Waymo is operating fully driverless taxis in multiple US cities.\n"
            "Tesla FSD continues improving with every update.\n\n"
            "🌍 Impact: 90% fewer accidents, new mobility economy, transformed cities.\n\n"
            "#AutonomousVehicles #SelfDriving #Tesla #Waymo #Innovation #ZemenByte"
        ),
    ],

    "Tech": [
        (
            "💻 *TECH TREND OF THE DAY*\n\n"
            "Edge computing shifts processing from centralized clouds to devices *at the edge* — "
            "closer to where data is generated.\n\n"
            "⚡ Benefits: ultra-low latency, reduced costs, better privacy, works offline.\n\n"
            "IoT + 5G + Edge = the infrastructure of tomorrow.\n\n"
            "#EdgeComputing #IoT #5G #CloudComputing #ZemenByte"
        ),
        (
            "🔧 *OPEN SOURCE IS EATING THE WORLD*\n\n"
            "Linux powers 96.4% of the world's top 1M web servers.\n"
            "Android (Linux-based) runs 72% of smartphones.\n\n"
            "💪 Open source isn't charity — it's the foundation of the modern internet.\n\n"
            "#OpenSource #Linux #GitHub #DevOps #ZemenByte"
        ),
        (
            "☁️ *CLOUD COMPUTING: THE INVISIBLE BACKBONE*\n\n"
            "Without the cloud, there is no Netflix, no Zoom, no ChatGPT.\n\n"
            "🌐 The big three:\n"
            "• AWS: 31% • Azure: 25% • GCP: 11%\n\n"
            "🚀 Multi-cloud and sovereign cloud are the next big trends.\n\n"
            "#CloudComputing #AWS #Azure #GCP #ZemenByte"
        ),
    ],

    "Technology": [
        (
            "📱 *THE SMARTPHONE IS EVOLVING*\n\n"
            "AI-native smartphones now have dedicated Neural Processing Units running models on-device.\n\n"
            "🔮 What's coming:\n"
            "• Real-time AI translation\n"
            "• On-device health monitoring\n"
            "• AR glasses replacing phones by 2030?\n\n"
            "#Smartphone #AIPhone #Mobile #Technology #ZemenByte"
        ),
        (
            "🌐 *5G IS CHANGING EVERYTHING*\n\n"
            "5G is not just faster internet — it's the backbone of the IoT revolution.\n\n"
            "📡 5G enables:\n"
            "• Smart cities & autonomous vehicles\n"
            "• Remote surgery with zero latency\n"
            "• Massive IoT device connectivity\n\n"
            "#5G #IoT #SmartCity #Technology #ZemenByte"
        ),
        (
            "🔋 *THE BATTERY REVOLUTION*\n\n"
            "Solid-state batteries could give EVs 1,000km range on a single charge.\n\n"
            "⚡ Toyota, Samsung, and QuantumScape are racing to commercialize this tech.\n\n"
            "🌱 The future of clean energy runs on better batteries.\n\n"
            "#Battery #EV #CleanEnergy #Technology #ZemenByte"
        ),
    ],

    "DeepTech": [
        (
            "🔬 *DEEP TECH: BUILDING THE IMPOSSIBLE*\n\n"
            "Deep Tech startups are solving humanity's hardest problems:\n\n"
            "🧬 Biotech — engineering life itself\n"
            "⚛️ Quantum — computing beyond classical limits\n"
            "🤖 Robotics — machines that learn and adapt\n"
            "🌍 CleanTech — reversing climate change\n\n"
            "💰 $60B invested in Deep Tech in 2024 alone.\n\n"
            "#DeepTech #Startups #Innovation #FutureTech #ZemenByte"
        ),
    ],
}


# ════════════════════════════════════════════════════════════════════════════
#  AMHARIC POSTS (አማርኛ)
# ════════════════════════════════════════════════════════════════════════════

POSTS_AM = {

    "AI": [
        (
            "🤖 *የዛሬው AI ትምህርት*\n\n"
            "ሰው ሰራሽ አስተውሎት (AI) አሁን ጽሑፍ ከመፍጠር በላይ ሆኗል።\n"
            "ብዙ ደረጃ ያለው እቅድ ማውጣት፣ ኮድ መፃፍ እና ኢንተርኔትን "
            "በቀጥታ ማስሰስ ይችላል።\n\n"
            "🔮 *ቀጣዩ ምዕራፍ?* ምንም የሰው ጣልቃ ገብነት ሳያስፈልግ ውስብስብ "
            "ተግባሮችን የሚያከናውን AI ወኪል።\n\n"
            "💡 ጥያቄው *'AI ይህን ማድረግ ይችላል?'* ሳይሆን *'ማድረግ ይፈቀድለታል?'* ነው።\n\n"
            "#AI #ሰውሰራሽአስተውሎት #ቴክኖሎጂ #ZemenByte"
        ),
        (
            "⚡ *AI ሁሉንም ዘርፍ እየቀየረ ነው*\n\n"
            "ከጤና አጠባበቅ እስከ ፋይናንስ — AI አሁን እውነታ ነው፣ የወደፊት ህልም አይደለም።\n\n"
            "📊 *ቁልፍ ስታቲስቲክስ:*\n"
            "• 77% የሚሆኑ መሳሪያዎች AI ይጠቀማሉ\n"
            "• የ AI ገበያ እስከ 2030 $1.8 ትሪሊዮን ይደርሳል\n"
            "• 300 ሚሊዮን የሥራ ቦታዎች ይነካሉ\n\n"
            "🧠 መረጃ ያዙ። ቀድሙ።\n\n"
            "#AI #ቴክኖሎጂ #ወደፊት #ZemenByte"
        ),
        (
            "🧬 *AI + ሳይንስ = የማይቆም ጥምረት*\n\n"
            "AlphaFold ለሚታወቁ ሁሉም ፕሮቲኖች መዋቅር አስልቷል።\n"
            "AI አሁን በቀናት ውስጥ አዲስ መድሃኒቶችን ይፈጥራል — ከዓመታት ይልቅ።\n\n"
            "🔬 AI እና ባዮሎጂ መዋሃድ በታሪክ ውስጥ ትልቁ ለውጦች አንዱ ነው።\n\n"
            "#AI #ባዮቴክ #ሳይንስ #ZemenByte"
        ),
    ],

    "Crypto": [
        (
            "₿ *ቢትኮይን: ዲጂታል ወርቅ ወይስ የዓለም ምንዛሬ?*\n\n"
            "ቢትኮይን ለ15 ዓመታት በላይ ቀውሶችን፣ እገዳዎችን እና ጫናዎችን ተቋቁሟል።\n\n"
            "📌 *ቢትኮይን አሁንም ጠቃሚ የሆነው ለምንድን ነው?*\n"
            "✅ 21 ሚሊዮን ብቻ — ቋሚ አቅርቦት\n"
            "✅ ሙሉ ለሙሉ ያልተማከለ\n"
            "✅ የሀገር ደረጃ ተቀባይነት\n"
            "✅ ዋጋ ቅነሳን ይቋቋማል\n\n"
            "#ቢትኮይን #ክሪፕቶ #ዲጂታልምንዛሬ #ZemenByte"
        ),
        (
            "🔗 *Web3: የኢንተርኔት አብዮት*\n\n"
            "Web1: ማንበብ\nWeb2: ማንበብ + መፃፍ\nWeb3: ማንበብ + መፃፍ + *መያዝ*\n\n"
            "Blockchain ላይ የተመሰረተ ባለቤትነት ሁሉንም ይቀይራል:\n"
            "• ውሂብህ *ያንተ* ነው\n"
            "• ያለ ባንክ ክፍያ\n"
            "• ዳኦ ኮርፖሬሽኖችን ይተካሉ\n\n"
            "#Web3 #ብሎክቼይን #DeFi #ZemenByte"
        ),
    ],

    "Cybersecurity": [
        (
            "🔐 *የሳይበር ደህንነት ማስጠንቀቂያ*\n\n"
            "Ransomware ጥቃቶች ባለፈው ዓመት 95% ጨምረዋል — ማንም ከዚህ አያመልጥም።\n\n"
            "🏢 ዒላማዎቹ:\n"
            "• ሆስፒታሎች • ወሳኝ መሠረተ ልማቶች • አነስተኛ ንግዶች • መንግስት\n\n"
            "🛡️ *መከላከያ ከግንዛቤ ይጀምራል።*\n\n"
            "ቁጥር አንድ የሳይበር ደህንነት ልምድህ ምንድን ነው? 👇\n\n"
            "#ሳይበርደህንነት #InfoSec #ZemenByte"
        ),
        (
            "🔑 *የ암호 ንፅህና 101*\n\n"
            "አሁንም 'Password123' ትጠቀማለህ? 🚨\n\n"
            "✅ የ암호 አስተዳዳሪ ተጠቀም (Bitwarden, 1Password)\n"
            "✅ везде 2FA አንቃ\n"
            "✅ ።Passkey ተጠቀም\n"
            "✅ አንድ암호 ብዙ ጊዜ አትጠቀም\n\n"
            "#ደህንነት #ሳይበር #ZemenByte"
        ),
    ],

    "Quantum": [
        (
            "⚛️ *ኳንተም ኮምፒዩቲንግ: ቀጣዩ ድንበር*\n\n"
            "ክላሲካል ኮምፒዩተሮች ቢት (0 ወይም 1) ይጠቀማሉ።\n"
            "ኳንተም ኮምፒዩተሮች *ኩቢት* ይጠቀማሉ — 0፣ 1 ወይም *ሁለቱም በአንድ ጊዜ*።\n\n"
            "🌀 ይህ ሃይለኛ ስሌት ያስችላል:\n"
            "• የህክምና ምርምር • ምስጠራ • የአየር ሁኔታ ሞዴሊንግ\n\n"
            "#ኳንተም #ቴክኖሎጂ #ZemenByte"
        ),
    ],

    "Innovation": [
        (
            "💡 *የፈጠራ ትኩረት*\n\n"
            "የዚህ አስርት ዓመት በጣም አስደናቂ ቴክኖሎጂዎች:\n\n"
            "1️⃣ Generative AI\n"
            "2️⃣ AR/VR\n"
            "3️⃣ ባዮቴክ\n"
            "4️⃣ የራሱን ሚነዳ ተሽከርካሪ\n"
            "5️⃣ Brain-Computer Interface\n"
            "6️⃣ Fusion Energy\n\n"
            "🔮 እነዚህ ቴክኖሎጂዎች ሲዋሃዱ ዓለምን ይቀይሩታል።\n\n"
            "ትልቁ ተፅዕኖ የሚኖረው የቱ ነው? 👇\n\n"
            "#ፈጠራ #ቴክኖሎጂ #ZemenByte"
        ),
        (
            "🚀 *ኢትዮጵያ እና ቴክኖሎጂ*\n\n"
            "ኢትዮጵያ ወጣት ስነ-ህዝብ ያላት ሀገር ናት — ከህዝቧ 70% ከ30 ዓመት በታች ናቸው።\n\n"
            "💻 ቴክኖሎጂ ኢትዮጵያን ሊቀይር ይችላል:\n"
            "• ዲጂታል ኢኮኖሚ\n"
            "• የቴክ ስጋቶች\n"
            "• AI-powered ትምህርት\n\n"
            "ZemenByte ወጣት ኢትዮጵያውያን ቴክ እንዲቀላቀሉ ያመቻቻል! 🇪🇹\n\n"
            "#ኢትዮጵያ #ቴክ #ፈጠራ #ZemenByte"
        ),
    ],

    "Tech": [
        (
            "💻 *የዛሬው ቴክ ዜና*\n\n"
            "Edge Computing ዳታ ማቀናበርን ከማዕከላዊ ደመና ወደ መሳሪያዎቹ ቅርብ ያዛውራል።\n\n"
            "⚡ ጥቅሞች:\n"
            "• ዝቅተኛ መዘግየት\n"
            "• ወጪ ቅነሳ\n"
            "• የተሻለ ግላዊነት\n"
            "• ከኢንተርኔት ውጪ ይሰራል\n\n"
            "#EdgeComputing #IoT #5G #ZemenByte"
        ),
        (
            "🔧 *ክፍት ምንጭ ዓለምን እየወሰደ ነው*\n\n"
            "Linux ከዓለም ከፍተኛ 1 ሚሊዮን ድህረ-ገጾች 96.4% ያስኬዳል።\n"
            "Android (Linux-based) 72% ስልኮችን ያስኬዳል።\n\n"
            "💪 ክፍት ምንጭ ዘመናዊ ኢንተርኔት መሰረት ነው።\n\n"
            "#OpenSource #Linux #ZemenByte"
        ),
    ],

    "Technology": [
        (
            "📱 *ስማርት ፎን እየተሻሻለ ነው*\n\n"
            "AI-native ስማርትፎኖች አሁን ሞዴሎችን ኦን-ዲቫይስ የሚያሄዱ "
            "NPU (Neural Processing Unit) አላቸው።\n\n"
            "🔮 የሚመጣው:\n"
            "• እውነተኛ ጊዜ AI ትርጉም\n"
            "• ኦን-ዲቫይስ የጤና ክትትል\n"
            "• AR መነጽር ስልኮችን ሊተካ ይችላል?\n\n"
            "#ስማርትፎን #AI #ቴክኖሎጂ #ZemenByte"
        ),
        (
            "🌐 *5G ሁሉንም እየቀየረ ነው*\n\n"
            "5G ፈጣን ኢንተርኔት ብቻ አይደለም — የ IoT አብዮት አዕምሮ ነው።\n\n"
            "📡 5G የሚያስችለው:\n"
            "• ስማርት ከተሞች\n"
            "• ያለ ዘግይ የርቀት ቀዶ ጥገና\n"
            "• ግዙፍ IoT ግንኙነት\n\n"
            "#5G #IoT #ቴክኖሎጂ #ZemenByte"
        ),
    ],
}


# ════════════════════════════════════════════════════════════════════════════
#  AFAAN OROMOO POSTS
# ════════════════════════════════════════════════════════════════════════════

POSTS_ORM = {

    "AI": [
        (
            "🤖 *BEEKUMSA AI GUYYAA HAR'AA*\n\n"
            "Modeloonni Afaan Guddaan (LLMs) ammayyaa barreessuu qofa miti — "
            "kaayyoo hedduu qabu, koodii barreessu, fi interneetii yeroo dhugaa barbaaduuf danda'u.\n\n"
            "🔮 *Kan itti aanu?* Hojii xumuraa hojjetan kan nama hin barbaachifne.\n\n"
            "💡 Gaaffiin amma *'AI kana hojjechuu danda'aa?'* osoo hin taane, *'Hojjechuu hayyamamaa?'* dha.\n\n"
            "#AI #TeeknooloojiiNamtolchee #ZemenByte"
        ),
        (
            "⚡ *AI INDAASTIRII HUNDA JIJJIIRAA JRA*\n\n"
            "Fayyaa irraa hanga maallaqaatti — AI har'a dhugaa dha, boru miti.\n\n"
            "📊 *Lakkoofsa Guddaa:*\n"
            "• Meeshaalee 77% AI fayyadamu\n"
            "• Gabaa AI bara 2030 doolaara tiriliyoona 1.8 ni ga'a\n"
            "• Hojii miiliyoona 300 ni miidha\n\n"
            "🧠 Odeeffannoo qabadhu. Dura dhaabbadhu.\n\n"
            "#AI #Teknooloojii #ZemenByte"
        ),
    ],

    "Crypto": [
        (
            "₿ *BITCOIN: WARQEE DIJITAALAA MOOYYEE MAALLAQAA ADDUNYAA?*\n\n"
            "Bitcoin waggaa 15 oliif rakkoo, dhorkaa fi sodaa dandamateera.\n\n"
            "📌 *Maaliif Bitcoin hanga ammaatuu barbaachisaa ta'e?*\n"
            "✅ Lakkoofsaan miiliyoona 21 qofa\n"
            "✅ Giddu-galeessa hin qabu\n"
            "✅ Biyyoonni fudhachuu jalqabaniiru\n"
            "✅ Hanqina gatii irraa ni eega\n\n"
            "#Bitcoin #Crypto #ZemenByte"
        ),
        (
            "🔗 *WEB3: REVOLIYUUSHINII INTERNEETII*\n\n"
            "Web1: Dubbisuu\nWeb2: Dubbisuu + Barreessuu\nWeb3: Dubbisuu + Barreessuu + *Qabachuu*\n\n"
            "Blockchain irratti hundaa'uun qabeenya kee bulchuu ni dandeessa:\n"
            "• Deetaan kee *kan keetiiti*\n"
            "• Maallaqni baankii malee\n"
            "• DAO dhaabbilee ni bakka bu'a\n\n"
            "#Web3 #Blockchain #Crypto #ZemenByte"
        ),
    ],

    "Cybersecurity": [
        (
            "🔐 *AKEEKKACHIISA NAGEENYAA SAAYIBARII*\n\n"
            "Dhalanniiwwan Ransomware bara darbe 95% dabalaniiru — eenyullee nagaa miti.\n\n"
            "🏢 Bakka qabaman:\n"
            "• Hospitaalonni • Bu'uura fayyaa • Daldala xiqqaa • Mootummaa\n\n"
            "🛡️ *Eegumsi beekumsaan jalqaba.*\n\n"
            "Mala nageenyaa saayibarii tokko 1ffaa kan ati fayyadamtu maali? 👇\n\n"
            "#NageenyaSaayibarii #InfoSec #ZemenByte"
        ),
    ],

    "Innovation": [
        (
            "💡 *ARGANNOO HAARAA*\n\n"
            "Teknooloojii yeroo kana baay'ee dinqisiisoo ta'an:\n\n"
            "1️⃣ Generative AI\n"
            "2️⃣ AR/VR\n"
            "3️⃣ Baayoteknooloojii\n"
            "4️⃣ Konkolaataa ofiin ooftu\n"
            "5️⃣ Sammuu fi Kompyuutara walqunnamsiisuu\n"
            "6️⃣ Bifa Fusion Energy\n\n"
            "🔮 Walitti dhufeenya isaanii addunyaa ni jijjiiru.\n\n"
            "Kam caala miidhaa qabaata? 👇\n\n"
            "#Argannoo #Teknooloojii #ZemenByte"
        ),
        (
            "🇪🇹 *OROMIYAA FI TEKNOOLOOJII*\n\n"
            "Dargaggoonni Oromoo kan teknooloojii fayyadamuu baratan addunyaa jijjiiruu danda'u!\n\n"
            "💻 Kan ZemenByte kennu:\n"
            "• AI • Crypto • Nageenyaa Saayibarii • Argannoo Haaraa\n\n"
            "Beekumsa teknooloojii Afaan Oromootiin! 🌟\n\n"
            "#Oromiyaa #Teknooloojii #ZemenByte"
        ),
    ],

    "Tech": [
        (
            "💻 *ODUU TEKNOOLOOJII GUYYAA HAR'AA*\n\n"
            "Edge Computing odeeffannoo qindeessuu gara meeshaalee dhiyoo jiraniitti ni jijjiira.\n\n"
            "⚡ Faaydaalee:\n"
            "• Turmaata gadi bu'aa\n"
            "• Baasii hir'isu\n"
            "• Iccitummaa caalutu jira\n"
            "• Maree interneetii malee ni hojjeta\n\n"
            "#Teknooloojii #IoT #ZemenByte"
        ),
    ],

    "Technology": [
        (
            "📱 *BILBILLI XIQQAAN JIJJIIRAMAA JRA*\n\n"
            "Bilbiloonni AI-native amma modeeloota meeshaa irratti oofan NPU qabu.\n\n"
            "🔮 Kan dhufaa jiru:\n"
            "• Hiikkaa AI yeroo dhugaa\n"
            "• Hordoffii fayyaa meeshaa irratti\n"
            "• Miilaatii AR bilbila bakka bu'uu danda'aa?\n\n"
            "#Bilbila #AI #Teknooloojii #ZemenByte"
        ),
    ],

    "Quantum": [
        (
            "⚛️ *KOMPYUUTARA KWANTAMII: DAANGAA ITTI AANU*\n\n"
            "Kompyuutaroonni baramoo biitii (0 ykn 1) fayyadamu.\n"
            "Kompyuutaroonni kwantamii *kubiitii* fayyadamu — 0, 1, ykn *lamaanuu yeroo tokkotti*.\n\n"
            "🌀 Kun herregaa saffisaa guddaa ni dandeessa:\n"
            "• Qorannoo fayyaa • Iccitummaa • Moodeelii qilleensa\n\n"
            "#Kwantamii #Teknooloojii #ZemenByte"
        ),
    ],
}


# ════════════════════════════════════════════════════════════════════════════
#  WEEKLY SERIES (trilingual, rotates by language)
# ════════════════════════════════════════════════════════════════════════════

WEEKLY_SERIES = {
    "Monday": {
        "en": (
            "🗓️ *MONDAY MOTIVATION — Tech Edition*\n\n"
            "'The best way to predict the future is to invent it.' — Alan Kay\n\n"
            "What are your tech goals this week? Drop them below! 👇\n\n"
            "#MondayMotivation #Tech #ZemenByte"
        ),
        "am": (
            "🗓️ *የሰኞ መነሳሳት — የቴክ እትም*\n\n"
            "'ወደፊቱን ለመተንበይ የሚሻለው መንገድ እሱን መፍጠር ነው።' — Alan Kay\n\n"
            "የዚህ ሳምንት የቴክ ግቦችህ ምንድን ናቸው? ጻፍ! 👇\n\n"
            "#የሰኞመነሳሳት #ቴክ #ZemenByte"
        ),
        "orm": (
            "🗓️ *KAKAASAA WIIXATAA — Teknooloojii*\n\n"
            "'Karaan gaarii futura tilmaamuuf isa uumuu dha.' — Alan Kay\n\n"
            "Galma teknooloojii tis torbee kana maali? Barreessi! 👇\n\n"
            "#KakaasaaWiixataa #Teknooloojii #ZemenByte"
        ),
    },
    "Friday": {
        "en": (
            "🎉 *FRIDAY TECH ROUNDUP*\n\n"
            "Another week, another leap forward in technology.\n\n"
            "📌 This week: AI got smarter, crypto found direction, quantum broke barriers.\n\n"
            "Have a great weekend — keep building! 🙌\n\n"
            "#FridayRoundup #TechWeekly #ZemenByte"
        ),
        "am": (
            "🎉 *የዓርብ ቴክ ማጠቃለያ*\n\n"
            "ሌላ ሳምንት፣ ሌላ ቴክኖሎጂ ዝላይ።\n\n"
            "📌 ይህ ሳምንት: AI ተሻሻለ፣ crypto አቅጣጫ አገኘ፣ quantum ድንበሮችን ሰበረ።\n\n"
            "ጥሩ ሳምንት መጨረሻ! 🙌\n\n"
            "#የዓርብማጠቃለያ #ZemenByte"
        ),
        "orm": (
            "🎉 *CUUNFAA TEKNOOLOOJII JIMAATAA*\n\n"
            "Torbeewwan biraa, tarkaanfii teknooloojii biraa.\n\n"
            "📌 Torbee kana: AI fooyya'e, crypto kallattii argatte, kwantamii daangaa cabse.\n\n"
            "Torban gaarii! 🙌\n\n"
            "#CuunfaaJimaataa #ZemenByte"
        ),
    },
}


# ════════════════════════════════════════════════════════════════════════════
#  ENGINE
# ════════════════════════════════════════════════════════════════════════════

class ContentEngine:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self._topic_history: list = []

    def pick_topic(self) -> str:
        topics  = self.cfg.TOPICS
        weights = list(self.cfg.TOPIC_WEIGHTS)
        if self._topic_history:
            last = self._topic_history[-1]
            if last in topics:
                idx = topics.index(last)
                weights[idx] *= 0.2
                total = sum(weights)
                weights = [x/total for x in weights]
        chosen = random.choices(topics, weights=weights, k=1)[0]
        self._topic_history.append(chosen)
        if len(self._topic_history) > 10:
            self._topic_history.pop(0)
        return chosen

    def pick_language(self) -> str:
        """Pick a language based on config weights."""
        langs   = self.cfg.LANGUAGES
        weights = self.cfg.LANGUAGE_WEIGHTS
        return random.choices(langs, weights=weights, k=1)[0]

    def _get_posts(self, lang: str) -> dict:
        if lang == "am":
            return POSTS_AM
        elif lang == "orm":
            return POSTS_ORM
        return POSTS_EN

    def generate_post(self, topic: str, lang: str = None) -> str:
        if lang is None:
            lang = self.pick_language()

        # Weekly series check (15% chance)
        day = datetime.utcnow().strftime("%A")
        if day in WEEKLY_SERIES and random.random() < 0.15:
            series = WEEKLY_SERIES[day]
            # pick language, fall back to English
            post = series.get(lang) or series.get("en")
        else:
            pool = self._get_posts(lang)
            posts = pool.get(topic) or POSTS_EN.get(topic) or POSTS_EN["Tech"]
            post  = random.choice(posts)

        ts     = datetime.utcnow().strftime("%d %b %Y • %H:%M UTC")
        footer = f"\n\n📡 _ZemenByte | {ts}_"
        return post + footer

    def generate_post_all_languages(self, topic: str) -> list[str]:
        """Generate the same topic in all 3 languages (for special posts)."""
        posts = []
        for lang in ["en", "am", "orm"]:
            pool  = self._get_posts(lang)
            items = pool.get(topic) or POSTS_EN.get(topic) or POSTS_EN["Tech"]
            ts    = datetime.utcnow().strftime("%d %b %Y • %H:%M UTC")
            posts.append(random.choice(items) + f"\n\n📡 _ZemenByte | {ts}_")
        return posts

    def generate_thread(self, topic: str, points: list) -> list[str]:
        thread = [f"🧵 *THREAD: {topic.upper()}*\n\nA breakdown you need to read. 👇 (1/{len(points)+1})"]
        for i, point in enumerate(points, start=2):
            thread.append(f"({i}/{len(points)+1}) {point}")
        thread.append(
            f"({len(points)+1}/{len(points)+1}) That's a wrap! 🎯\n\n"
            f"Follow @{self.cfg.CHANNEL_USERNAME} for more.\n\n"
            f"#{topic} #ZemenByte"
        )
        return thread
