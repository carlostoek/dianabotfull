# src/telegram_bot/handlers/admin_handlers.py
import os
import traceback
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.seeds import seed_initial_data

router = Router()

# Obtener el ID de administrador desde las variables de entorno
ADMIN_ID = os.environ.get("ADMIN_USER_ID")

@router.message(Command("seed"))
async def seed_database_handler(message: Message, session: AsyncSession):
    """
    Comando para sembrar la base de datos con datos iniciales.
    Restringido solo al administrador.
    """
    if not ADMIN_ID or str(message.from_user.id) != ADMIN_ID:
        await message.answer("🚫 No tienes permiso para ejecutar este comando.")
        return

    try:
        await message.answer("🌱 Comenzando el sembrado de la base de datos...")
        await seed_initial_data(session)
        await message.answer("✅ ¡Base de datos sembrada exitosamente!")
    except Exception as e:
        error_details = traceback.format_exc()
        await message.answer(f"❌ Ocurrió un error al sembrar la base de datos:\n\n<pre>{e}</pre>\n\n<pre>{error_details}</pre>", parse_mode="HTML")
        print(f"Error during seeding: {error_details}")
