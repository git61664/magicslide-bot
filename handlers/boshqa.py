from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import PRICES
from database import get_balance, deduct_balance, create_order, update_balance
from keyboards import other_works_kb, kurs_ishi_group_kb, language_kb, confirm_kb, cancel_kb, main_menu
from handlers.start import require_subscription

router = Router()

class BoshqaStates(StatesGroup):
    kurs_topic = State()
    kurs_group = State()
    kurs_language = State()
    kurs_confirm = State()
    other_type = State()
    other_topic = State()
    other_language = State()
    other_confirm = State()

OTHER_PRICES = {
    "insho": PRICES["insho"],
    "maqola": PRICES["ilmiy_maqola"],
    "tezis": PRICES["tezis"],
    "keys": PRICES["keys"],
    "glossariy": PRICES["glossariy"],
    "krossvord": PRICES["krossvord"],
}

OTHER_NAMES = {
    "insho": "Insho",
    "maqola": "Ilmiy maqola",
    "tezis": "Tezis",
    "keys": "Keys",
    "glossariy": "Glossariy",
    "krossvord": "Krossvord",
}

@router.message(F.text == "📚 Boshqa ishlar")
async def show_other_works(message: Message, bot: Bot, state: FSMContext):
    if not await require_subscription(message, bot):
        return
    await state.clear()
    await message.answer("📚 BOSHQA ISHLAR\n\nKerakli turni tanlang:", reply_markup=other_works_kb(), parse_mode="HTML")

@router.message(F.text == "🎓 Kurs ishi yaratish")
async def start_kurs(message: Message, bot: Bot, state: FSMContext):
    if not await require_subscription(message, bot):
        return
    await state.clear()
    await state.set_state(BoshqaStates.kurs_topic)
    await message.answer("🎓 KURS ISHI\n\n✏️ Mavzuni yozing:", reply_markup=cancel_kb())

@router.message(BoshqaStates.kurs_topic)
async def kurs_topic(message: Message, state: FSMContext):
    topic = message.text.strip()
    if len(topic) < 3:
        await message.answer("Mavzu juda qisqa.")
        return
    await state.update_data(topic=topic, work_type="kurs_ishi")
    await state.set_state(BoshqaStates.kurs_group)
    await message.answer(f"✅ Mavzu: {topic}\n\nKurs va guruh:", reply_markup=kurs_ishi_group_kb())

@router.callback_query(F.data == "kurs_nogroup", BoshqaStates.kurs_group)
async def kurs_no_group(call: CallbackQuery, state: FSMContext):
    await state.update_data(group="")
    await state.set_state(BoshqaStates.kurs_language)
    await call.message.edit_text("🌐 Til tanlang:", reply_markup=language_kb())
    await call.answer()

@router.message(BoshqaStates.kurs_group)
async def kurs_group_msg(message: Message, state: FSMContext):
    await state.update_data(group=message.text.strip())
    await state.set_state(BoshqaStates.kurs_language)
    await message.answer("🌐 Til tanlang:", reply_markup=language_kb())

@router.callback_query(F.data.startswith("lang_"), BoshqaStates.kurs_language)
async def kurs_lang(call: CallbackQuery, state: FSMContext):
    lang = call.data.replace("lang_", "")
    await state.update_data(language=lang)
    await state.set_state(BoshqaStates.kurs_confirm)
    data = await state.get_data()
    price = PRICES["kurs_ishi_min"]
    balance = await get_balance(call.from_user.id)
    text = f"TASDIQLASH\n\n{data['topic']}\n{lang}\n{price:,} so'm\nBalans: {balance:,} so'm"
    await call.message.edit_text(text, reply_markup=confirm_kb("kurs_confirm", "kurs_cancel"))
    await call.answer()

