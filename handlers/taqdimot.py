from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command

from config import PRICES, DESIGN_THEMES
from database import get_balance, deduct_balance, create_order
from keyboards import (
    slides_count_kb, design_theme_kb, images_kb,
    language_kb, confirm_kb, cancel_kb, main_menu
)
from handlers.start import require_subscription

router = Router()


# ═══════════════════════════════════════════════════════════
#  FSM HOLATLARI
# ═══════════════════════════════════════════════════════════

class TaqdimotStates(StatesGroup):
    waiting_topic = State()
    waiting_author = State()
    waiting_slides = State()
    waiting_slides_custom = State()
    waiting_theme = State()
    waiting_images = State()
    waiting_language = State()
    confirm = State()


# ═══════════════════════════════════════════════════════════
#  NARX HISOBLASH
# ═══════════════════════════════════════════════════════════

def calc_price(slides: int) -> int:
    """Slaydlar soniga qarab narx hisoblash."""
    if slides <= 10:
        return PRICES["taqdimot_min"]
    elif slides <= 20:
        return 4500
    else:
        return PRICES["taqdimot_max"]


# ═══════════════════════════════════════════════════════════
#  BOSHLASH
# ═══════════════════════════════════════════════════════════

@router.message(F.text == "📕 Taqdimot")
@router.message(Command("new"))
async def start_taqdimot(message: Message, bot: Bot, state: FSMContext):
    if not await require_subscription(message, bot):
        return

    await state.clear()
    await state.set_state(TaqdimotStates.waiting_topic)
    await message.answer(
        "📕 <b>TAQDIMOT TAYYORLASH</b>\n\n"
        "📋 <b>Narx:</b> 4 000 – 5 000 so'm (6–30 slayd)\n\n"
        "✏️ Taqdimot mavzusini yozing:\n\n"
        "<i>💡 Mavzuni to'liq va aniq yozing — sifat shunga bog'liq!</i>",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )


# ═══════════════════════════════════════════════════════════
#  MAVZU
# ═══════════════════════════════════════════════════════════

@router.message(TaqdimotStates.waiting_topic)
async def get_topic(message: Message, state: FSMContext):
    topic = message.text.strip()
    if len(topic) < 3:
        await message.answer("❌ Mavzu juda qisqa. Iltimos, to'liqroq yozing:")
        return
    if len(topic) > 300:
        await message.answer("❌ Mavzu juda uzun (300 belgidan oshmasin):")
        return

    await state.update_data(topic=topic)
    await state.set_state(TaqdimotStates.waiting_author)
    await message.answer(
        f"✅ Mavzu: <b>{topic}</b>\n\n"
        f"👤 Muallif ism-familiyasini yozing:\n"
        f"<i>(Masalan: Alisher Nazarov)</i>",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )


# ═══════════════════════════════════════════════════════════
#  MUALLIF
# ═══════════════════════════════════════════════════════════

@router.message(TaqdimotStates.waiting_author)
async def get_author(message: Message, state: FSMContext):
    author = message.text.strip()
    if len(author) < 2:
        await message.answer("❌ Ism juda qisqa. Qaytadan yozing:")
        return

    await state.update_data(author=author)
    await state.set_state(TaqdimotStates.waiting_slides)
    await message.answer(
        f"✅ Muallif: <b>{author}</b>\n\n"
        f"📊 Nechta slayd kerak? (6–30):",
        reply_markup=slides_count_kb(),
        parse_mode="HTML"
    )


# ═══════════════════════════════════════════════════════════
#  SLAYDLAR SONI — tugma
# ═══════════════════════════════════════════════════════════

@router.callback_query(F.data.startswith("slides_"), TaqdimotStates.waiting_slides)
async def get_slides(call: CallbackQuery, state: FSMContext):
    value = call.data.replace("slides_", "")

    if value == "custom":
        await state.set_state(TaqdimotStates.waiting_slides_custom)
        await call.message.edit_text(
            "✏️ Slaydlar sonini kiriting (6 dan 30 gacha):",
            reply_markup=cancel_kb()
        )
        await call.answer()
        return

    slides = int(value)
    await state.update_data(slides=slides)
    await state.set_state(TaqdimotStates.waiting_theme)
    await call.message.edit_text(
        f"✅ Slaydlar soni: <b>{slides}</b>\n\n"
        f"🎨 Dizayn shablonini tanlang:",
        reply_markup=design_theme_kb(),
        parse_mode="HTML"
    )
    await call.answer()


# ═══════════════════════════════════════════════════════════
#  SLAYDLAR SONI — qo'lda kiritish
# ═══════════════════════════════════════════════════════════

@router.message(TaqdimotStates.waiting_slides_custom)
async def get_slides_custom(message: Message, state: FSMContext):
    try:
        slides = int(message.text.strip())
        if not 6 <= slides <= 30:
            await message.answer("❌ 6 dan 30 gacha bo'lgan son kiriting:")
            return
    except ValueError:
        await message.answer("❌ Faqat raqam kiriting (6–30):")
        return

    await state.update_data(slides=slides)
    await state.set_state(TaqdimotStates.waiting_theme)
    await message.answer(
        f"✅ Slaydlar soni: <b>{slides}</b>\n\n"
        f"🎨 Dizayn shablonini tanlang:",
        reply_markup=design_theme_kb(),
        parse_mode="HTML"
    )


# ═══════════════════════════════════════════════════════════
#  DIZAYN TANLASH
# ═══════════════════════════════════════════════════════════

