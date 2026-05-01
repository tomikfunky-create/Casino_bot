"""Manual payment handlers — no Stars needed."""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from database import Database
from config import Config
from locales.strings import get_string
from utils.keyboards import main_menu, deposit_keyboard

logger = logging.getLogger(__name__)
router = Router()


class PaymentStates(StatesGroup):
    waiting_screenshot = State()


# ─── DEPOSIT MENU ─────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("deposit:"))
async def cb_deposit(callback: CallbackQuery, db: Database, config: Config, state: FSMContext):
    _, amount_str, coins_str = callback.data.split(":")
    amount = amount_str
    coins = int(coins_str)

    user = await db.get_user(callback.from_user.id)
    lang = user["language"] if user else "ru"

    await state.update_data(pending_coins=coins, pending_amount=amount, lang=lang)
    await state.set_state(PaymentStates.waiting_screenshot)

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅ Я оплатил / I paid",
            callback_data=f"paid_confirm:{coins}"
        )
    )
    builder.row(
        InlineKeyboardButton(text="❌ Отмена / Cancel", callback_data="paid_cancel")
    )

    if lang == "ru":
        text = (
            f"💳 *Пополнение на {coins} монет*\n\n"
            f"Переведи *{amount} {config.CURRENCY}* на реквизиты:\n\n"
            f"{config.PAYMENT_DETAILS}\n\n"
            f"⚠️ В комментарии к переводу укажи свой ID:\n"
            f"`{callback.from_user.id}`\n\n"
            f"После оплаты нажми кнопку ниже ↓"
        )
    else:
        text = (
            f"💳 *Deposit {coins} coins*\n\n"
            f"Send *{amount} {config.CURRENCY}* to:\n\n"
            f"{config.PAYMENT_DETAILS}\n\n"
            f"⚠️ Include your ID in the payment comment:\n"
            f"`{callback.from_user.id}`\n\n"
            f"After payment press the button below ↓"
        )

    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data.startswith("paid_confirm:"))
async def cb_paid_confirm(callback: CallbackQuery, db: Database, config: Config, state: FSMContext):
    coins = int(callback.data.split(":")[1])
    user = await db.get_user(callback.from_user.id)
    lang = user["language"] if user else "ru"

    await state.clear()

    user_name = user["full_name"] or user["username"] or f"ID {callback.from_user.id}"

    admin_text = (
        f"💰 *Новая заявка на пополнение!*\n\n"
        f"👤 {user_name}\n"
        f"🆔 ID: `{callback.from_user.id}`\n"
        f"🪙 Монет: *{coins}*\n\n"
        f"Подтверди оплату:"
    )

    confirm_builder = InlineKeyboardBuilder()
    confirm_builder.row(
        InlineKeyboardButton(
            text=f"✅ Зачислить {coins} монет",
            callback_data=f"admin_approve:{callback.from_user.id}:{coins}"
        )
    )
    confirm_builder.row(
        InlineKeyboardButton(
            text="❌ Отклонить",
            callback_data=f"admin_reject:{callback.from_user.id}:{coins}"
        )
    )

    sent_to_admin = False
    for admin_id in config.ADMIN_IDS:
        try:
            await callback.bot.send_message(
                admin_id, admin_text,
                parse_mode="Markdown",
                reply_markup=confirm_builder.as_markup()
            )
            sent_to_admin = True
        except Exception as e:
            logger.error(f"Failed to notify admin {admin_id}: {e}")

    if lang == "ru":
        user_text = (
            "⏳ *Заявка отправлена!*\n\n"
            "Администратор проверит платёж и зачислит монеты.\n"
            "Обычно это занимает до 15 минут. ⌛"
        )
    else:
        user_text = (
            "⏳ *Request sent!*\n\n"
            "Admin will verify your payment and credit coins.\n"
            "Usually takes up to 15 minutes. ⌛"
        )

    await callback.message.edit_text(user_text, parse_mode="Markdown")
    await callback.answer("✅ Заявка отправлена!" if lang == "ru" else "✅ Request sent!")


@router.callback_query(F.data == "paid_cancel")
async def cb_paid_cancel(callback: CallbackQuery, db: Database, config: Config, state: FSMContext):
    await state.clear()
    user = await db.get_user(callback.from_user.id)
    lang = user["language"] if user else "ru"
    text = get_string(lang, "deposit_menu", rate=config.CURRENCY)
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=deposit_keyboard(lang))
    await callback.answer()


