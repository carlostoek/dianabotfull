# src/telegram_bot/handlers/game_handlers.py
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.mission_service import MissionService
from src.services.user_service import UserService

router = Router()

@router.message(Command("misiones"))
async def misions_handler(message: Message, session: AsyncSession):
    mission_service = MissionService(session)
    missions = await mission_service.mission_repo.get_all_missions()
    
    response = "📜 **Misiones Disponibles** 📜\n\n"
    for mission in missions:
        response += f"🔹 **{mission.name}**\n"
        response += f"   {mission.description}\n"
        response += f"   Recompensa: {mission.reward_points} puntos ✨\n\n"
        
    await message.answer(response, parse_mode="Markdown")

@router.message(Command("puntos"))
async def points_handler(message: Message, session: AsyncSession):
    user_service = UserService(session)
    user, _ = await user_service.get_or_create_user(message.from_user.id, message.from_user.username)
    
    response = f"💰 **Tus Puntos** 💰\n\n"
    response += f"Hola {user.username}, tienes un total de **{user.points}** puntos. ¡Sigue así! 💪"
    
    await message.answer(response, parse_mode="Markdown")
