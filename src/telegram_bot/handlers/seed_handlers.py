from aiogram import Router, types
from aiogram.filters import Command
import asyncio
from src.database.connection import get_db_session
from src.database.seeds import seed_initial_data

router = Router()

from aiogram import Router, types
from aiogram.filters import Command
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession # Importar AsyncSession
from src.database.seeds import seed_initial_data

router = Router()

@router.message(Command("seed"))
async def seed_command(message: types.Message, session: AsyncSession): # Inyectar la sesión
    """Handles the /seed command to populate the database."""
    user_id = message.from_user.id
    # For security, you might want to restrict this command to specific user IDs (e.g., admins)
    if user_id not in [6181290784]: # Reemplaza YOUR_ADMIN_TELEGRAM_ID con tu ID de Telegram
        await message.reply_text("No tienes permiso para ejecutar este comando.")
        return

    await message.reply("Iniciando el proceso de siembra de la base de datos...")
    try:
        await seed_initial_data(session) # Usar la sesión inyectada
        await message.reply("Base de datos sembrada exitosamente.")
    except Exception as e:
        await message.reply(f"Error al sembrar la base de datos: {e}")
    except Exception as e:
        await message.reply(f"Error al sembrar la base de datos: {e}")