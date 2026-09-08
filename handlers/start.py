from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import CHANNELS, ADMIN_ID, CARD_NUMBER, CARD_OWNER
from database import register_user, get_user, get_balance, get_stats, get_pending_payments
from keyboards import (
    main_menu, channel_subscription_kb, admin_panel_kb, balance_kb
)

router = Router()


# ═══════════════════════════════════════════════════════════
#  KANAL OBUNA TEKSHIRUVI
# ═══════════════════════════════════════════════════════════

async def check_subscription(bot: Bot, user_id: int) -> bool:
    """Foydalanuvchi barcha kanallarga a'zo ekanligini tekshiradi."""
    if not CHANNELS:
        return True
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(channel, user_id)
            if member.status in ("left", "kicked", "banned"):
                return False
        except Exception:
            return False
    return True


async def require_subscription(message: Message, bot: Bot) -> bool:
    """Obuna yo'q bo'lsa xabar yuboradi va False qaytaradi."""
    if not await check_subscription(bot, message.from_user.id):
        await message.answer(
            "⚠️ <b>Botdan foydalanish uchun quyidagi kanallarga a'zo bo'lishingiz shart!</b>\n\n"
            "A'zo bo'lgach <b>✅ A'zo bo'ldim</b> tugmasini bosing.",
            reply_markup=channel_subscription_kb(CHANNELS),
            parse_mode="HTML"
        )
        return False
    return True


# ═══════════════════════════════════════════════════════════
#  /start KOMANDASI
# ═══════════════════════════════════════════════════════════

@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot, state: FSMContext):
    await state.clear()
    user = message.from_user

    # Referal parametr tekshiruvi
    args = message.text.split()
    referal_by = None
    if len(args) > 1:
        try:
            ref_id = int(args[1].replace("ref", ""))
            if ref_id != user.id:
                referal_by = ref_id
        except ValueError:
            pass

    # Foydalanuvchini ro'yxatdan o'tkazish
    is_new = await register_user(
        user_id=user.id,
        username=user.username or "",
        full_name=user.full_name,
        referal_by=referal_by
    )

    # Kanal obuna tekshiruvi
    if CHANNELS and not await check_subscription(bot, user.id):
        await message.answer(
            "👋 Salom!\n\n"
            "⚠️ <b>Botdan foydalanish uchun avval quyidagi kanallarga a'zo bo'ling:</b>",
            reply_markup=channel_subscription_kb(CHANNELS),
            parse_mode="HTML"
        )
        return

    # Referal xabar
    if is_new and referal_by:
        try:
            await bot.send_message(
                referal_by,
                f"🎉 Siz taklif qilgan foydalanuvchi botga qo'shildi!\n"
                f"💰 Hisobingizga <b>1 000 so'm</b> bonus qo'shildi.",
                parse_mode="HTML"
            )
        except Exception:
            pass

    await send_welcome(message)


async def send_welcome(message: Message):
    """Xush kelibsiz xabari."""
    text = (
        "Assalomu alaykum! 👋\n\n"
        "📌 Bot yordamida quyidagilarni tayyorlashingiz mumkin:\n\n"
        "📕 <b>TAQDIMOT</b> (.pptx)\n"
        "📘 <b>REFERAT / MUSTAQIL ISH</b> (.docx)\n"
        "🎓 <b>KURS ISHI</b> (.docx)\n"
        "📝 <b>TEST</b> (.docx)\n"
        "✍️ <b>INSHO</b>\n"
        "📰 <b>ILMIY MAQOLA</b>\n"
        "📑 <b>TEZIS</b>\n"
        "💼 <b>KEYS</b>\n"
        "📖 <b>GLOSSARIY</b>\n"
        "🧩 <b>KROSSVORD</b>\n\n"
        "📄 Har bir fayl <b>PDF</b> ko'rinishida ham beriladi.\n"
        "🌐 Hujjatlar <b>13 tilda</b> tayyorlanishi mumkin.\n\n"
        "⬇️ Quyidagi menyudan kerakli bo'limni tanlang:"
    )
    await message.answer(text, reply_markup=main_menu(), parse_mode="HTML")


# ═══════════════════════════════════════════════════════════
#  KANAL TEKSHIRUV CALLBACK
# ═══════════════════════════════════════════════════════════

@router.callback_query(F.data == "check_subscription")
async def check_sub_callback(call: CallbackQuery, bot: Bot):
    if await check_subscription(bot, call.from_user.id):
        await call.message.delete()
        await send_welcome(call.message)
        await call.answer("✅ Ajoyib! Botdan foydalanishingiz mumkin.", show_alert=False)
    else:
        await call.answer(
            "❌ Siz hali barcha kanallarga a'zo bo'lmadingiz!",
            show_alert=True
        )


# ═══════════════════════════════════════════════════════════
#  ASOSIY MENYU (callback orqali qaytish)
# ═══════════════════════════════════════════════════════════