# ─── ADMIN: APPROVE ───────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("admin_approve:"))
async def cb_admin_approve(callback: CallbackQuery, db: Database, config: Config):
    if callback.from_user.id not in config.ADMIN_IDS:
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return

    _, user_id_str, coins_str = callback.data.split(":")
    user_id = int(user_id_str)
    coins = int(coins_str)

    user = await db.get_user(user_id)
    if not user:
        await callback.answer("❌ Пользователь не найден", show_alert=True)
        return

    lang = user["language"]

    await db.add_coins(user_id, coins, "Manual deposit approved by admin")
    await db.update_user(user_id, total_deposited=user["total_deposited"] + coins)

    # Referral bonus
    if user["referrer_id"]:
        referrer = await db.get_user(user["referrer_id"])
        if referrer:
            bonus = int(coins * config.REFERRAL_PERCENT)
            await db.add_referral_bonus(user["referrer_id"], bonus, user_id)
            try:
                ref_lang = referrer["language"]
                await callback.bot.send_message(
                    user["referrer_id"],
                    get_string(ref_lang, "referral_bonus_received", amount=bonus),
                    parse_mode="Markdown",
                )
            except Exception:
                pass

    updated_user = await db.get_user(user_id)

    if lang == "ru":
        user_text = (
            f"✅ *Монеты зачислены!*\n\n"
            f"🪙 Зачислено: *{coins} монет*\n"
            f"💰 Твой баланс: *{updated_user['coins']} монет*\n\n"
            f"Удачи в игре! 🎰"
        )
    else:
        user_text = (
            f"✅ *Coins credited!*\n\n"
            f"🪙 Added: *{coins} coins*\n"
            f"💰 Your balance: *{updated_user['coins']} coins*\n\n"
            f"Good luck! 🎰"
        )

    try:
        await callback.bot.send_message(
            user_id, user_text, parse_mode="Markdown",
            reply_markup=main_menu(lang)
        )
    except Exception:
        pass

    await callback.message.edit_text(
        callback.message.text + f"\n\n✅ *Одобрено администратором* — зачислено {coins} монет",
        parse_mode="Markdown"
    )
    await callback.answer("✅ Монеты зачислены!")


# ─── ADMIN: REJECT ────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("admin_reject:"))
async def cb_admin_reject(callback: CallbackQuery, db: Database, config: Config):
    if callback.from_user.id not in config.ADMIN_IDS:
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return

    _, user_id_str, coins_str = callback.data.split(":")
    user_id = int(user_id_str)
    coins = int(coins_str)

    user = await db.get_user(user_id)
    lang = user["language"] if user else "ru"

    if lang == "ru":
        user_text = (
            f"❌ *Платёж не подтверждён*\n\n"
            f"Заявка на {coins} монет отклонена.\n"
            f"Если ты уверен что оплатил — напиши администратору."
        )
    else:
        user_text = (
            f"❌ *Payment not confirmed*\n\n"
            f"Request for {coins} coins was rejected.\n"
            f"If you're sure you paid — contact admin."
        )

    try:
        await callback.bot.send_message(user_id, user_text, parse_mode="Markdown")
    except Exception:
        pass

    await callback.message.edit_text(
        callback.message.text + "\n\n❌ *Отклонено*",
        parse_mode="Markdown"
    )
    await callback.answer("❌ Заявка отклонена")


# ─── ADMIN: MANUAL TOPUP COMMAND ──────────────────────────────────────────────

@router.message(F.text.startswith("/topup"))
async def cmd_topup(message: Message, db: Database, config: Config):
    """/topup <user_id> <coins>"""
    if message.from_user.id not in config.ADMIN_IDS:
        return

    parts = message.text.split()
    if len(parts) != 3:
        await message.answer("Использование: /topup <user_id> <coins>\nПример: /topup 123456789 500")
        return

    try:
        user_id = int(parts[1])
        coins = int(parts[2])
    except ValueError:
        await message.answer("❌ Неверный формат. Пример: /topup 123456789 500")
        return

    user = await db.get_user(user_id)
    if not user:
        await message.answer(f"❌ Пользователь {user_id} не найден")
        return

    await db.add_coins(user_id, coins, "Admin manual top-up")
    updated = await db.get_user(user_id)
    lang = user["language"]

    await message.answer(
        f"✅ Зачислено *{coins} монет* пользователю `{user_id}`\n"
        f"💰 Новый баланс: *{updated['coins']} монет*",
        parse_mode="Markdown"
    )

    try:
        if lang == "ru":
            user_text = f"✅ Администратор зачислил *{coins} монет*\n💰 Баланс: *{updated['coins']} монет*"
        else:
            user_text = f"✅ Admin credited *{coins} coins*\n💰 Balance: *{updated['coins']} coins*"
        await message.bot.send_message(user_id, user_text, parse_mode="Markdown")
    except Exception:
        pass
