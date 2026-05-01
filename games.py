"""Game handlers for all 5 casino games."""
import asyncio
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import Database
from config import Config
from locales.strings import get_string
from utils.keyboards import (
    roulette_bet_keyboard, coin_keyboard, blackjack_keyboard,
    play_again_keyboard, crash_autowin_keyboard, crash_cashout_keyboard, games_menu
)
from games.engine import (
    spin_slots, spin_roulette, flip_coin,
    generate_crash_point, calculate_crash_result,
    deal_blackjack, blackjack_hit, resolve_blackjack,
    hand_score, format_cards,
)

logger = logging.getLogger(__name__)
router = Router()


class GameStates(StatesGroup):
    waiting_bet = State()
    roulette_bet_type = State()
    roulette_number = State()
    crash_autowin = State()
    crash_in_progress = State()
    blackjack_playing = State()


# ─── HELPERS ──────────────────────────────────────────────────────────────────

async def validate_bet(message: Message, db: Database, config: Config, lang: str) -> int | None:
    try:
        bet = int(message.text.strip())
    except ValueError:
        await message.answer(
            get_string(lang, "invalid_bet", min=config.MIN_BET, max=config.MAX_BET)
        )
        return None
    
    if bet < config.MIN_BET:
        await message.answer(get_string(lang, "bet_too_low", min=config.MIN_BET))
        return None
    if bet > config.MAX_BET:
        await message.answer(get_string(lang, "bet_too_high", max=config.MAX_BET))
        return None
    
    user = await db.get_user(message.from_user.id)
    if user["coins"] < bet:
        await message.answer(
            get_string(lang, "insufficient_funds", balance=user["coins"])
        )
        return None
    
    return bet


# ─── GAME SELECTOR ────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("game:"))
async def cb_game_select(callback: CallbackQuery, db: Database, config: Config, state: FSMContext):
    game = callback.data.split(":")[1]
    user = await db.get_user(callback.from_user.id)
    lang = user["language"] if user else "ru"
    
    await state.clear()
    await state.update_data(game=game, lang=lang)
    
    if game == "roulette":
        await callback.message.edit_text(
            get_string(lang, "roulette_menu"),
            parse_mode="Markdown",
            reply_markup=roulette_bet_keyboard(lang),
        )
        await state.set_state(GameStates.roulette_bet_type)
    elif game == "coin":
        await callback.message.edit_text(
            get_string(lang, "coin_choose"),
            parse_mode="Markdown",
            reply_markup=coin_keyboard(lang),
        )
    elif game == "crash":
        await callback.message.edit_text(
            get_string(lang, "crash_info"),
            parse_mode="Markdown",
        )
        await state.set_state(GameStates.waiting_bet)
    elif game == "blackjack":
        await callback.message.edit_text(
            get_string(lang, "enter_bet", min=config.MIN_BET, max=config.MAX_BET),
            parse_mode="Markdown",
        )
        await state.set_state(GameStates.waiting_bet)
    else:  # slots
        await callback.message.edit_text(
            get_string(lang, "enter_bet", min=config.MIN_BET, max=config.MAX_BET),
            parse_mode="Markdown",
        )
        await state.set_state(GameStates.waiting_bet)
    
    await callback.answer()


# ─── SLOTS ────────────────────────────────────────────────────────────────────

@router.message(GameStates.waiting_bet)
async def handle_bet_input(message: Message, db: Database, config: Config, state: FSMContext):
    data = await state.get_data()
    game = data.get("game", "slots")
    lang = data.get("lang", "ru")
    
    bet = await validate_bet(message, db, config, lang)
    if bet is None:
        return
    
    if game == "slots":
        await play_slots(message, db, bet, lang, state)
    elif game == "blackjack":
        await start_blackjack(message, db, config, bet, lang, state)
    elif game == "crash":
        await state.update_data(bet=bet)
        await message.answer(
            get_string(lang, "crash_autowin"),
            reply_markup=crash_autowin_keyboard(lang),
        )
        await state.set_state(GameStates.crash_autowin)


