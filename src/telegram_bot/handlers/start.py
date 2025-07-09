# src/telegram_bot/handlers/start.py
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.repository import UserRepository

router = Router()

@router.message(CommandStart())
async def command_start_handler(message: Message, session: AsyncSession) -> None:
    user_repo = UserRepository(session)
    user, created = await user_repo.get_or_create(message.from_user.id, message.from_user.username)

    if created:
        await message.answer(f"¡Hola, {user.username}! ¡Bienvenido a DianaBot! Hemos creado tu perfil.")
    else:
        await message.answer(f"¡Bienvenido de nuevo, {user.username}! Me alegra verte de nuevo.")

    print(f"User {user.username} (ID: {user.id}) - Created: {created}")
