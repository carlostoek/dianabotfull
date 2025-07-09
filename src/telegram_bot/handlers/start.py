# src/telegram_bot/handlers/start.py
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.user_service import UserService
from src.services.mission_service import MissionService

router = Router()

@router.message(CommandStart())
async def command_start_handler(message: Message, session: AsyncSession) -> None:
    user_service = UserService(session)
    user, created = await user_service.get_or_create_user(message.from_user.id, message.from_user.username)

    if created:
        await message.answer(f"¡Hola, {user.username}! ¡Bienvenido a DianaBot! Hemos creado tu perfil.")
    else:
        await message.answer(f"¡Bienvenido de nuevo, {user.username}! Me alegra verte de nuevo.")

    # Check for daily login mission
    mission_service = MissionService(session)
    completed = await mission_service.check_daily_login(user.id)
    if completed:
        await message.answer("¡Has completado la misión de inicio de sesión diario! 🏆")

    print(f"User {user.username} (ID: {user.id}) - Created: {created}")