async def play_slots(message: Message, db: Database, bet: int, lang: str, state: FSMContext):
    await db.deduct_coins(message.from_user.id, bet, "Slots bet")
    
    wait_msg = await message.answer(get_string(lang, "slots_spinning"))
    await asyncio.sleep(1.5)
    
    result = spin_slots(bet)
    
    if result["payout"] > 0:
        await db.add_coins(message.from_user.id, result["payout"], "Slots win")
    
    await db.record_game(
        message.from_user.id, "slots", bet,
        result["result"], result["payout"], result["reels"]
    )
    
    user = await db.get_user(message.from_user.id)
    
    if result["result"] == "jackpot":
        key = "slots_jackpot"
    elif result["payout"] > 0:
        key = "slots_win"
    else:
        key = "slots_loss"
    
    text = get_string(lang, key,
                     reels=result["reels"],
                     payout=result["payout"],
                     bet=bet,
                     balance=user["coins"])
    
    await wait_msg.delete()
    await message.answer(text, parse_mode="Markdown", reply_markup=play_again_keyboard(lang, "slots"))
    await state.clear()


# ─── ROULETTE ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("roulette_bet:"))
async def cb_roulette_bet(callback: CallbackQuery, db: Database, config: Config, state: FSMContext):
    bet_type = callback.data.split(":")[1]
    data = await state.get_data()
    lang = data.get("lang", "ru")
    
    await state.update_data(roulette_bet_type=bet_type)
    
    if bet_type == "number":
        await callback.message.edit_text(
            get_string(lang, "roulette_enter_number"),
            parse_mode="Markdown",
        )
        await state.set_state(GameStates.roulette_number)
        await callback.answer()
        return
    
    await callback.message.edit_text(
        get_string(lang, "enter_bet", min=config.MIN_BET, max=config.MAX_BET),
        parse_mode="Markdown",
    )
    await state.set_state(GameStates.waiting_bet)
    await state.update_data(game="roulette")
    await callback.answer()


