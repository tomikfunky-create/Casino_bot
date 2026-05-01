import os
from dataclasses import dataclass, field


@dataclass
class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
    DB_PATH: str = os.getenv("DB_PATH", "casino.db")

    # ── Game settings ──────────────────────────────────────────────────────────
    MIN_BET: int = 10
    MAX_BET: int = 10000
    START_BONUS: int = 100          # Free coins on first /start

    # ── Referral ───────────────────────────────────────────────────────────────
    REFERRAL_PERCENT: float = 0.10  # 10% from friend's deposits

    # ── House edge ─────────────────────────────────────────────────────────────
    CRASH_HOUSE_EDGE: float = 0.05

    # ── Payment settings ───────────────────────────────────────────────────────
    # Currency label shown to users (e.g. "GEL", "USD", "USDT")
    CURRENCY: str = os.getenv("CURRENCY", "GEL")

    # Your payment details — shown inside the bot when user clicks "Deposit"
    # Use \n to add new lines. Supports Markdown.
    PAYMENT_DETAILS: str = os.getenv(
        "PAYMENT_DETAILS",
        "🏦 *Банк:* TBC / BOG\n"
        "💳 *Карта:* `5000 0000 0000 0000`\n"
        "👤 *Получатель:* Имя Фамилия\n\n"
        "_или_\n\n"
        "₿ *USDT (TRC-20):*\n"
        "`TYourWalletAddressHere`"
    )

    # Admin Telegram IDs — these users receive deposit requests and can approve
    ADMIN_IDS: list = None

    def __post_init__(self):
        if self.ADMIN_IDS is None:
            admin_ids_str = os.getenv("ADMIN_IDS", "")
            self.ADMIN_IDS = [int(x) for x in admin_ids_str.split(",") if x.strip()]
