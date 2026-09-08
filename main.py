import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from config import BOT_TOKEN
from database import init_db
from handlers import start, taqdimot, referat, test_handler, boshqa, balans, zip_pdf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Botni ishga tushirish"),
        BotCommand(command="my", description="Mening ma'lumotlarim"),
        BotCommand(command="help", description="Yordam"),
        BotCommand(command="new", description="Yangi taqdimot"),
        BotCommand(command="test", description="Test yaratish"),
        BotCommand(command="buy", description="Balans to'ldirish"),
        BotCommand(command="admin", description="Admin panel"),
    ]
    await bot.set_my_commands(commands)

async def main():
    await init_db()
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    dp.include_router(start.router)
    dp.include_router(taqdimot.router)
    dp.include_router(referat.router)
    dp.include_router(test_handler.router)
    dp.include_router(boshqa.router)
    dp.include_router(balans.router)
    dp.include_router(zip_pdf.router)
    
    await set_commands(bot)
    
    logger.info("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