@router.message(GameStates.roulette_number)
async def handle_roulette_number(message: Message, db: Database, config: Config, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    
    try:
        num = int(message.text.strip())
        if not 0 <= num <= 36:
            raise ValueError
    except ValueError:
        await message.answer(get_string(lang, "roulette_invalid_number"))
        return
    
    await state.update_data(roulette_number=num, game="roulette")
    await message.answer(get_string(lang, "enter_bet", min=config.MIN_BET, max=config.MAX_BET))
    await state.set_state(GameStates.waiting_bet)


async def play_roulette(message: Message, db: Database, bet: int, lang: str, state: FSMContext):
    data = await state.get_data()
    bet_type = data.get("roulette_bet_type", "red")
    chosen_number = data.get("roulette_number")
    
    await db.deduct_coins(message.from_user.id, bet, "Roulette bet")
    
    wait_msg = await message.answer(get_string(lang, "roulette_spinning"))
    await asyncio.sleep(2)
    
    result = spin_roulette(bet, bet_type, chosen_number)
    
    if result["payout"] > 0:
        await db.add_coins(message.from_user.id, result["payout"], "Roulette win")
    
    await db.record_game(
        message.from_user.id, "roulette", bet,
        "win" if result["won"] else "loss",
        result["payout"], f"{result['number']} {result['color']}"
    )
    
    user = await db.get_user(message.from_user.id)
    
    if result["won"]:
        outcome_emoji = "🎉"
        outcome_text = get_string(lang, "roulette_win", payout=result["payout"])
    else:
        outcome_emoji = "😔"
        outcome_text = get_string(lang, "roulette_loss", bet=bet)
    
    text = get_string(lang, "roulette_result",
                     number=result["number"],
                     color=result["color"],
                     bet_type=result["bet_label"],
                     outcome_emoji=outcome_emoji,
                     outcome_text=outcome_text,
                     balance=user["coins"])
    
    await wait_msg.delete()
    await message.answer(text, parse_mode="Markdown", reply_markup=play_again_keyboard(lang, "roulette"))
    await state.clear()


# Override waiting_bet handler to route correctly
@router.message(GameStates.waiting_bet)
async def handle_bet_router(message: Message, db: Database, config: Config, state: FSMContext):
    pass  # Handled above


# ─── COIN FLIP ────────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("coin:"))
async def cb_coin(callback: CallbackQuery, db: Database, config: Config, state: FSMContext):
    choice = callback.data.split(":")[1]
    user = await db.get_user(callback.from_user.id)
    lang = user["language"] if user else "ru"
    
    await state.update_data(game="coin", lang=lang, coin_choice=choice)
    await callback.message.edit_text(
        get_string(lang, "enter_bet", min=config.MIN_BET, max=config.MAX_BET),
        parse_mode="Markdown",
    )
    await state.set_state(GameStates.waiting_bet)
    await callback.answer()


async def play_coin(message: Message, db: Database, bet: int, lang: str, state: FSMContext):
    data = await state.get_data()
    choice = data.get("coin_choice", "heads")
    
    await db.deduct_coins(message.from_user.id, bet, "Coin flip bet")
    
    wait_msg = await message.answer(get_string(lang, "coin_flipping"))
    await asyncio.sleep(1.5)
    
    result = flip_coin(bet, choice)
    
    if result["payout"] > 0:
        await db.add_coins(message.from_user.id, result["payout"], "Coin flip win")
    
    await db.record_game(
        message.from_user.id, "coin", bet,
        "win" if result["won"] else "loss",
        result["payout"], result["result"]
    )
    
    user = await db.get_user(message.from_user.id)
    
    result_label = get_string(lang, f"coin_{result['result']}")
    choice_label = get_string(lang, f"coin_{choice}")
    
    if result["won"]:
        outcome_emoji = "🎉"
        outcome_text = f"+{result['payout']} coins"
    else:
        outcome_emoji = "😔"
        outcome_text = f"-{bet} coins"
    
    text = get_string(lang, "coin_result",
                     result=result_label,
                     choice=choice_label,
                     outcome_emoji=outcome_emoji,
                     outcome_text=outcome_text,
                     balance=user["coins"])
    
    await wait_msg.delete()
    await message.answer(text, parse_mode="Markdown", reply_markup=play_again_keyboard(lang, "coin"))
    await state.clear()


# ─── CRASH ────────────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("crash_auto:"))
async def cb_crash_auto(callback: CallbackQuery, db: Database, config: Config, state: FSMContext):
    auto_str = callback.data.split(":")[1]
    data = await state.get_data()
    lang = data.get("lang", "ru")
    bet = data.get("bet")
    
    if not bet:
        await callback.answer("❌ No bet set")
        return
    
    user = await db.get_user(callback.from_user.id)
    if user["coins"] < bet:
        await callback.answer(get_string(lang, "insufficient_funds", balance=user["coins"]), show_alert=True)
        return
    
    auto_mult = None if auto_str == "manual" else float(auto_str.replace("x", ""))
    
    crash_point = generate_crash_point(config.CRASH_HOUSE_EDGE)
    await db.deduct_coins(callback.from_user.id, bet, "Crash bet")
    
    await state.update_data(
        crash_point=crash_point,
        auto_mult=auto_mult,
        cashed_out=False,
    )
    await state.set_state(GameStates.crash_in_progress)
    
    # Simulate crash animation
    current_mult = 1.00
    step = 0.10
    
    msg = await callback.message.edit_text(
        get_string(lang, "crash_flying", mult=f"{current_mult:.2f}"),
        parse_mode="Markdown",
        reply_markup=crash_cashout_keyboard(lang) if not auto_mult else None,
    )
    
    crashed = False
    cashed_out = False
    final_mult = current_mult
    
    while current_mult < crash_point:
        await asyncio.sleep(0.5)
        current_mult = round(current_mult + step, 2)
        if current_mult > 2:
            step = 0.20
        if current_mult > 5:
            step = 0.50
        
        # Check auto cashout
        if auto_mult and current_mult >= auto_mult:
            cashed_out = True
            final_mult = auto_mult
            break
        
        # Check if user cashed out manually
        fresh_data = await state.get_data()
        if fresh_data.get("cashed_out"):
            cashed_out = True
            final_mult = current_mult
            break
        
        try:
            await msg.edit_text(
                get_string(lang, "crash_flying", mult=f"{current_mult:.2f}"),
                parse_mode="Markdown",
                reply_markup=crash_cashout_keyboard(lang) if not auto_mult else None,
            )
        except Exception:
            pass
    
    if not cashed_out:
        final_mult = crash_point
        crashed = True
    
    result = calculate_crash_result(bet, final_mult, crash_point)
    
    if result["payout"] > 0:
        await db.add_coins(callback.from_user.id, result["payout"], "Crash win")
    
    await db.record_game(
        callback.from_user.id, "crash", bet,
        "win" if not crashed else "loss",
        result["payout"], f"Crash@{crash_point}x Cashout@{final_mult}x"
    )
    
    user = await db.get_user(callback.from_user.id)
    
    if not crashed:
        text = get_string(lang, "crash_cashed_out",
                         mult=f"{final_mult:.2f}",
                         payout=result["payout"],
                         balance=user["coins"])
    else:
        text = get_string(lang, "crash_lost",
                         mult=f"{crash_point:.2f}",
                         bet=bet,
                         balance=user["coins"])
    
    try:
        await msg.edit_text(text, parse_mode="Markdown", reply_markup=play_again_keyboard(lang, "crash"))
    except Exception:
        await callback.message.answer(text, parse_mode="Markdown", reply_markup=play_again_keyboard(lang, "crash"))
    
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "crash:cashout", GameStates.crash_in_progress)
async def cb_crash_cashout(callback: CallbackQuery, state: FSMContext):
    await state.update_data(cashed_out=True)
    await callback.answer("✅ Cashing out...")


