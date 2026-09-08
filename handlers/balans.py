from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command

from config import ADMIN_ID, CARD_NUMBER, CARD_OWNER, REFERAL_BONUS
from database import (
    get_balance, update_balance, get_user, get_referal_count,
    get_referal_earnings, create_payment, approve_payment, reject_payment
)
from keyboards import balance_kb, topup_amount_kb, payment_sent_kb, main_menu

router = Router()

class BalanceStates(StatesGroup):
    waiting_topup_amount = State()
    waiting_payment_check = State()

@router.message(F.text == "💰 Balans")
@router.message(Command("buy"))
async def check_balance(message: Message):
    balance = await get_balance(message.from_user.id)
    user = await get_user(message.from_user.id)
    await message.answer(
        f"💰 <b>BALANS</b>\n\n"
        f"Sizning balansingiz: <b>{balance:,} so'm</b>\n\n"
        f"Balans to'ldirishni xohlaysizmi?",
        reply_markup=balance_kb(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "buy_balance")
async def topup_balance(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        "💳 <b>Nechta so'm to'ldirmoqchisiz?</b>",
        reply_markup=topup_amount_kb(),
        parse_mode="HTML"
    )
    await call.answer()

@router.callback_query(F.data.startswith("topup_"))
async def select_topup(call: CallbackQuery, state: FSMContext):
    value = call.data.replace("topup_", "")
    
    if value == "custom":
        await state.set_state(BalanceStates.waiting_topup_amount)
        await call.message.edit_text("✏️ So'mni kiriting:", parse_mode="HTML")
        await call.answer()
        return
    
    amount = int(value)
    await _process_payment(call.message, state, amount, call.from_user.id, call)

@router.message(BalanceStates.waiting_topup_amount)
async def custom_topup(message: Message, state: FSMContext):
    try:
        amount = int(message.text.strip())
        if amount < 1000:
            await message.answer("❌ Eng kam 1000 so'm kerak.")
            return
        if amount > 1000000:
            await message.answer("❌ Eng ko'p 1 000 000 so'm.")
            return
    except ValueError:
        await message.answer("❌ Faqat raqam kiriting.")
        return
    
    await _process_payment(message, state, amount, message.from_user.id)

async def _process_payment(msg, state: FSMContext, amount: int, user_id: int, call=None):
    await state.update_data(topup_amount=amount)
    await state.set_state(BalanceStates.waiting_payment_check)
    
    text = (
        f"💳 <b>TO'LOV HISOB-KITOBLAR</b>\n\n"
        f"Miqdor: <b>{amount:,} so'm</b>\n\n"
        f"<b>Hisob raqami:</b>\n"
        f"<code>{CARD_NUMBER}</code>\n\n"
        f"<b>Egasi:</b>\n"
        f"{CARD_OWNER}\n\n"
        f"1️⃣ To'lovni amalga oshiring\n"
        f"2️⃣ Chekni tasnifini shu yerga yuboring\n"
        f"3️⃣ Admin tasdiqlash kutib turing"
    )
    
    if call:
        await msg.edit_text(text, reply_markup=payment_sent_kb(), parse_mode="HTML")
        await call.answer()
    else:
        await msg.answer(text, reply_markup=payment_sent_kb(), parse_mode="HTML")

@router.callback_query(F.data == "payment_check_sent", BalanceStates.waiting_payment_check)
async def payment_check_sent(call: CallbackQuery, state: FSMContext):
    await state.set_state(BalanceStates.waiting_payment_check)
    await call.message.edit_text(
        "📷 Chek rasmini yuboring (screenshot yoki foto):",
        parse_mode="HTML"
    )
    await call.answer()

@router.message(BalanceStates.waiting_payment_check)
async def handle_payment_check(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    amount = data.get("topup_amount", 0)
    
    if not message.photo and not message.document:
        await message.answer("❌ Iltimos, rasm yuboring.")
        return
    
    file_id = None
    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.document:
        file_id = message.document.file_id
    
    payment_id = await create_payment(message.from_user.id, amount, file_id)
    await state.clear()
    
    user = await get_user(message.from_user.id)
    
    admin_text = (
        f"💳 <b>YANGI TO'LOV</b>\n\n"
        f"👤 Foydalanuvchi: {user['full_name']}\n"
        f"🆔 ID: <code>{user['user_id']}</code>\n"
        f"💰 Miqdor: <b>{amount:,} so'm</b>\n"
        f"📅 Sana: {message.date}\n\n"
        f"Tasdiqlash uchun /admin ga boring."
    )
    
    try:
        if message.photo:
            await bot.send_photo(ADMIN_ID, file_id, caption=admin_text, parse_mode="HTML")
        else:
            await bot.send_document(ADMIN_ID, file_id, caption=admin_text, parse_mode="HTML")
    except:
        pass
    
    await message.answer(
        "✅ <b>To'lov qabul qilindi!</b>\n\n"
        "Admin tasdiqlash kutib turing. Balans qo'shiladi.",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("admin_approve_"))
async def admin_approve(call: CallbackQuery, bot: Bot):
    if call.from_user.id != ADMIN_ID:
        await call.answer("Ruxsat yo'q", show_alert=True)
        return
    
    parts = call.data.replace("admin_approve_", "").split("_")
    payment_id, user_id = int(parts[0]), int(parts[1])
    
    payment = await approve_payment(payment_id)
    if payment:
        await bot.send_message(
            user_id,
            f"✅ <b>To'lov tasdiqlandi!</b>\n\n"
            f"Balansingiz {payment['amount']:,} so'm ga o'zgartirildi.",
            parse_mode="HTML"
        )
        await call.message.edit_text("✅ Tasdiqlandi.", parse_mode="HTML")
        await call.answer()

@router.callback_query(F.data.startswith("admin_reject_"))
async def admin_reject(call: CallbackQuery, bot: Bot):
    if call.from_user.id != ADMIN_ID:
        await call.answer("Ruxsat yo'q", show_alert=True)
        return
    
    parts = call.data.replace("admin_reject_", "").split("_")
    payment_id, user_id = int(parts[0]), int(parts[1])
    
    await reject_payment(payment_id)
    await bot.send_message(user_id, "❌ To'lov rad etildi. Qaytadan urinib ko'ring.", parse_mode="HTML")
    await call.message.edit_text("❌ Rad etildi.", parse_mode="HTML")
    await call.answer()

@router.callback_query(F.data == "referal_info")
async def referal_info(call: CallbackQuery):
    user_id = call.from_user.id
    count = await get_referal_count(user_id)
    earnings = await get_referal_earnings(user_id)
    link = f"https://t.me/username_here?start=ref{user_id}"
    
    text = (
        f"👥 <b>REFERAL DASTURI</b>\n\n"
        f"🔗 Sizning havolangiz:\n<code>{link}</code>\n\n"
        f"👤 Taklif etilganlar: <b>{count}</b>\n"
        f"💰 Ishlagan bonus: <b>{earnings:,} so'm</b>\n\n"
        f"<b>Bonuslar:</b>\n"
        f"💵 Har taklif: 1 000 so'm\n"
        f"💵 Har buyurtma: 100 so'm\n"
        f"💵 To'lovdan: 5%"
    )
    
    await call.message.edit_text(text, parse_mode="HTML")
    await call.answer()

@router.message(Command("chek"))
async def cmd_chek(message: Message):
    balance = await get_balance(message.from_user.id)
    await message.answer(
        f"📋 <b>TO'LOV CHEKI</b>\n\n"
        f"Sizning balansingiz: <b>{balance:,} so'm</b>\n\n"
        f"Buyurtmalarni /my ga bosib ko'rishingiz mumkin.",
        parse_mode="HTML"
    )
