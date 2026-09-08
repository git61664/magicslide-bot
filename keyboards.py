from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from config import CHANNELS, LANGUAGES, DESIGN_THEMES, TEST_LEVELS


# ═══════════════════════════════════════════════════════════
#  ASOSIY MENYU
# ═══════════════════════════════════════════════════════════

def main_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="🚀 Ilova orqali tayyorlash"),
    )
    builder.row(
        KeyboardButton(text="📕 Taqdimot"),
        KeyboardButton(text="📘 Referat / Mustaqil ish"),
    )
    builder.row(
        KeyboardButton(text="🎓 Kurs ishi yaratish"),
        KeyboardButton(text="📝 Test yaratish"),
    )
    builder.row(
        KeyboardButton(text="📚 Boshqa ishlar"),
    )
    builder.row(
        KeyboardButton(text="🗜 ZIP qilish"),
        KeyboardButton(text="📄 PDF qilish"),
    )
    builder.row(
        KeyboardButton(text="💰 Balans"),
        KeyboardButton(text="📋 Qo'llanma"),
    )
    return builder.as_markup(resize_keyboard=True)


# ═══════════════════════════════════════════════════════════
#  KANAL OBUNA TEKSHIRUVI
# ═══════════════════════════════════════════════════════════

def channel_subscription_kb(channels: list[str]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for ch in channels:
        builder.row(
            InlineKeyboardButton(
                text=f"📢 {ch} kanaliga o'tish",
                url=f"https://t.me/{ch.lstrip('@')}"
            )
        )
    builder.row(
        InlineKeyboardButton(text="✅ A'zo bo'ldim", callback_data="check_subscription")
    )
    return builder.as_markup()


# ═══════════════════════════════════════════════════════════
#  TAQDIMOT KLAVIATURALARI
# ═══════════════════════════════════════════════════════════

def slides_count_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    counts = [6, 8, 10, 12, 15, 20, 25, 30]
    for i in range(0, len(counts), 4):
        row = counts[i:i+4]
        builder.row(*[
            InlineKeyboardButton(text=str(n), callback_data=f"slides_{n}")
            for n in row
        ])
    builder.row(
        InlineKeyboardButton(text="✏️ O'zim kiriting", callback_data="slides_custom")
    )
    builder.row(cancel_btn())
    return builder.as_markup()


def design_theme_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for i, theme in enumerate(DESIGN_THEMES):
        builder.row(
            InlineKeyboardButton(text=theme, callback_data=f"theme_{i}")
        )
    builder.row(cancel_btn())
    return builder.as_markup()


def images_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Ha, rasm kerak", callback_data="images_yes"),
        InlineKeyboardButton(text="❌ Yo'q", callback_data="images_no"),
    )
    builder.row(cancel_btn())
    return builder.as_markup()


# ═══════════════════════════════════════════════════════════
#  TIL TANLASH
# ═══════════════════════════════════════════════════════════

def language_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for i in range(0, len(LANGUAGES), 3):
        row = LANGUAGES[i:i+3]
        builder.row(*[
            InlineKeyboardButton(text=lang, callback_data=f"lang_{lang}")
            for lang in row
        ])
    builder.row(cancel_btn())
    return builder.as_markup()


# ═══════════════════════════════════════════════════════════
#  BET SONI (REFERAT / MUSTAQIL ISH)
# ═══════════════════════════════════════════════════════════

def pages_count_kb(min_p: int = 5, max_p: int = 25) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    counts = [p for p in [5, 7, 10, 12, 15, 18, 20, 25] if min_p <= p <= max_p]
    for i in range(0, len(counts), 4):
        row = counts[i:i+4]
        builder.row(*[
            InlineKeyboardButton(text=str(n), callback_data=f"pages_{n}")
            for n in row
        ])
    builder.row(
        InlineKeyboardButton(text="✏️ O'zim kiriting", callback_data="pages_custom")
    )
    builder.row(cancel_btn())
    return builder.as_markup()


# ═══════════════════════════════════════════════════════════
#  TEST KLAVIATURALARI
# ═══════════════════════════════════════════════════════════

def test_level_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for level in TEST_LEVELS:
        builder.row(
            InlineKeyboardButton(text=level, callback_data=f"level_{level}")
        )
    builder.row(cancel_btn())
    return builder.as_markup()