@router.callback_query(F.data.startswith("theme_"), TaqdimotStates.waiting_theme)
async def get_theme(call: CallbackQuery, state: FSMContext):
    idx = int(call.data.replace("theme_", ""))
    theme = DESIGN_THEMES[idx]

    await state.update_data(theme=theme, theme_idx=idx)
    await state.set_state(TaqdimotStates.waiting_images)
    await call.message.edit_text(
        f"✅ Dizayn: <b>{theme}</b>\n\n"
        f"🖼 Taqdimotga rasm qo'shilsinmi?",
        reply_markup=images_kb(),
        parse_mode="HTML"
    )
    await call.answer()


# ═══════════════════════════════════════════════════════════
#  RASMLAR
# ═══════════════════════════════════════════════════════════

@router.callback_query(F.data.startswith("images_"), TaqdimotStates.waiting_images)
async def get_images(call: CallbackQuery, state: FSMContext):
    with_images = call.data == "images_yes"
    await state.update_data(with_images=with_images)
    await state.set_state(TaqdimotStates.waiting_language)

    await call.message.edit_text(
        f"✅ Rasmlar: <b>{'Ha' if with_images else \"Yo'q\"}</b>\n\n"
        f"🌐 Taqdimot tilini tanlang:",
        reply_markup=language_kb(),
        parse_mode="HTML"
    )
    await call.answer()


# ═══════════════════════════════════════════════════════════
#  TIL TANLASH
# ═══════════════════════════════════════════════════════════

@router.callback_query(F.data.startswith("lang_"), TaqdimotStates.waiting_language)
async def get_language(call: CallbackQuery, state: FSMContext):
    lang = call.data.replace("lang_", "")
    await state.update_data(language=lang)
    await state.set_state(TaqdimotStates.confirm)

    data = await state.get_data()
    price = calc_price(data["slides"])
    balance = await get_balance(call.from_user.id)

    balance_info = (
        f"✅ Balansingiz yetarli ({balance:,} so'm)"
        if balance >= price
        else f"❌ Balansingiz yetarli emas ({balance:,} so'm). /buy orqali to'ldiring."
    )

    summary = (
        f"📋 <b>TASDIQLASH</b>\n\n"
        f"📌 Mavzu: <b>{data['topic']}</b>\n"
        f"👤 Muallif: <b>{data['author']}</b>\n"
        f"📊 Slaydlar: <b>{data['slides']} ta</b>\n"
        f"🎨 Dizayn: <b>{data['theme']}</b>\n"
        f"🖼 Rasmlar: <b>{'Ha' if data['with_images'] else \"Yo'q\"}</b>\n"
        f"🌐 Til: <b>{lang}</b>\n\n"
        f"💰 Narx: <b>{price:,} so'm</b>\n"
        f"{balance_info}"
    )

    await call.message.edit_text(
        summary,
        reply_markup=confirm_kb("taqdimot_confirm", "taqdimot_cancel"),
        parse_mode="HTML"
    )
    await call.answer()


# ═══════════════════════════════════════════════════════════
#  TASDIQLASH VA YARATISH
# ═══════════════════════════════════════════════════════════

@router.callback_query(F.data == "taqdimot_confirm", TaqdimotStates.confirm)
async def confirm_taqdimot(call: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    price = calc_price(data["slides"])
    user_id = call.from_user.id

    # Balans tekshiruvi
    if not await deduct_balance(user_id, price):
        await call.answer(
            "❌ Balansingiz yetarli emas! /buy orqali to'ldiring.",
            show_alert=True
        )
        return

    await call.message.edit_text(
        "⏳ <b>Taqdimot tayyorlanmoqda...</b>\n\n"
        "🔄 Iltimos, bir oz kuting (30–60 soniya).",
        parse_mode="HTML"
    )
    await state.clear()

    # Generator chaqirish
    try:
        from generators.pptx_generator import generate_presentation
        file_path = await generate_presentation(data, user_id)

        # Faylni yuborish
        from aiogram.types import FSInputFile
        doc = FSInputFile(file_path)
        await bot.send_document(
            user_id,
            doc,
            caption=(
                f"✅ <b>Taqdimot tayyor!</b>\n\n"
                f"📌 Mavzu: <b>{data['topic']}</b>\n"
                f"📊 Slaydlar: <b>{data['slides']} ta</b>\n"
                f"🌐 Til: <b>{data['language']}</b>\n\n"
                f"💡 Faylni <b>WPS Office</b> yoki kompyuterda oching."
            ),
            parse_mode="HTML"
        )

        # Buyurtmani saqlash
        await create_order(
            user_id=user_id,
            order_type="taqdimot",
            details=f"{data['topic']} | {data['slides']} slayd | {data['language']}",
            price=price
        )

        # Cleanup
        import os
        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as e:
        # Xato bo'lsa pulni qaytarish
        from database import update_balance
        await update_balance(user_id, price)
        await bot.send_message(
            user_id,
            f"❌ <b>Xato yuz berdi!</b>\n\nPulingiz qaytarildi.\nQaytadan urinib ko'ring: /new",
            parse_mode="HTML"
        )
        raise e

    await bot.send_message(user_id, "⬇️ Bosh menyu:", reply_markup=main_menu())


@router.callback_query(F.data == "taqdimot_cancel")
async def cancel_taqdimot(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(
        "❌ Taqdimot yaratish bekor qilindi.",
        reply_markup=None
    )
    await call.answer()
    await call.message.answer("⬇️ Bosh menyu:", reply_markup=main_menu())
