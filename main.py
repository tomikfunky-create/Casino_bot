"""Main bot handlers."""
import logging
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database import Database
from config import Config
from locales.strings import get_string
from utils.keyboards import main_menu, games_menu, language_keyboard, deposit_keyboard

logger = logging.getLogger(__name__)
router = Router()


async def get_or_create_user(message: Message, db: Database, config: Config, referrer_id: int = None):
    user = await db.get_user(message.from_user.id)
    if not user:
        lang = message.from_user.language_code
        lang = "ru" if lang and lang.startswith("ru") else "en"
        user = await db.create_user(
            user_id=message.from_user.id,
            username=message.from_user.username or "",
            full_name=message.from_user.full_name or "Player",
            language=lang,
            referrer_id=referrer_id,
            start_bonus=config.START_BONUS,
        )
        await db.add_coins(message.from_user.id, config.START_BONUS, "Welcome bonus")
        return user, True  # is_new
    return user, False


@router.message(CommandStart())
async def cmd_start(message: Message, db: Database, config: Config, state: FSMContext):
    await state.clear()
    
    # Extract referral
    referrer_id = None
    args = message.text.split()
    if len(args) > 1 and args[1].startswith("ref_"):
        try:
            referrer_id = int(args[1][4:])
            if referrer_id == message.from_user.id:
                referrer_id = None
        except ValueError:
            pass
    
    user, is_new = await get_or_create_user(message, db, config, referrer_id)
    lang = user["language"]
    
    if is_new:
        text = get_string(lang, "welcome", bonus=config.START_BONUS)
    else:
        text = get_string(lang, "welcome_back", name=user["full_name"], coins=user["coins"])
    
    await message.answer(text, parse_mode="Markdown", reply_markup=main_menu(lang))


@router.message(Command("balance"))
@router.message(F.text.in_(["💰 Баланс", "💰 Balance"]))
async def cmd_balance(message: Message, db: Database):
    user = await db.get_user(message.from_user.id)
    if not user:
        await message.answer("Please use /start first")
        return
    
    lang = user["language"]
    profit = user["total_won"] - user["total_wagered"]
    
    text = get_string(
        lang, "balance",
        coins=user["coins"],
        ref_balance=user["referral_balance"],
        games_played=user["games_played"],
        total_wagered=user["total_wagered"],
        total_won=user["total_won"],
        profit=profit,
    )
    await message.answer(text, parse_mode="Markdown")


@router.message(Command("deposit"))
@router.message(F.text.in_(["💳 Пополнить", "💳 Deposit"]))
async def cmd_deposit(message: Message, db: Database, config: Config):
    user = await db.get_user(message.from_user.id)
    if not user:
        await message.answer("Please use /start first")
        return
    
    lang = user["language"]
    text = get_string(lang, "deposit_menu", rate=config.CURRENCY)
    await message.answer(text, parse_mode="Markdown", reply_markup=deposit_keyboard(lang, config.CURRENCY))


@router.message(Command("referral"))
@router.message(F.text.in_(["👥 Рефералы", "👥 Referrals"]))
async def cmd_referral(message: Message, db: Database):
    user = await db.get_user(message.from_user.id)
    if not user:
        await message.answer("Please use /start first")
        return
    
    lang = user["language"]
    bot_username = (await message.bot.get_me()).username
    link = f"https://t.me/{bot_username}?start=ref_{message.from_user.id}"
    
    referrals = await db.get_referrals(message.from_user.id)
    
    if referrals:
        ref_list = "\n".join(
            get_string(lang, "referral_item",
                      name=r["full_name"] or r["username"] or f"User#{r['referred_id']}",
                      earned=r["bonus_earned"])
            for r in referrals
        )
    else:
        ref_list = get_string(lang, "referral_empty")
    
    text = get_string(
        lang, "referral_info",
        link=link,
        count=len(referrals),
        earned=user["referral_balance"],
        referrals_list=ref_list,
    )
    await message.answer(text, parse_mode="Markdown")


