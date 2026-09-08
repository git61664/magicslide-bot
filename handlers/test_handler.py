from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command

from config import PRICES, TEST_LEVELS
from database import get_balance, deduct_balance, create_order, update_balance
from keyboards import (
    test_level_kb, test_count_kb, language_kb,
    confirm_kb, cancel_kb, main_menu
)
from handlers.start import require_subscription

router = Router()


# ═══════════════════════════════════════════════════════════
#  FSM HOLATLARI
# ═══════════════════════════════════════════════════════════

class TestStates(StatesGroup):
    waiting_topic = State()
    waiting_author = State()
    waiting_language = State()
    waiting_level = State()
    waiting_count = State()
    waiting_count_custom = State()
    confirm = State()


# ═══════════════════════════════════════════════════════════
#  NARX HISOBLASH
# ═══════════════════════════════════════════════════════════

def calc_price(count: int) -> int:
    """Har 10 ta savol = 2000 so'm."""
    import math
    blocks = math.ceil(count / 10)
    return blocks * PRICES["test_per_10"]


# ═══════════════════════════════════════════════════════════
#  BOSHLASH
# ═══════════════════════════════════════════════════════════

@router.message(F.text == "📝 Test yaratish")
@router.message(Command("test"))
async def start_test(message: Message, bot: Bot, state: FSMContext):
    if not await require_subscription(message, bot):
        return

    await state.clear()
    await state.set_state(TestStates.waiting_topic)
    await message.answer(
        "📝 <b>TEST YARATISH</b>\n\n"
        "📋 <b>Narx:</b> har 10 ta savol — 2 000 so'm (10–50 savol)\n"
        "✅ Har bir savol 4 variantli. Javoblar kaliti oxirida beriladi.\n\n"
        "✏️ Test mavzusini yozing:\n\n"
        "<i>💡 Mavzuni to'liq va aniq yozing!</i>",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )


# ═══════════════════════════════════════════════════════════
#  MAVZU
# ═══════════════════════════════════════════════════════════

@router.message(TestStates.waiting_topic)
async def get_topic(message: Message, state: FSMContext):
    topic = message.text.strip()
    if len(topic) < 3:
        await message.answer("❌ Mavzu juda qisqa. To'liqroq yozing:")
        return
    if len(topic) > 300:
        await message.answer("❌ Mavzu juda uzun (300 belgidan oshmasin):")
        return

    await state.update_data(topic=topic)
    await state.set_state(TestStates.waiting_author)
    await message.answer(
        f"✅ Mavzu: <b>{topic}</b>\n\n"
        f"👤 Tuzuvchi ism-familiyasini yozing:",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )


# ═══════════════════════════════════════════════════════════
#  TUZUVCHI
# ═══════════════════════════════════════════════════════════

@router.message(TestStates.waiting_author)
async def get_author(message: Message, state: FSMContext):
    author = message.text.strip()
    await state.update_data(author=author)
    await state.set_state(TestStates.waiting_language)
    await message.answer(
        f"✅ Tuzuvchi: <b>{author}</b>\n\n"
        f"🌐 Test tilini tanlang:",
        reply_markup=language_kb(),
        parse_mode="HTML"
    )


# ═══════════════════════════════════════════════════════════
#  TIL
# ═══════════════════════════════════════════════════════════

@router.callback_query(F.data.startswith("lang_"), TestStates.waiting_language)
async def get_language(call: CallbackQuery, state: FSMContext):
    lang = call.data.replace("lang_", "")
    await state.update_data(language=lang)
    await state.set_state(TestStates.waiting_level)
    await call.message.edit_text(
        f"✅ Til: <b>{lang}</b>\n\n"
        f"📊 Qiyinlik darajasini tanlang:",
        reply_markup=test_level_kb(),
        parse_mode="HTML"
    )
    await call.answer()


# ═══════════════════════════════════════════════════════════
#  DARAJA
# ═══════════════════════════════════════════════════════════

@router.callback_query(F.data.startswith("level_"), TestStates.waiting_level)
async def get_level(call: CallbackQuery, state: FSMContext):
    level = call.data.replace("level_", "")
    await state.update_data(level=level)
    await state.set_state(TestStates.waiting_count)
    await call.message.edit_text(
        f"✅ Daraja: <b>{level}</b>\n\n"
        f"🔢 Savollar sonini tanlang (10–50):",
        reply_markup=test_count_kb(),
        parse_mode="HTML"
    )
    await call.answer()


# ═══════════════════════════════════════════════════════════
#  SAVOLLAR SONI — tugma
# ═══════════════════════════════════════════════════════════

