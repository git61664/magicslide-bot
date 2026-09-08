import os
from dotenv import load_dotenv

load_dotenv()

# Bot sozlamalari
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
PAYMENT_CHAT_ID = int(os.getenv("PAYMENT_CHAT_ID", "0"))

# Majburiy obuna kanallari
CHANNELS_RAW = os.getenv("CHANNELS", "")
CHANNELS: list[str] = [ch.strip() for ch in CHANNELS_RAW.split(",") if ch.strip()]

# To'lov ma'lumotlari
CARD_NUMBER = os.getenv("CARD_NUMBER", "")
CARD_OWNER = os.getenv("CARD_OWNER", "")

# Narxlar (so'mda)
PRICES = {
    "taqdimot_min": 4000,
    "taqdimot_max": 5000,
    "referat_min": 4000,
    "referat_max": 5000,
    "test_per_10": 2000,
    "kurs_ishi_min": 10000,
    "kurs_ishi_max": 30000,
    "insho": 3000,
    "ilmiy_maqola": 5000,
    "tezis": 4000,
    "keys": 4000,
    "glossariy": 3000,
    "krossvord": 3000,
}

# Referal bonuslar
REFERAL_BONUS = 1000        # Har bir taklif uchun
REFERAL_ORDER_BONUS = 100   # Referal a'zo har buyurtma bersa
REFERAL_PERCENT = 5         # Har to'lovdan %

# Fayl chegaralari
ZIP_MAX_FILES = 100
ZIP_MAX_FILE_SIZE_MB = 200
ZIP_MAX_TOTAL_MB = 1000
PDF_MAX_FILES = 20
PDF_MAX_FILE_SIZE_MB = 200

# Temp papka
TEMP_DIR = "temp"

# Qo'llab-quvvatlanadigan tillar
LANGUAGES = [
    "O'zbek", "Rus", "Ingliz", "Qozoq", "Tojik",
    "Turk", "Arab", "Nemis", "Fransuz", "Ispan",
    "Xitoy", "Yapon", "Koreys"
]

# Taqdimot dizayn shablonlari
DESIGN_THEMES = [
    "🎨 Zamonaviy (ko'k-oq)",
    "🌿 Yashil-tabiat",
    "🔴 Qizil-professional",
    "🟣 Binafsha-elegant",
    "🟡 Sariq-ijodiy",
    "⚫ Qora-biznes",
    "🌅 Gradient-rangli",
    "🏛 Klassik-oq",
]

# Test darajalari
TEST_LEVELS = ["🟢 Oson", "🟡 O'rtacha", "🔴 Qiyin"]
