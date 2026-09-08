from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import PRICES
from database import get_balance, deduct_balance, create_order, update_balance
from keyboards import (
    pages_count_kb, language_kb, confirm_kb,
    cancel_kb, main_menu
)
from handlers.start import require_subscription

router = Router()


# ═══════════════════════════════════════════════════════════
#  FSM HOLATLARI
# ═══════════════════════════════════════════════════════════

class ReferatStates(StatesGroup):
    waiting_topic = State()
    waiting_institution = State()
    waiting_author = State()
    waiting_pages = State()
    waiting_pages_custom = State()
    waiting_language = State()
    confirm = State()


# ═══════════════════════════════════════════════════════════
#  NARX HISOBLASH
# ═══════════════════════════════════════════════════════════

def calc_price(pages: int) -> int:
    if pages <= 10:
        return PRICES["referat_min"]
    elif pages <= 18:
        return 4500
    else:
        return PRICES["referat_max"]


# ═══════════════════════════════════════════════════════════
#  BOSHLASH
# ═══════════════════════════════════════════════════════════

@router.message(F.text == "📘 Referat / Mustaqil ish")
async def start_referat(message: Message, bot: Bot, state: FSMContext):
    if not await require_subscription(message, bot):
        return

    await state.clear()
    await state.set_state(ReferatStates.waiting_topic)
    await message.answer(
        "📘 <b>REFERAT / MUSTAQIL ISH TAYYORLASH</b>\n\n"
        "📋 <b>Narx:</b> 4 000 – 5 000 so'm (5–25 bet)\n\n"
        "✏️ Mavzuni yozing:\n\n"
        "<i>💡 Mavzuni to'liq va aniq yozing!</i>",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )


# ═══════════════════════════════════════════════════════════
#  MAVZU
# ═══════════════════════════════════════════════════════════

@router.message(ReferatStates.waiting_topic)
async def get_topic(message: Message, state: FSMContext):
    topic = message.text.strip()
    if len(topic) < 3:
        await message.answer("❌ Mavzu juda qisqa. To'liqroq yozing:")
        return
    if len(topic) > 300:
        await message.answer("❌ Mavzu juda uzun (300 belgidan oshmasin):")
        return

    await state.update_data(topic=topic)
    await state.set_state(ReferatStates.waiting_institution)
    await message.answer(
        f"✅ Mavzu: <b>{topic}</b>\n\n"
        f"🏫 Muassasa nomini yozing:\n"
        f"<i>(Masalan: TATU, ToshDU, ...)</i>",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )


# ═══════════════════════════════════════════════════════════
#  MUASSASA
# ═══════════════════════════════════════════════════════════

@router.message(ReferatStates.waiting_institution)
async def get_institution(message: Message, state: FSMContext):
    institution = message.text.strip()
    await state.update_data(institution=institution)
    await state.set_state(ReferatStates.waiting_author)
    await message.answer(
        f"✅ Muassasa: <b>{institution}</b>\n\n"
        f"👤 Muallif ism-familiyasini yozing:",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )


# ═══════════════════════════════════════════════════════════
#  MUALLIF
# ═══════════════════════════════════════════════════════════

@router.message(ReferatStates.waiting_author)
async def get_author(message: Message, state: FSMContext):
    author = message.text.strip()
    if len(author) < 2:
        await message.answer("❌ Ism juda qisqa. Qaytadan yozing:")
        return

    await state.update_data(author=author)
    await state.set_state(ReferatStates.waiting_pages)
    await message.answer(
        f"✅ Muallif: <b>{author}</b>\n\n"
        f"📄 Nechta bet kerak? (5–25):",
        reply_markup=pages_count_kb(5, 25),
        parse_mode="HTML"
    )


# ═══════════════════════════════════════════════════════════
#  BET SONI — tugma
# ═══════════════════════════════════════════════════════════

@router.callback_query(F.data.startswith("pages_"), ReferatStates.waiting_pages)
async def get_pages(call: CallbackQuery, state: FSMContext):
    value = call.data.replace("pages_", "")

    if value == "custom":
        await state.set_state(ReferatStates.waiting_pages_custom)
        await call.message.edit_text(
            "✏️ Betlar sonini kiriting (5 dan 25 gacha):",
            reply_markup=cancel_kb()
        )
        await call.answer()
        return

    pages = int(value)
    await state.update_data(pages=pages)
    await state.set_state(ReferatStates.waiting_language)
    await call.message.edit_text(
        f"✅ Betlar soni: <b>{pages}</b>\n\n"
        f"🌐 Hujjat tilini tanlang:",
        reply_markup=language_kb(),
        parse_mode="HTML"
    )
    await call.answer()