@router.callback_query(F.data == "main_menu")
async def back_to_main(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.delete()
    await send_welcome(call.message)
    await call.answer()


@router.callback_query(F.data == "cancel")
async def cancel_action(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(
        "❌ Amal bekor qilindi.\n\n"
        "Menyudan kerakli bo'limni tanlang:",
        reply_markup=None
    )
    await call.answer()


# ═══════════════════════════════════════════════════════════
#  QO'LLANMA
# ═══════════════════════════════════════════════════════════

@router.message(F.text == "📋 Qo'llanma")
@router.message(Command("help"))
async def cmd_help(message: Message, bot: Bot):
    if not await require_subscription(message, bot):
        return

    text = (
        "📋 <b>QO'LLANMA</b>\n\n"
        "1️⃣ Menyudan kerakli xizmatni tanlang\n"
        "2️⃣ So'ralgan ma'lumotlarni to'liq kiriting\n"
        "3️⃣ Ma'lumotlarni tasdiqlang\n"
        "4️⃣ Balans yetarli bo'lsa fayl tayyorlanadi\n\n"
        "<b>📌 Buyruqlar:</b>\n"
        "/my — Ma'lumotlarim\n"
        "/new — Yangi taqdimot\n"
        "/test — Test yaratish\n"
        "/zip — ZIP arxiv\n"
        "/pdf — PDF qilish\n"
        "/referal — Referal dasturi\n"
        "/buy — Balans to'ldirish\n"
        "/chek — To'lov cheki\n"
        "/help — Yordam\n\n"
        "<b>💡 Eslatma:</b>\n"
        "• Mavzuni to'liq va aniq yozing — sifat shunga bog'liq!\n"
        "• Fayllarni <b>WPS Office</b> yoki kompyuterda oching\n"
        "• Istalgan paytda boshqa tugma bossa jarayon bekor bo'ladi\n\n"
        "❓ Savollar bo'lsa: /help"
    )
    await message.answer(text, parse_mode="HTML")


# ═══════════════════════════════════════════════════════════
#  /my — FOYDALANUVCHI MA'LUMOTLARI
# ═══════════════════════════════════════════════════════════

@router.message(Command("my"))
async def cmd_my(message: Message, bot: Bot):
    if not await require_subscription(message, bot):
        return

    user = await get_user(message.from_user.id)
    if not user:
        await message.answer("❌ Siz ro'yxatdan o'tmagansiz. /start bosing.")
        return

    balance = user["balance"]
    referal_link = f"https://t.me/{(await bot.get_me()).username}?start=ref{message.from_user.id}"

    text = (
        f"👤 <b>Mening ma'lumotlarim</b>\n\n"
        f"🆔 ID: <code>{user['user_id']}</code>\n"
        f"👤 Ism: {user['full_name']}\n"
        f"💰 Balans: <b>{balance:,} so'm</b>\n"
        f"📅 Ro'yxatdan o'tgan: {user['joined_at'][:10]}\n\n"
        f"🔗 Referal havolam:\n<code>{referal_link}</code>"
    )
    await message.answer(text, reply_markup=balance_kb(), parse_mode="HTML")


# ═══════════════════════════════════════════════════════════
#  ADMIN PANEL
# ═══════════════════════════════════════════════════════════

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    stats = await get_stats()
    text = (
        "🔧 <b>ADMIN PANEL</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{stats['total_users']}</b>\n"
        f"📋 Jami buyurtmalar: <b>{stats['total_orders']}</b>\n"
        f"💳 Kutayotgan to'lovlar: <b>{stats['pending_payments']}</b>\n"
        f"💰 Jami tushum: <b>{stats['total_income']:,} so'm</b>"
    )
    await message.answer(text, reply_markup=admin_panel_kb(), parse_mode="HTML")


@router.callback_query(F.data == "admin_stats")
async def admin_stats_cb(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        await call.answer("❌ Ruxsat yo'q", show_alert=True)
        return

    stats = await get_stats()
    text = (
        "📊 <b>STATISTIKA</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{stats['total_users']}</b>\n"
        f"📋 Jami buyurtmalar: <b>{stats['total_orders']}</b>\n"
        f"💳 Kutayotgan to'lovlar: <b>{stats['pending_payments']}</b>\n"
        f"💰 Jami tushum: <b>{stats['total_income']:,} so'm</b>"
    )
    await call.message.edit_text(text, reply_markup=admin_panel_kb(), parse_mode="HTML")
    await call.answer()


@router.callback_query(F.data == "admin_payments")
async def admin_payments_cb(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        await call.answer("❌ Ruxsat yo'q", show_alert=True)
        return

    payments = await get_pending_payments()
    if not payments:
        await call.answer("✅ Hozircha kutayotgan to'lov yo'q", show_alert=True)
        return

    await call.answer()
    for p in payments[:5]:
        text = (
            f"💳 <b>To'lov #{p['id']}</b>\n"
            f"👤 Foydalanuvchi: {p['full_name']} (@{p['username']})\n"
            f"🆔 ID: <code>{p['user_id']}</code>\n"
            f"💰 Miqdor: <b>{p['amount']:,} so'm</b>\n"
            f"📅 Sana: {p['created_at'][:16]}"
        )
        from keyboards import admin_payment_kb
        await call.message.answer(text, reply_markup=admin_payment_kb(p["id"], p["user_id"]), parse_mode="HTML")
