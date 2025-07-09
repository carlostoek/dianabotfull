# main.py
import asyncio
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher

from src.database.connection import init_db
from src.telegram_bot.middleware import DbSessionMiddleware
from src.telegram_bot.handlers.start import router as start_router

async def main():
    load_dotenv() # Cargar variables de entorno

    # Inicializar la base de datos (crear tablas si no existen)
    await init_db()

    bot = Bot(token=os.environ.get("TELEGRAM_BOT_TOKEN"))
    dp = Dispatcher()

    # Registrar middleware
    dp.message.middleware(DbSessionMiddleware())
    dp.callback_query.middleware(DbSessionMiddleware())

    # Registrar routers
    dp.include_router(start_router)

    # Iniciar el bot
    print("Bot started...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
