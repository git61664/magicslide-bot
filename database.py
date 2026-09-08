import aiosqlite
import asyncio
from datetime import datetime
from config import REFERAL_BONUS, REFERAL_ORDER_BONUS, REFERAL_PERCENT

DB_PATH = "bot.db"


async def init_db():
    """Ma'lumotlar bazasini ishga tushirish va jadvallar yaratish."""
    async with aiosqlite.connect(DB_PATH) as db:
        # Foydalanuvchilar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id     INTEGER PRIMARY KEY,
                username    TEXT,
                full_name   TEXT,
                balance     INTEGER DEFAULT 0,
                referal_by  INTEGER DEFAULT NULL,
                joined_at   TEXT DEFAULT (datetime('now')),
                is_banned   INTEGER DEFAULT 0
            )
        """)

        # Buyurtmalar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                order_type  TEXT NOT NULL,
                details     TEXT,
                price       INTEGER DEFAULT 0,
                status      TEXT DEFAULT 'pending',
                created_at  TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        # To'lovlar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                amount      INTEGER NOT NULL,
                check_file  TEXT,
                status      TEXT DEFAULT 'pending',
                created_at  TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        # Referal statistika
        await db.execute("""
            CREATE TABLE IF NOT EXISTS referals (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                referrer_id INTEGER NOT NULL,
                referred_id INTEGER NOT NULL,
                bonus_paid  INTEGER DEFAULT 0,
                joined_at   TEXT DEFAULT (datetime('now'))
            )
        """)

        await db.commit()


# ─── FOYDALANUVCHI ──────────────────────────────────────────────────────────

async def get_user(user_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def register_user(user_id: int, username: str, full_name: str, referal_by: int = None):
    """Yangi foydalanuvchi ro'yxatdan o'tkazish."""
    async with aiosqlite.connect(DB_PATH) as db:
        existing = await get_user(user_id)
        if existing:
            # Username yoki ismni yangilash
            await db.execute(
                "UPDATE users SET username=?, full_name=? WHERE user_id=?",
                (username, full_name, user_id)
            )
            await db.commit()
            return False  # Yangi emas

        await db.execute(
            "INSERT INTO users (user_id, username, full_name, referal_by) VALUES (?, ?, ?, ?)",
            (user_id, username, full_name, referal_by)
        )

        # Referal bonus berish
        if referal_by:
            referrer = await get_user(referal_by)
            if referrer:
                # Referer ga bonus
                await db.execute(
                    "UPDATE users SET balance = balance + ? WHERE user_id = ?",
                    (REFERAL_BONUS, referal_by)
                )
                # Referal jadvaliga qo'shish
                await db.execute(
                    "INSERT INTO referals (referrer_id, referred_id, bonus_paid) VALUES (?, ?, ?)",
                    (referal_by, user_id, REFERAL_BONUS)
                )

        await db.commit()
        return True  # Yangi foydalanuvchi


async def get_balance(user_id: int) -> int:
    user = await get_user(user_id)
    return user["balance"] if user else 0


async def update_balance(user_id: int, amount: int):
    """Balansni o'zgartirish (musbat yoki manfiy)."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET balance = balance + ? WHERE user_id = ?",
            (amount, user_id)
        )
        await db.commit()


async def deduct_balance(user_id: int, amount: int) -> bool:
    """Balansdan pul yechish. Yetarli bo'lmasa False qaytaradi."""
    user = await get_user(user_id)
    if not user or user["balance"] < amount:
        return False
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET balance = balance - ? WHERE user_id = ?",
            (amount, user_id)
        )
        await db.commit()
    return True


# ─── BUYURTMALAR ────────────────────────────────────────────────────────────

async def create_order(user_id: int, order_type: str, details: str, price: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO orders (user_id, order_type, details, price, status) VALUES (?, ?, ?, ?, 'completed')",
            (user_id, order_type, details, price)
        )
        await db.commit()
        order_id = cursor.lastrowid

    # Referal - buyurtma bonusi berish
    user = await get_user(user_id)
    if user and user.get("referal_by"):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "UPDATE users SET balance = balance + ? WHERE user_id = ?",
                (REFERAL_ORDER_BONUS, user["referal_by"])
            )
            await db.commit()

    return order_id


async def get_user_orders(user_id: int) -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC LIMIT 10",
            (user_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]


# ─── TO'LOVLAR ───────────────────────────────────────────────────────────────

async def create_payment(user_id: int, amount: int, check_file: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO payments (user_id, amount, check_file, status) VALUES (?, ?, ?, 'pending')",
            (user_id, amount, check_file)
        )
        await db.commit()
        return cursor.lastrowid


async def approve_payment(payment_id: int):
    """To'lovni tasdiqlash va balansni to'ldirish."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM payments WHERE id = ?", (payment_id,)
        ) as cursor:
            payment = await cursor.fetchone()

        if not payment or payment["status"] != "pending":
            return None

        # Tasdiqlash
        await db.execute(
            "UPDATE payments SET status='approved' WHERE id=?", (payment_id,)
        )
        # Balans to'ldirish
        await db.execute(
            "UPDATE users SET balance = balance + ? WHERE user_id = ?",
            (payment["amount"], payment["user_id"])
        )

        # Referal % berish
        user = await get_user(payment["user_id"])
        if user and user.get("referal_by"):
            bonus = int(payment["amount"] * REFERAL_PERCENT / 100)
            if bonus > 0:
                await db.execute(
                    "UPDATE users SET balance = balance + ? WHERE user_id = ?",
                    (bonus, user["referal_by"])
                )

        await db.commit()
        return dict(payment)


async def reject_payment(payment_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE payments SET status='rejected' WHERE id=?", (payment_id,)
        )
        await db.commit()


# ─── REFERAL ─────────────────────────────────────────────────────────────────

async def get_referal_count(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM referals WHERE referrer_id = ?", (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0


async def get_referal_earnings(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT SUM(bonus_paid) FROM referals WHERE referrer_id = ?", (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row and row[0] else 0


# ─── ADMIN STATISTIKA ────────────────────────────────────────────────────────

async def get_stats() -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as c:
            total_users = (await c.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM orders") as c:
            total_orders = (await c.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM payments WHERE status='pending'") as c:
            pending_payments = (await c.fetchone())[0]
        async with db.execute("SELECT SUM(amount) FROM payments WHERE status='approved'") as c:
            total_income = (await c.fetchone())[0] or 0

    return {
        "total_users": total_users,
        "total_orders": total_orders,
        "pending_payments": pending_payments,
        "total_income": total_income,
    }


async def get_all_users() -> list[int]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT user_id FROM users WHERE is_banned=0") as cursor:
            rows = await cursor.fetchall()
            return [r[0] for r in rows]


async def get_pending_payments() -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT p.*, u.full_name, u.username FROM payments p "
            "JOIN users u ON p.user_id = u.user_id "
            "WHERE p.status='pending' ORDER BY p.created_at DESC"
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]