def test_count_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    counts = [10, 20, 30, 40, 50]
    builder.row(*[
        InlineKeyboardButton(text=str(n), callback_data=f"tcount_{n}")
        for n in counts
    ])
    builder.row(
        InlineKeyboardButton(text="✏️ O'zim kiriting", callback_data="tcount_custom")
    )
    builder.row(cancel_btn())
    return builder.as_markup()


# ═══════════════════════════════════════════════════════════
#  BOSHQA ISHLAR MENYUSI
# ═══════════════════════════════════════════════════════════

def other_works_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    works = [
        ("✍️ Insho", "other_insho"),
        ("📰 Ilmiy maqola", "other_maqola"),
        ("📑 Tezis", "other_tezis"),
        ("💼 Keys (Case study)", "other_keys"),
        ("📖 Glossariy", "other_glossariy"),
        ("🧩 Krossvord", "other_krossvord"),
    ]
    for text, cb in works:
        builder.row(InlineKeyboardButton(text=text, callback_data=cb))
    builder.row(cancel_btn())
    return builder.as_markup()


# ═══════════════════════════════════════════════════════════
#  KURS ISHI
# ═══════════════════════════════════════════════════════════

def kurs_ishi_group_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⏭ Kerak emas", callback_data="kurs_nogroup")
    )
    builder.row(cancel_btn())
    return builder.as_markup()


# ═══════════════════════════════════════════════════════════
#  TASDIQLASH / BEKOR QILISH
# ═══════════════════════════════════════════════════════════

def confirm_kb(confirm_cb: str = "confirm_yes", cancel_cb: str = "confirm_no") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=confirm_cb),
        InlineKeyboardButton(text="❌ Bekor qilish", callback_data=cancel_cb),
    )
    return builder.as_markup()


def cancel_btn() -> InlineKeyboardButton:
    return InlineKeyboardButton(text="🔙 Bekor qilish", callback_data="cancel")


def cancel_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(cancel_btn())
    return builder.as_markup()


# ═══════════════════════════════════════════════════════════
#  BALANS VA TO'LOV
# ═══════════════════════════════════════════════════════════

def balance_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="💳 Balans to'ldirish", callback_data="buy_balance"),
    )
    builder.row(
        InlineKeyboardButton(text="👥 Referal dasturi", callback_data="referal_info"),
    )
    return builder.as_markup()


def topup_amount_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    amounts = [5000, 10000, 20000, 50000, 100000]
    for i in range(0, len(amounts), 3):
        row = amounts[i:i+3]
        builder.row(*[
            InlineKeyboardButton(
                text=f"{a:,} so'm".replace(",", " "),
                callback_data=f"topup_{a}"
            )
            for a in row
        ])
    builder.row(
        InlineKeyboardButton(text="✏️ Boshqa miqdor", callback_data="topup_custom")
    )
    builder.row(cancel_btn())
    return builder.as_markup()


def payment_sent_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Chek yubordim", callback_data="payment_check_sent")
    )
    builder.row(cancel_btn())
    return builder.as_markup()


# ═══════════════════════════════════════════════════════════
#  ADMIN PANEL
# ═══════════════════════════════════════════════════════════

def admin_payment_kb(payment_id: int, user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅ Tasdiqlash",
            callback_data=f"admin_approve_{payment_id}_{user_id}"
        ),
        InlineKeyboardButton(
            text="❌ Rad etish",
            callback_data=f"admin_reject_{payment_id}_{user_id}"
        ),
    )
    return builder.as_markup()


def admin_panel_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats"),
        InlineKeyboardButton(text="💳 Kutayotgan to'lovlar", callback_data="admin_payments"),
    )
    builder.row(
        InlineKeyboardButton(text="📢 Xabar yuborish", callback_data="admin_broadcast"),
    )
    return builder.as_markup()


# ═══════════════════════════════════════════════════════════
#  ZIP / PDF
# ═══════════════════════════════════════════════════════════

def zip_ready_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🗜 ZIP qilish", callback_data="zip_process"),
        InlineKeyboardButton(text="🗑 Tozalash", callback_data="zip_clear"),
    )
    return builder.as_markup()


def pdf_ready_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📄 PDF qilish", callback_data="pdf_process"),
        InlineKeyboardButton(text="🗑 Tozalash", callback_data="pdf_clear"),
    )
    return builder.as_markup()


# ═══════════════════════════════════════════════════════════
#  UMUMIY YORDAMCHI
# ═══════════════════════════════════════════════════════════

def back_to_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="main_menu")
    )
    return builder.as_markup()


def url_button_kb(text: str, url: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=text, url=url))
    return builder.as_markup()
