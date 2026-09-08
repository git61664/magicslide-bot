# 📕 Taqdimot va O'quv Ishlari Telegram Boti

**AI-powered bot** talabalar va o'quvchilar uchun taqdimot, referat, test va boshqa o'quv ishlarini avtomatik tayyorlab beradi.

## 🎯 Xususiyatlari

- 📕 **TAQDIMOT** (.pptx) - 6-30 slayd
- 📘 **REFERAT** (.docx) - 5-25 bet
- 🎓 **KURS ISHI** (.docx) - 2 bob + xulosa + adabiyotlar
- 📝 **TEST** (.docx) - 10-50 savol (4 variantli)
- ✍️ **INSHO, MAQOLA, TEZIS, KEYS, GLOSSARIY, KROSSVORD**
- 🗜 **ZIP** - fayllarni arxivga qilish
- 📄 **PDF** - Word, PowerPoint, rasmlarni PDF ga o'tkazish
- 💳 **BALANS** - to'lov tizimi + referal dasturi
- 👥 **REFERAL** - bonuslar va komissiya

## 📋 Narxlar

| Xizmat | Narx |
|--------|------|
| Taqdimot (6-30 slayd) | 4 000 - 5 000 so'm |
| Referat/Mustaqil ish (5-25 bet) | 4 000 - 5 000 so'm |
| Kurs ishi | 10 000 - 30 000 so'm |
| Test (10 savol = 1 blok) | 2 000 so'm/blok |
| Insho | 3 000 so'm |
| Ilmiy maqola | 5 000 so'm |
| Tezis | 4 000 so'm |
| Keys/Glossariy/Krossvord | 3 000 - 4 000 so'm |
| ZIP / PDF | BEPUL |

## 🚀 O'rnatish

### 1. Dependensiyalarni o'rnatish

\\\ash
pip install -r requirements.txt
\\\

### 2. .env faylini to'ldirish

\\\.env
BOT_TOKEN=your_token_here
OPENAI_API_KEY=your_openai_key
ADMIN_ID=your_admin_id
CHANNELS=@channel1,@channel2
CARD_NUMBER=1234 5678 9012 3456
CARD_OWNER=Ism Familiya
PAYMENT_CHAT_ID=123456789
\\\

### 3. Botni ishga tushirish

\\\ash
python main.py
\\\

## 📁 Loyiha Strukturasi

\\\
magicslide/
├── main.py                 # Asosiy fayl
├── config.py              # Sozlamalar
├── database.py            # SQLite baza
├── keyboards.py           # Tugmalar
├── .env                   # Maxfiy o'zgaruvchilar
├── requirements.txt       # Kutubxonalar
├── handlers/              # Handler fayllar
│   ├── start.py          # /start komandasi
│   ├── taqdimot.py       # Taqdimot
│   ├── referat.py        # Referat
│   ├── test_handler.py   # Test
│   ├── boshqa.py         # Kurs ishi va boshqalar
│   ├── balans.py         # To'lov va balans
│   └── zip_pdf.py        # ZIP va PDF
├── generators/            # Fayl generatorlar
│   ├── pptx_generator.py # PPTX generatsiya
│   ├── docx_generator.py # DOCX generatsiya
│   └── __init__.py
├── temp/                  # Vaqtinchalik fayllar
├── bot.db                # SQLite baza
└── README.md
\\\

## 🔧 Konfiguratsiya

### Kanal Obuna

Bot o'z xizmatlarini faqat majburiy kanallarga a'zo bo'lgan foydalanuvchilar uchun taqdim etadi.

\\\python
CHANNELS = ["@channel1", "@channel2"]  # .env da belgilang
\\\

### Narxlar

\\\python
# config.py
PRICES = {
    "taqdimot_min": 4000,
    "taqdimot_max": 5000,
    # ...
}
\\\

### Referal Dasturi

\\\python
REFERAL_BONUS = 1000        # Har bir taklif uchun
REFERAL_ORDER_BONUS = 100   # Har buyurtma uchun
REFERAL_PERCENT = 5         # To'lovdan %
\\\

## 📊 Buyruqlar

| Buyruq | Vazifasi |
|--------|----------|
| /start | Botni ishga tushirish |
| /my | Mening ma'lumotlarim |
| /help | Qo'llanma |
| /new | Yangi taqdimot |
| /test | Test yaratish |
| /buy | Balans to'ldirish |
| /chek | To'lov cheki |
| /admin | Admin panel |

## 💳 To'lov Tizimi

1. Foydalanuvchi balansini to'ldirmaqni xohlaydi
2. Bot to'lov hisob-kitoblarini ko'rsatadi (karta raqami)
3. Foydalanuvchi o'z bankida to'lov qiladi
4. Chekni botga yubormadi
5. Admin chekni tasdiqlay yoki rad etadi
6. Balans avtomatik qo'shiladi

## 👥 Referal Dasturi

- **Har taklif**: 1 000 so'm bonus
- **Har buyurtma**: taklif etilgan foydalanuvchiga 100 so'm bonus
- **To'lovdan**: 5% commission

## 🗄 Ma'lumotlar Bazasi

SQLite baza quyidagi jadvallarni o'z ichiga oladi:

- **users** - foydalanuvchilar
- **orders** - buyurtmalar
- **payments** - to'lovlar
- **referals** - referal statistika

## 🤖 AI Integrations

Bot quyidagi kutubxonalardan foydalanadi:

- **aiogram 3.4.1** - Telegram bot API
- **python-pptx** - PPTX fayllar yaratish
- **python-docx** - DOCX fayllar yaratish
- **aiosqlite** - async SQLite
- **aiofiles** - async fayl operatsiyalari

## ⚙️ Admin Panel

Admin (/admin komandasi) quyidagi imkoniyatlarga ega:

- 📊 Statistika ko'rish
- 💳 Kutayotgan to'lovlarni tasdiqlash/rad etish
- 📢 Broadcast xabar yuborish

## 🐛 Xatolarni Tuzatish

Agar xato yuz bersa:

1. Bot consolni tekshiring
2. \ot.db\ faylni o'chirib qayta boshlang
3. .env faylni tekshiring
4. Token to'g'riligini tasdiqlang

## 📞 Qo'llab-Quvvatlash

Botga savollar bo'lsa: /help buyrug'ini bosing

## 📄 Litsenziya

This project is open source.

---

**Yaratilgan:** 2024
**Dasturiy til:** Python 3.9+