# ─── BLACKJACK ────────────────────────────────────────────────────────────────

async def start_blackjack(message: Message, db: Database, config: Config, bet: int, lang: str, state: FSMContext):
    await db.deduct_coins(message.from_user.id, bet, "Blackjack bet")
    
    game_data = deal_blackjack()
    player = game_data["player"]
    dealer = game_data["dealer"]
    deck = game_data["deck"]
    
    player_score = hand_score(player)
    
    # Check for natural blackjack
    if player_score == 21:
        result = resolve_blackjack(player, dealer, deck, bet)
        if result["payout"] > 0:
            await db.add_coins(message.from_user.id, result["payout"], "Blackjack win")
        await db.record_game(
            message.from_user.id, "blackjack", bet,
            result["outcome"], result["payout"], f"Player:{player_score} Dealer:{result['dealer_score']}"
        )
        user = await db.get_user(message.from_user.id)
        
        text = get_string(lang, "blackjack_result",
                         player_cards=format_cards(result["player"]),
                         player_score=result["player_score"],
                         dealer_cards=format_cards(result["dealer"]),
                         dealer_score=result["dealer_score"],
                         outcome_emoji="🃏",
                         outcome_text=get_string(lang, "blackjack_natural", payout=result["payout"]),
                         payout_text="",
                         balance=user["coins"])
        await message.answer(text, parse_mode="Markdown", reply_markup=play_again_keyboard(lang, "blackjack"))
        await state.clear()
        return
    
    await state.update_data(
        bj_player=player,
        bj_dealer=dealer,
        bj_deck=deck,
        bj_bet=bet,
        bj_doubled=False,
    )
    await state.set_state(GameStates.blackjack_playing)
    
    text = get_string(lang, "blackjack_start",
                     player_cards=format_cards(player),
                     player_score=player_score,
                     dealer_card=dealer[0])
    
    can_double = True  # Can double on first two cards
    await message.answer(text, parse_mode="Markdown", reply_markup=blackjack_keyboard(lang, can_double))


