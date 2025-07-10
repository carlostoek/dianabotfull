# src/telegram_bot/handlers/start.py
"""
Handler for the /start command.
"""
import logging
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.user_service import UserService
from src.utils.user_roles import assign_role
from src.utils.menu_factory import get_main_menu

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = Router()

@router.message(CommandStart())
async def command_start_handler(message: Message, session: AsyncSession) -> None:
    """
    Handles the /start command.

    This function ensures a user is registered, assigns them a default role
    if they don't have one, and displays the main menu.

    Args:
        message: The incoming message object from Aiogram.
        session: The SQLAlchemy async session provided by middleware.
    """
    try:
        user_id = message.from_user.id
        username = message.from_user.username or "Aventurero"

        # 1. & 2. Verify and register the user if they don't exist.
        user_service = UserService(session)
        await user_service.create_user_if_not_exists(user_id, username)

        # 3. Assign a role if the user doesn't have one.
        # Note: This uses the in-memory implementation.
        assign_role(user_id)

        # 4. Send the welcome message with the main menu.
        welcome_text = (
            f"¡Hola, {username}! ✨\n\n"
            "Soy Diana, tu guía en este viaje. "
            "Usa el menú de abajo para explorar las opciones disponibles."
        )
        
        await message.answer(
            welcome_text,
            reply_markup=get_main_menu()
        )
        logger.info(f"User {username} (ID: {user_id}) started the bot.")

    except Exception as e:
        logger.error(f"Error in command_start_handler for user {message.from_user.id}: {e}", exc_info=True)
        await message.answer(
            "😕 Hubo un problema al iniciar. Por favor, intenta de nuevo más tarde."
        )