# ═══════════════════════════════════════════════════════════
#  BET SONI — qo'lda kiritish
# ═══════════════════════════════════════════════════════════

@router.message(ReferatStates.waiting_pages_custom)
async def get_pages_custom(message: Message, state: FSMContext):
    try:
        pages = int(message.text.strip())
        if not 5 <= pages <= 25:
            await message.answer("❌ 5 dan 25 gacha son kiriting:")
            return
    except ValueError:
        await message.answer("❌ Faqat raqam kiriting (5–25):")
        return

    await state.update_data(pages=pages)
    await state.set_state(ReferatStates.waiting_language)
    await message.answer(
        f"✅ Betlar soni: <b>{pages}</b>\n\n"
        f"🌐 Hujjat tilini tanlang:",
        reply_markup=language_kb(),
        parse_mode="HTML"
    )


# ═══════════════════════════════════════════════════════════
#  TIL TANLASH
# ═══════════════════════════════════════════════════════════

@router.callback_query(F.data.startswith("lang_"), ReferatStates.waiting_language)
async def get_language(call: CallbackQuery, state: FSMContext):
    lang = call.data.replace("lang_", "")
    await state.update_data(language=lang)
    await state.set_state(ReferatStates.confirm)

    data = await state.get_data()
    price = calc_price(data["pages"])
    balance = await get_balance(call.from_user.id)

    balance_info = (
        f"✅ Balansingiz yetarli ({balance:,} so'm)"
        if balance >= price
        else f"❌ Balansingiz yetarli emas ({balance:,} so'm). /buy orqali to'ldiring."
    )

    summary = (
        f"📋 <b>TASDIQLASH</b>\n\n"
        f"📌 Mavzu: <b>{data['topic']}</b>\n"
        f"🏫 Muassasa: <b>{data['institution']}</b>\n"
        f"👤 Muallif: <b>{data['author']}</b>\n"
        f"📄 Betlar: <b>{data['pages']} ta</b>\n"
        f"🌐 Til: <b>{lang}</b>\n\n"
        f"💰 Narx: <b>{price:,} so'm</b>\n"
        f"{balance_info}"
    )

    await call.message.edit_text(
        summary,
        reply_markup=confirm_kb("referat_confirm", "referat_cancel"),
        parse_mode="HTML"
    )
    await call.answer()


# ═══════════════════════════════════════════════════════════
#  TASDIQLASH VA YARATISH
# ═══════════════════════════════════════════════════════════

@router.callback_query(F.data == "referat_confirm", ReferatStates.confirm)
async def confirm_referat(call: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    price = calc_price(data["pages"])
    user_id = call.from_user.id

    if not await deduct_balance(user_id, price):
        await call.answer(
            "❌ Balansingiz yetarli emas! /buy orqali to'ldiring.",
            show_alert=True
        )
        return

    await call.message.edit_text(
        "⏳ <b>Referat tayyorlanmoqda...</b>\n\n"
        "🔄 Iltimos, bir oz kuting (30–60 soniya).",
        parse_mode="HTML"
    )
    await state.clear()

    try:
        from generators.docx_generator import generate_referat
        file_path = await generate_referat(data, user_id)

        from aiogram.types import FSInputFile
        doc = FSInputFile(file_path)
        await bot.send_document(
            user_id,
            doc,
            caption=(
                f"✅ <b>Referat tayyor!</b>\n\n"
                f"📌 Mavzu: <b>{data['topic']}</b>\n"
                f"📄 Betlar: <b>{data['pages']} ta</b>\n"
                f"🌐 Til: <b>{data['language']}</b>\n\n"
                f"💡 Faylni <b>WPS Office</b> yoki kompyuterda oching."
            ),
            parse_mode="HTML"
        )

        await create_order(
            user_id=user_id,
            order_type="referat",
            details=f"{data['topic']} | {data['pages']} bet | {data['language']}",
            price=price
        )

        import os
        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as e:
        await update_balance(user_id, price)
        await bot.send_message(
            user_id,
            "❌ <b>Xato yuz berdi!</b>\n\nPulingiz qaytarildi. Qaytadan urinib ko'ring.",
            parse_mode="HTML"
        )
        raise e

    await bot.send_message(user_id, "⬇️ Bosh menyu:", reply_markup=main_menu())


@router.callback_query(F.data == "referat_cancel")
async def cancel_referat(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("❌ Referat yaratish bekor qilindi.", reply_markup=None)
    await call.answer()
    await call.message.answer("⬇️ Bosh menyu:", reply_markup=main_menu())