@router.callback_query(F.data.startswith("bj:"), GameStates.blackjack_playing)
async def cb_blackjack(callback: CallbackQuery, db: Database, state: FSMContext):
    action = callback.data.split(":")[1]
    data = await state.get_data()
    lang = data.get("lang", "ru")
    
    player = data["bj_player"]
    dealer = data["bj_dealer"]
    deck = data["bj_deck"]
    bet = data["bj_bet"]
    doubled = data.get("bj_doubled", False)
    
    if action == "hit":
        player, deck, score = blackjack_hit(player, deck)
        
        if score > 21:
            # Bust
            await db.record_game(
                callback.from_user.id, "blackjack", bet,
                "bust", 0, f"Player:{score} BUST"
            )
            user = await db.get_user(callback.from_user.id)
            text = get_string(lang, "blackjack_result",
                             player_cards=format_cards(player),
                             player_score=score,
                             dealer_cards=format_cards(dealer),
                             dealer_score=hand_score(dealer),
                             outcome_emoji="💥",
                             outcome_text=get_string(lang, "blackjack_bust"),
                             payout_text=get_string(lang, "blackjack_loss", bet=bet),
                             balance=user["coins"])
            await callback.message.edit_text(text, parse_mode="Markdown",
                                            reply_markup=play_again_keyboard(lang, "blackjack"))
            await state.clear()
        else:
            await state.update_data(bj_player=player, bj_deck=deck)
            text = get_string(lang, "blackjack_start",
                             player_cards=format_cards(player),
                             player_score=score,
                             dealer_card=dealer[0])
            await callback.message.edit_text(text, parse_mode="Markdown",
                                            reply_markup=blackjack_keyboard(lang, False))
    
    elif action == "double":
        # Double down: double bet, take one card, then stand
        user = await db.get_user(callback.from_user.id)
        if user["coins"] >= bet:
            await db.deduct_coins(callback.from_user.id, bet, "Blackjack double down")
            bet = bet * 2
            doubled = True
        
        player, deck, score = blackjack_hit(player, deck)
        
        if score > 21:
            await db.record_game(callback.from_user.id, "blackjack", bet, "bust", 0, f"Player:{score} BUST DD")
            user = await db.get_user(callback.from_user.id)
            text = get_string(lang, "blackjack_result",
                             player_cards=format_cards(player), player_score=score,
                             dealer_cards=format_cards(dealer), dealer_score=hand_score(dealer),
                             outcome_emoji="💥", outcome_text=get_string(lang, "blackjack_bust"),
                             payout_text=get_string(lang, "blackjack_loss", bet=bet),
                             balance=user["coins"])
            await callback.message.edit_text(text, parse_mode="Markdown",
                                            reply_markup=play_again_keyboard(lang, "blackjack"))
            await state.clear()
            await callback.answer()
            return
        
        # Force stand after double
        await state.update_data(bj_player=player, bj_deck=deck, bj_bet=bet, bj_doubled=True)
        action = "stand"  # Fall through to stand logic
    
    if action == "stand":
        data = await state.get_data()
        player = data["bj_player"]
        dealer = data["bj_dealer"]
        deck = data["bj_deck"]
        bet = data["bj_bet"]
        
        result = resolve_blackjack(player, dealer, deck, bet)
        
        if result["payout"] > 0:
            await db.add_coins(callback.from_user.id, result["payout"], f"Blackjack {result['outcome']}")
        
        await db.record_game(
            callback.from_user.id, "blackjack", bet,
            result["outcome"], result["payout"],
            f"Player:{result['player_score']} Dealer:{result['dealer_score']}"
        )
        
        user = await db.get_user(callback.from_user.id)
        
        outcome_map = {
            "win": ("🎉", get_string(lang, "blackjack_win", payout=result["payout"])),
            "loss": ("😔", get_string(lang, "blackjack_loss", bet=bet)),
            "push": ("🤝", get_string(lang, "blackjack_push")),
            "blackjack": ("🃏", get_string(lang, "blackjack_natural", payout=result["payout"])),
            "bust": ("💥", get_string(lang, "blackjack_bust")),
        }
        emoji, outcome_text = outcome_map.get(result["outcome"], ("❓", "Unknown"))
        
        text = get_string(lang, "blackjack_result",
                         player_cards=format_cards(result["player"]),
                         player_score=result["player_score"],
                         dealer_cards=format_cards(result["dealer"]),
                         dealer_score=result["dealer_score"],
                         outcome_emoji=emoji,
                         outcome_text=outcome_text,
                         payout_text="",
                         balance=user["coins"])
        
        await callback.message.edit_text(text, parse_mode="Markdown",
                                        reply_markup=play_again_keyboard(lang, "blackjack"))
        await state.clear()
    
    await callback.answer()
