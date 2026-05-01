import aiosqlite
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path

    async def init(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    full_name TEXT,
                    language TEXT DEFAULT 'ru',
                    coins INTEGER DEFAULT 0,
                    referral_balance INTEGER DEFAULT 0,
                    referrer_id INTEGER,
                    total_deposited INTEGER DEFAULT 0,
                    total_withdrawn INTEGER DEFAULT 0,
                    total_wagered INTEGER DEFAULT 0,
                    total_won INTEGER DEFAULT 0,
                    games_played INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    last_active TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    type TEXT,
                    amount INTEGER,
                    description TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                );

                CREATE TABLE IF NOT EXISTS game_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    game TEXT,
                    bet INTEGER,
                    result TEXT,
                    payout INTEGER,
                    profit INTEGER,
                    details TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                );

                CREATE TABLE IF NOT EXISTS referrals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    referrer_id INTEGER,
                    referred_id INTEGER,
                    bonus_earned INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (referrer_id) REFERENCES users(user_id),
                    FOREIGN KEY (referred_id) REFERENCES users(user_id)
                );

                CREATE TABLE IF NOT EXISTS star_payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    stars INTEGER,
                    coins INTEGER,
                    payload TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                );
            """)
            await db.commit()
        logger.info("Database initialized")

    # ─── USER OPERATIONS ───────────────────────────────────────────────────────

    async def get_user(self, user_id: int) -> Optional[dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def create_user(
        self,
        user_id: int,
        username: str,
        full_name: str,
        language: str = "ru",
        referrer_id: int = None,
        start_bonus: int = 100,
    ) -> dict:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT OR IGNORE INTO users 
                   (user_id, username, full_name, language, coins, referrer_id)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (user_id, username, full_name, language, start_bonus, referrer_id),
            )
            if referrer_id:
                await db.execute(
                    "INSERT OR IGNORE INTO referrals (referrer_id, referred_id) VALUES (?, ?)",
                    (referrer_id, user_id),
                )
            await db.commit()
        return await self.get_user(user_id)

    async def update_user(self, user_id: int, **kwargs):
        if not kwargs:
            return
        fields = ", ".join(f"{k} = ?" for k in kwargs)
        values = list(kwargs.values()) + [user_id]
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                f"UPDATE users SET {fields}, last_active = CURRENT_TIMESTAMP WHERE user_id = ?",
                values,
            )
            await db.commit()

    async def add_coins(self, user_id: int, amount: int, description: str = ""):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET coins = coins + ?, last_active = CURRENT_TIMESTAMP WHERE user_id = ?",
                (amount, user_id),
            )
            await db.execute(
                "INSERT INTO transactions (user_id, type, amount, description) VALUES (?, ?, ?, ?)",
                (user_id, "credit", amount, description),
            )
            await db.commit()

    async def deduct_coins(self, user_id: int, amount: int, description: str = "") -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT coins FROM users WHERE user_id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if not row or row[0] < amount:
                    return False
            await db.execute(
                "UPDATE users SET coins = coins - ?, last_active = CURRENT_TIMESTAMP WHERE user_id = ?",
                (amount, user_id),
            )
            await db.execute(
                "INSERT INTO transactions (user_id, type, amount, description) VALUES (?, ?, ?, ?)",
                (user_id, "debit", amount, description),
            )
            await db.commit()
            return True

    async def add_referral_bonus(self, referrer_id: int, amount: int, referred_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET referral_balance = referral_balance + ?, coins = coins + ? WHERE user_id = ?",
                (amount, amount, referrer_id),
            )
            await db.execute(
                "UPDATE referrals SET bonus_earned = bonus_earned + ? WHERE referrer_id = ? AND referred_id = ?",
                (amount, referrer_id, referred_id),
            )
            await db.execute(
                "INSERT INTO transactions (user_id, type, amount, description) VALUES (?, ?, ?, ?)",
                (referrer_id, "referral_bonus", amount, f"Referral bonus from user {referred_id}"),
            )
            await db.commit()

    # ─── GAME OPERATIONS ───────────────────────────────────────────────────────

    async def record_game(
        self,
        user_id: int,
        game: str,
        bet: int,
        result: str,
        payout: int,
        details: str = "",
    ):
        profit = payout - bet
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT INTO game_history (user_id, game, bet, result, payout, profit, details)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (user_id, game, bet, result, payout, profit, details),
            )
            await db.execute(
                """UPDATE users SET 
                   games_played = games_played + 1,
                   total_wagered = total_wagered + ?,
                   total_won = total_won + ?,
                   last_active = CURRENT_TIMESTAMP
                   WHERE user_id = ?""",
                (bet, payout, user_id),
            )
            await db.commit()

    async def get_game_history(self, user_id: int, limit: int = 10) -> list:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM game_history WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
                (user_id, limit),
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(r) for r in rows]

    async def get_referrals(self, user_id: int) -> list:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                """SELECT r.*, u.username, u.full_name, u.total_deposited
                   FROM referrals r
                   JOIN users u ON r.referred_id = u.user_id
                   WHERE r.referrer_id = ?
                   ORDER BY r.created_at DESC""",
                (user_id,),
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(r) for r in rows]

    async def record_star_payment(self, user_id: int, stars: int, coins: int, payload: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO star_payments (user_id, stars, coins, payload) VALUES (?, ?, ?, ?)",
                (user_id, stars, coins, payload),
            )
            await db.execute(
                "UPDATE users SET total_deposited = total_deposited + ? WHERE user_id = ?",
                (coins, user_id),
            )
            await db.commit()

    # ─── STATS & LEADERBOARD ───────────────────────────────────────────────────

    async def get_leaderboard(self, limit: int = 10) -> list:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                """SELECT user_id, username, full_name, coins, games_played, total_won
                   FROM users ORDER BY coins DESC LIMIT ?""",
                (limit,),
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(r) for r in rows]

    async def get_stats(self) -> dict:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM users") as c:
                total_users = (await c.fetchone())[0]
            async with db.execute("SELECT COUNT(*) FROM game_history") as c:
                total_games = (await c.fetchone())[0]
            async with db.execute("SELECT SUM(total_wagered) FROM users") as c:
                total_wagered = (await c.fetchone())[0] or 0
            return {
                "total_users": total_users,
                "total_games": total_games,
                "total_wagered": total_wagered,
            }
