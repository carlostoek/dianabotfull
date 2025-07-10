# src/telegram_bot/handlers/profile_handler.py
"""
Handler for the /perfil command.
"""
from typing import Dict, Any

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.repository import UserRepository, UserProgressRepository, PointTransactionRepository
from src.services.points_service import PointsService
from src.services.persona_service import PersonaService
from src.services.user_service import UserService

profile_router = Router()


@profile_router.message(Command("perfil"))
async def show_profile(message: types.Message, state: FSMContext, session: AsyncSession):
    """
    Shows the user's profile with their points, Diana's state, resonance, and role.

    Args:
        message: The message object from Telegram.
        state: The FSM context.
        session: The database session provided by middleware.
    """
    await state.clear()
    user_id = message.from_user.id
    username = message.from_user.username or "Usuario"

    try:
        # Instantiate repositories
        user_repo = UserRepository(session)
        user_progress_repo = UserProgressRepository(session)
        transaction_repo = PointTransactionRepository(session)

        # Instantiate services
        user_service = UserService(session)
        points_service = PointsService(user_repo, transaction_repo)
        persona_service = PersonaService(user_progress_repo)

        # Fetch user data
        user, _ = await user_service.get_or_create_user(user_id, username)
        points = await points_service.get_points(user_id)
        diana_state = await persona_service.get_diana_state(user_id)
        
        resonance_score = 0.0
        if user.progress:
            resonance_score = user.progress.resonance_score
            
        role = user.role

        # Format the message
        profile_text = (
            f"<b>✨ Perfil de {username} ✨</b>\n\n"
            f"<b>Puntos:</b> {points} 💠\n"
            f"<b>Estado de Diana:</b> {diana_state}\n"
            f"<b>Nivel de Resonancia:</b> {resonance_score:.2f} / 10.0\n"
            f"<b>Rol:</b> {role.capitalize()}\n"
        )

        await message.answer(
            profile_text,
            parse_mode="HTML",
            reply_markup=ReplyKeyboardRemove()
        )

    except Exception as e:
        # Log the error properly in a real application
        print(f"Error in show_profile: {e}")
        await message.answer(
            "😕 Lo siento, ha ocurrido un error al recuperar tu perfil. "
            "Por favor, inténtalo de nuevo más tarde.",
            reply_markup=ReplyKeyboardRemove()
        )
