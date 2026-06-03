"""
referral.py — ZemenByte Referral System
Each subscriber gets a unique referral link.
Tracks invites, rewards top referrers, leaderboard.
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path


REFERRAL_FILE = "referral_data.json"


class ReferralSystem:
    def __init__(self, bot_username: str, channel_username: str):
        self.bot_username     = bot_username
        self.channel_username = channel_username
        self._file = Path(REFERRAL_FILE)
        self._data = self._load()

    # ── Persistence ───────────────────────────────────────────────────────
    def _load(self) -> dict:
        if self._file.exists():
            return json.loads(self._file.read_text())
        return {"users": {}, "total_referrals": 0}

    def _save(self):
        self._file.write_text(json.dumps(self._data, indent=2))

    # ── User registration ─────────────────────────────────────────────────
    def register_user(self, user_id: int, username: str = None,
                      first_name: str = None, referred_by: int = None) -> dict:
        """Register a new user or return existing. Returns user dict."""
        uid = str(user_id)
        if uid not in self._data["users"]:
            self._data["users"][uid] = {
                "user_id":    user_id,
                "username":   username or "",
                "first_name": first_name or "User",
                "ref_code":   self._make_code(user_id),
                "referrals":  [],          # list of user_ids they referred
                "referred_by": referred_by,
                "points":     0,
                "joined":     datetime.utcnow().isoformat(),
                "badges":     [],
            }
            # Credit referrer
            if referred_by:
                self._credit_referrer(referred_by, user_id)
            self._save()
        else:
            # Update name/username if changed
            self._data["users"][uid]["username"]   = username or self._data["users"][uid].get("username","")
            self._data["users"][uid]["first_name"] = first_name or self._data["users"][uid].get("first_name","User")
            self._save()
        return self._data["users"][uid]

    def _make_code(self, user_id: int) -> str:
        """Short unique ref code: zb_ + last 8 chars of hash."""
        h = hashlib.md5(f"zemenbyte_{user_id}".encode()).hexdigest()
        return f"zb_{h[:8]}"

    def _credit_referrer(self, referrer_id: int, new_user_id: int):
        rid = str(referrer_id)
        if rid in self._data["users"]:
            if new_user_id not in self._data["users"][rid]["referrals"]:
                self._data["users"][rid]["referrals"].append(new_user_id)
                pts = len(self._data["users"][rid]["referrals"])
                self._data["users"][rid]["points"] = pts * 10
                self._data["total_referrals"] += 1
                # Award badges
                self._check_badges(rid)

    def _check_badges(self, uid: str):
        count  = len(self._data["users"][uid]["referrals"])
        badges = self._data["users"][uid]["badges"]
        milestones = {1:"🌱 Starter", 5:"⭐ Rising Star", 10:"🔥 Influencer",
                      25:"💎 Diamond", 50:"👑 ZemenByte Legend"}
        for threshold, badge in milestones.items():
            if count >= threshold and badge not in badges:
                badges.append(badge)
        self._data["users"][uid]["badges"] = badges

    # ── Getters ───────────────────────────────────────────────────────────
    def get_user(self, user_id: int) -> dict | None:
        return self._data["users"].get(str(user_id))

    def get_ref_link(self, user_id: int) -> str:
        user = self.get_user(user_id)
        if not user:
            return ""
        code = user["ref_code"]
        return f"https://t.me/{self.bot_username}?start={code}"

    def get_ref_count(self, user_id: int) -> int:
        user = self.get_user(user_id)
        return len(user["referrals"]) if user else 0

    def get_points(self, user_id: int) -> int:
        user = self.get_user(user_id)
        return user["points"] if user else 0

    def get_badges(self, user_id: int) -> list:
        user = self.get_user(user_id)
        return user.get("badges", []) if user else []

    def resolve_code(self, code: str) -> int | None:
        """Find user_id from a ref code."""
        for uid, u in self._data["users"].items():
            if u["ref_code"] == code:
                return u["user_id"]
        return None

    # ── Leaderboard ───────────────────────────────────────────────────────
    def get_leaderboard(self, top_n: int = 10) -> list[dict]:
        users = list(self._data["users"].values())
        users.sort(key=lambda u: len(u["referrals"]), reverse=True)
        return [u for u in users if len(u["referrals"]) > 0][:top_n]

    def get_rank(self, user_id: int) -> int:
        lb = self.get_leaderboard(9999)
        for i, u in enumerate(lb, 1):
            if u["user_id"] == user_id:
                return i
        return 0

    # ── Stats ─────────────────────────────────────────────────────────────
    def total_users(self) -> int:
        return len(self._data["users"])

    def total_referrals(self) -> int:
        return self._data.get("total_referrals", 0)

    # ── Messages ──────────────────────────────────────────────────────────
    def referral_card(self, user_id: int) -> str:
        user  = self.get_user(user_id)
        if not user:
            return "❌ Not registered. Send /start first."
        link  = self.get_ref_link(user_id)
        count = len(user["referrals"])
        pts   = user["points"]
        rank  = self.get_rank(user_id)
        badges= " ".join(user.get("badges", [])) or "None yet"
        name  = user.get("first_name", "User")

        # Progress to next badge
        milestones = [1, 5, 10, 25, 50]
        next_ms    = next((m for m in milestones if m > count), None)
        progress   = f"Invite {next_ms - count} more to reach next badge! 🎯" if next_ms else "🏆 MAX LEVEL!"

        return (
            f"🔗 *Your ZemenByte Referral Card*\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 Name:    {name}\n"
            f"🏅 Rank:    #{rank if rank else '—'} on leaderboard\n"
            f"👥 Invited: `{count}` friends\n"
            f"⭐ Points:  `{pts}`\n"
            f"🎖 Badges:  {badges}\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"📎 *Your unique link:*\n"
            f"`{link}`\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"💡 _{progress}_\n\n"
            f"Share and earn points! 🚀"
        )

    def leaderboard_text(self) -> str:
        lb = self.get_leaderboard(10)
        if not lb:
            return "🏆 *Leaderboard is empty.*\n\nBe the first to invite friends! 🚀"
        medals = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
        lines  = []
        for i, u in enumerate(lb):
            name   = u.get("username") and f"@{u['username']}" or u.get("first_name","User")
            count  = len(u["referrals"])
            pts    = u["points"]
            badges = " ".join(u.get("badges",[]))
            lines.append(f"{medals[i]} *{name}* — {count} invites · {pts} pts {badges}")
        return (
            f"🏆 *ZemenByte Referral Leaderboard*\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            + "\n".join(lines) +
            f"\n━━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 Total users: `{self.total_users():,}`\n"
            f"🔗 Total referrals: `{self.total_referrals():,}`\n\n"
            f"Get your link → /referral 🚀"
        )

    def welcome_referred_user(self, new_user: dict, referrer: dict) -> str:
        r_name = referrer.get("username") and f"@{referrer['username']}" or referrer.get("first_name","someone")
        return (
            f"👋 *Welcome to ZemenByte!*\n\n"
            f"You were invited by {r_name} 🎉\n\n"
            f"🇬🇧 Get your own referral link and earn points!\n"
            f"🇪🇹 የራስህን የሪፈራል ሊንክ ውሰድ እና ነጥቦች ስብስብ!\n"
            f"🟢 Hidhata referral kee fudhachuun qabxii argadhu!\n\n"
            f"👉 Tap /referral to get started"
        )
