from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from locales.strings import get_string


def main_menu(lang: str) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text=get_string(lang, "btn_games")),
        KeyboardButton(text=get_string(lang, "btn_balance")),
    )
    builder.row(
        KeyboardButton(text=get_string(lang, "btn_deposit")),
        KeyboardButton(text=get_string(lang, "btn_referral")),
    )
    builder.row(
        KeyboardButton(text=get_string(lang, "btn_history")),
        KeyboardButton(text=get_string(lang, "btn_leaderboard")),
    )
    builder.row(
        KeyboardButton(text=get_string(lang, "btn_help")),
        KeyboardButton(text=get_string(lang, "btn_language")),
    )
    return builder.as_markup(resize_keyboard=True)


def games_menu(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🎰 Слоты / Slots", callback_data="game:slots"),
        InlineKeyboardButton(text="🎲 Рулетка / Roulette", callback_data="game:roulette"),
    )
    builder.row(
        InlineKeyboardButton(text="🪙 Монетка / Coin", callback_data="game:coin"),
        InlineKeyboardButton(text="💥 Краш / Crash", callback_data="game:crash"),
    )
    builder.row(
        InlineKeyboardButton(text="🃏 Блэкджек / Blackjack", callback_data="game:blackjack"),
    )
    return builder.as_markup()


def language_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"),
        InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en"),
    )
    return builder.as_markup()


def deposit_keyboard(lang: str, currency: str = "GEL") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    # (amount in real currency, coins)
    packages = [
        ("5", 500),
        ("10", 1000),
        ("25", 2500),
        ("50", 5000),
        ("100", 10000),
    ]
    for amount, coins in packages:
        builder.row(
            InlineKeyboardButton(
                text=f"💳 {amount} {currency} → 🪙 {coins} монет",
                callback_data=f"deposit:{amount}:{coins}",
            )
        )
    builder.row(InlineKeyboardButton(text=get_string(lang, "btn_back"), callback_data="game_menu"))
    return builder.as_markup()


def roulette_bet_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔴 Красное/Red", callback_data="roulette_bet:red"),
        InlineKeyboardButton(text="⚫ Чёрное/Black", callback_data="roulette_bet:black"),
    )
    builder.row(
        InlineKeyboardButton(text="🟢 Зеро/Zero", callback_data="roulette_bet:zero"),
    )
    builder.row(
        InlineKeyboardButton(text="Чётное/Even", callback_data="roulette_bet:even"),
        InlineKeyboardButton(text="Нечётное/Odd", callback_data="roulette_bet:odd"),
    )
    builder.row(
        InlineKeyboardButton(text="1-18", callback_data="roulette_bet:low"),
        InlineKeyboardButton(text="19-36", callback_data="roulette_bet:high"),
    )
    builder.row(
        InlineKeyboardButton(text="🔢 Число/Number", callback_data="roulette_bet:number"),
    )
    builder.row(InlineKeyboardButton(text=get_string(lang, "btn_back"), callback_data="game_menu"))
    return builder.as_markup()


def coin_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=get_string(lang, "coin_heads"), callback_data="coin:heads"),
        InlineKeyboardButton(text=get_string(lang, "coin_tails"), callback_data="coin:tails"),
    )
    builder.row(InlineKeyboardButton(text=get_string(lang, "btn_back"), callback_data="game_menu"))
    return builder.as_markup()


def crash_autowin_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    multis = ["1.5x", "2x", "3x", "5x", "10x"]
    for m in multis:
        builder.button(text=m, callback_data=f"crash_auto:{m}")
    builder.button(text="❌ Manual", callback_data="crash_auto:manual")
    builder.adjust(3)
    return builder.as_markup()


def crash_cashout_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=get_string(lang, "crash_cashout"),
            callback_data="crash:cashout"
        )
    )
    return builder.as_markup()


def blackjack_keyboard(lang: str, can_double: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=get_string(lang, "blackjack_hit"), callback_data="bj:hit"),
        InlineKeyboardButton(text=get_string(lang, "blackjack_stand"), callback_data="bj:stand"),
    )
    if can_double:
        builder.row(
            InlineKeyboardButton(text=get_string(lang, "blackjack_double"), callback_data="bj:double"),
        )
    return builder.as_markup()


def play_again_keyboard(lang: str, game: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=get_string(lang, "btn_play_again"), callback_data=f"game:{game}"),
        InlineKeyboardButton(text=get_string(lang, "btn_back"), callback_data="game_menu"),
    )
    return builder.as_markup()