@router.callback_query(F.data == "kurs_confirm", BoshqaStates.kurs_confirm)
async def confirm_kurs(call: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    price = PRICES["kurs_ishi_min"]
    uid = call.from_user.id
    if not await deduct_balance(uid, price):
        await call.answer("Balans yetarli emas!", show_alert=True)
        return
    await call.message.edit_text("Tayyorlanmoqda...")
    await state.clear()
    try:
        from generators.docx_generator import generate_kurs_ishi
        fpath = await generate_kurs_ishi(data, uid)
        from aiogram.types import FSInputFile
        await bot.send_document(uid, FSInputFile(fpath), caption=f"✅ Tayyor: {data['topic']}")
        await create_order(uid, "kurs_ishi", f"{data['topic']} | {data['language']}", price)
        import os
        if os.path.exists(fpath): os.remove(fpath)
    except Exception as e:
        await update_balance(uid, price)
        raise e
    await bot.send_message(uid, "Menyu:", reply_markup=main_menu())

@router.callback_query(F.data == "kurs_cancel")
async def cancel_kurs(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("Bekor qilindi.")
    await call.message.answer("Menyu:", reply_markup=main_menu())

@router.callback_query(F.data.startswith("other_"))
async def select_other(call: CallbackQuery, state: FSMContext):
    wtype = call.data.replace("other_", "")
    if wtype not in OTHER_NAMES:
        return
    await state.clear()
    await state.update_data(work_type=wtype)
    await state.set_state(BoshqaStates.other_topic)
    price = OTHER_PRICES[wtype]
    name = OTHER_NAMES[wtype]
    await call.message.edit_text(f"{name}\n{price:,} so'm\n\n✏️ Mavzuni yozing:", reply_markup=cancel_kb())
    await call.answer()

@router.message(BoshqaStates.other_topic)
async def other_topic(message: Message, state: FSMContext):
    topic = message.text.strip()
    if len(topic) < 3:
        await message.answer("Mavzu juda qisqa.")
        return
    await state.update_data(topic=topic)
    await state.set_state(BoshqaStates.other_language)
    await message.answer("🌐 Til tanlang:", reply_markup=language_kb())

@router.callback_query(F.data.startswith("lang_"), BoshqaStates.other_language)
async def other_lang(call: CallbackQuery, state: FSMContext):
    lang = call.data.replace("lang_", "")
    await state.update_data(language=lang)
    await state.set_state(BoshqaStates.other_confirm)
    data = await state.get_data()
    wtype = data["work_type"]
    price = OTHER_PRICES[wtype]
    name = OTHER_NAMES[wtype]
    balance = await get_balance(call.from_user.id)
    text = f"TASDIQLASH\n\n{name}\n{data['topic']}\n{lang}\n{price:,} so'm\nBalans: {balance:,} so'm"
    await call.message.edit_text(text, reply_markup=confirm_kb("other_confirm", "other_cancel"))
    await call.answer()

@router.callback_query(F.data == "other_confirm", BoshqaStates.other_confirm)
async def confirm_other(call: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    wtype = data["work_type"]
    price = OTHER_PRICES[wtype]
    uid = call.from_user.id
    if not await deduct_balance(uid, price):
        await call.answer("Balans yetarli emas!", show_alert=True)
        return
    await call.message.edit_text("Tayyorlanmoqda...")
    await state.clear()
    try:
        from generators.docx_generator import generate_other_work
        fpath = await generate_other_work(data, uid)
        from aiogram.types import FSInputFile
        await bot.send_document(uid, FSInputFile(fpath), caption=f"✅ {OTHER_NAMES[wtype]}: {data['topic']}")
        await create_order(uid, wtype, f"{data['topic']} | {data['language']}", price)
        import os
        if os.path.exists(fpath): os.remove(fpath)
    except Exception as e:
        await update_balance(uid, price)
        raise e
    await bot.send_message(uid, "Menyu:", reply_markup=main_menu())

@router.callback_query(F.data == "other_cancel")
async def cancel_other(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("Bekor qilindi.")
    await call.message.answer("Menyu:", reply_markup=main_menu())