@router.message(Command("history"))
@router.message(F.text.in_(["📜 История", "📜 History"]))
async def cmd_history(message: Message, db: Database):
    user = await db.get_user(message.from_user.id)
    if not user:
        return
    
    lang = user["language"]
    history = await db.get_game_history(message.from_user.id, 10)
    
    if not history:
        await message.answer(get_string(lang, "history_empty"), parse_mode="Markdown")
        return
    
    game_emojis = {
        "slots": "🎰", "roulette": "🎲", "coin": "🪙",
        "crash": "💥", "blackjack": "🃏",
    }
    
    text = get_string(lang, "history_title")
    for h in history:
        emoji = game_emojis.get(h["game"], "🎮")
        profit_str = f"+{h['profit']}" if h["profit"] >= 0 else str(h["profit"])
        result_label = "Win" if h["profit"] > 0 else ("Push" if h["profit"] == 0 else "Loss")
        text += get_string(lang, "history_item",
                          emoji=emoji, game=h["game"].title(),
                          bet=h["bet"], result=result_label, profit=profit_str)
    
    await message.answer(text, parse_mode="Markdown")


@router.message(Command("leaderboard"))
@router.message(F.text.in_(["🏆 Лидеры", "🏆 Leaderboard"]))
async def cmd_leaderboard(message: Message, db: Database):
    user = await db.get_user(message.from_user.id)
    lang = user["language"] if user else "ru"
    
    leaders = await db.get_leaderboard(10)
    
    medals = ["🥇", "🥈", "🥉"]
    text = get_string(lang, "leaderboard_title")
    for i, leader in enumerate(leaders):
        pos = medals[i] if i < 3 else f"{i+1}."
        name = leader["full_name"] or leader["username"] or f"Player#{leader['user_id']}"
        text += get_string(lang, "leaderboard_item", pos=pos, name=name, coins=leader["coins"])
    
    await message.answer(text, parse_mode="Markdown")


@router.message(Command("help"))
@router.message(F.text.in_(["❓ Помощь", "❓ Help"]))
async def cmd_help(message: Message, db: Database, config: Config):
    user = await db.get_user(message.from_user.id)
    lang = user["language"] if user else "ru"
    
    text = get_string(lang, "help",
                     min_bet=config.MIN_BET,
                     max_bet=config.MAX_BET,
                     rate=config.STARS_TO_COINS)
    await message.answer(text, parse_mode="Markdown")


@router.message(F.text.in_(["🌍 Язык", "🌍 Language"]))
async def cmd_language(message: Message, db: Database):
    user = await db.get_user(message.from_user.id)
    lang = user["language"] if user else "ru"
    text = get_string(lang, "choose_language")
    await message.answer(text, reply_markup=language_keyboard())


@router.callback_query(F.data.startswith("lang:"))
async def cb_language(callback: CallbackQuery, db: Database):
    lang = callback.data.split(":")[1]
    await db.update_user(callback.from_user.id, language=lang)
    user = await db.get_user(callback.from_user.id)
    await callback.message.delete()
    text = get_string(lang, "welcome_back", name=user["full_name"], coins=user["coins"])
    await callback.message.answer(text, parse_mode="Markdown", reply_markup=main_menu(lang))
    await callback.answer()


@router.message(F.text.in_(["🎮 Игры", "🎮 Games"]))
async def cmd_games(message: Message, db: Database):
    user = await db.get_user(message.from_user.id)
    lang = user["language"] if user else "ru"
    await message.answer(get_string(lang, "games_menu"), parse_mode="Markdown", reply_markup=games_menu(lang))


@router.callback_query(F.data == "game_menu")
async def cb_game_menu(callback: CallbackQuery, db: Database):
    user = await db.get_user(callback.from_user.id)
    lang = user["language"] if user else "ru"
    await callback.message.edit_text(get_string(lang, "games_menu"), parse_mode="Markdown", reply_markup=games_menu(lang))
    await callback.answer()