@router.callback_query(F.data.startswith("tcount_"), TestStates.waiting_count)
async def get_count(call: CallbackQuery, state: FSMContext):
    value = call.data.replace("tcount_", "")

    if value == "custom":
        await state.set_state(TestStates.waiting_count_custom)
        await call.message.edit_text(
            "✏️ Savollar sonini kiriting (10 dan 50 gacha):",
            reply_markup=cancel_kb()
        )
        await call.answer()
        return

    count = int(value)
    await _show_test_confirm(call.message, state, count, call.from_user.id)
    await call.answer()


# ═══════════════════════════════════════════════════════════
#  SAVOLLAR SONI — qo'lda
# ═══════════════════════════════════════════════════════════

@router.message(TestStates.waiting_count_custom)
async def get_count_custom(message: Message, state: FSMContext):
    try:
        count = int(message.text.strip())
        if not 10 <= count <= 50:
            await message.answer("❌ 10 dan 50 gacha son kiriting:")
            return
    except ValueError:
        await message.answer("❌ Faqat raqam kiriting (10–50):")
        return

    await _show_test_confirm(message, state, count, message.from_user.id)


# ═══════════════════════════════════════════════════════════
#  TASDIQLASH EKRANI
# ═══════════════════════════════════════════════════════════

async def _show_test_confirm(msg, state: FSMContext, count: int, user_id: int):
    await state.update_data(count=count)
    await state.set_state(TestStates.confirm)

    data = await state.get_data()
    price = calc_price(count)
    balance = await get_balance(user_id)

    balance_info = (
        f"✅ Balansingiz yetarli ({balance:,} so'm)"
        if balance >= price
        else f"❌ Balansingiz yetarli emas ({balance:,} so'm). /buy orqali to'ldiring."
    )

    summary = (
        f"📋 <b>TASDIQLASH</b>\n\n"
        f"📌 Mavzu: <b>{data['topic']}</b>\n"
        f"👤 Tuzuvchi: <b>{data['author']}</b>\n"
        f"🌐 Til: <b>{data['language']}</b>\n"
        f"📊 Daraja: <b>{data['level']}</b>\n"
        f"🔢 Savollar: <b>{count} ta</b>\n\n"
        f"💰 Narx: <b>{price:,} so'm</b>\n"
        f"{balance_info}"
    )

    kb = confirm_kb("test_confirm", "test_cancel")
    if hasattr(msg, "edit_text"):
        await msg.edit_text(summary, reply_markup=kb, parse_mode="HTML")
    else:
        await msg.answer(summary, reply_markup=kb, parse_mode="HTML")


# ═══════════════════════════════════════════════════════════
#  TASDIQLASH VA YARATISH
# ═══════════════════════════════════════════════════════════

@router.callback_query(F.data == "test_confirm", TestStates.confirm)
async def confirm_test(call: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    price = calc_price(data["count"])
    user_id = call.from_user.id

    if not await deduct_balance(user_id, price):
        await call.answer(
            "❌ Balansingiz yetarli emas! /buy orqali to'ldiring.",
            show_alert=True
        )
        return

    await call.message.edit_text(
        "⏳ <b>Test tayyorlanmoqda...</b>\n\n"
        f"🔄 {data['count']} ta savol generatsiya qilinmoqda...",
        parse_mode="HTML"
    )
    await state.clear()

    try:
        from generators.docx_generator import generate_test
        file_path = await generate_test(data, user_id)

        from aiogram.types import FSInputFile
        doc = FSInputFile(file_path)
        await bot.send_document(
            user_id,
            doc,
            caption=(
                f"✅ <b>Test tayyor!</b>\n\n"
                f"📌 Mavzu: <b>{data['topic']}</b>\n"
                f"🔢 Savollar: <b>{data['count']} ta</b>\n"
                f"📊 Daraja: <b>{data['level']}</b>\n"
                f"🌐 Til: <b>{data['language']}</b>\n\n"
                f"✅ Javoblar kaliti faylning oxirida."
            ),
            parse_mode="HTML"
        )

        await create_order(
            user_id=user_id,
            order_type="test",
            details=f"{data['topic']} | {data['count']} savol | {data['level']}",
            price=price
        )

        import os
        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as e:
        await update_balance(user_id, price)
        await bot.send_message(
            user_id,
            "❌ <b>Xato yuz berdi!</b>\n\nPulingiz qaytarildi.",
            parse_mode="HTML"
        )
        raise e

    await bot.send_message(user_id, "⬇️ Bosh menyu:", reply_markup=main_menu())


@router.callback_query(F.data == "test_cancel")
async def cancel_test(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("❌ Test yaratish bekor qilindi.", reply_markup=None)
    await call.answer()
    await call.message.answer("⬇️ Bosh menyu:", reply_markup=main_menu())
