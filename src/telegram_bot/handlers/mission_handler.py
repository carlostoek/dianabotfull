# src/telegram_bot/handlers/mission_handler.py
"""
Handlers for mission-related commands and callbacks.
"""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.mission_service import MissionService
from src.services.user_service import UserService
from src.telegram_bot.menus.mission_menu import create_mission_layout
from src.utils.menu_factory import get_main_menu, format_section_message

logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(F.data == "missions_daily")
async def handle_daily_mission(callback_query: CallbackQuery, session: AsyncSession):
    """
    Handles the 'Daily Missions' button and shows the current daily mission.
    """
    try:
        user_id = callback_query.from_user.id
        mission_service = MissionService(session)
        mission = await mission_service.get_daily_mission(user_id)

        if not mission:
            await callback_query.answer("No hay misiones diarias disponibles hoy.", show_alert=True)
            return

        text, keyboard = create_mission_layout(mission)
        await callback_query.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        logger.info(f"User {user_id} viewed their daily mission.")

    except Exception as e:
        logger.error(f"Error in handle_daily_mission for user {callback_query.from_user.id}: {e}", exc_info=True)
        await callback_query.answer("😕 Hubo un problema al cargar la misión. Intenta de nuevo.", show_alert=True)

@router.callback_query(F.data.startswith("claim_mission_"))
async def handle_claim_mission(callback_query: CallbackQuery, session: AsyncSession):
    """
    Handles the callback for claiming a mission reward.
    """
    try:
        user_id = callback_query.from_user.id
        try:
            mission_id = int(callback_query.data.split("_")[2])
        except (IndexError, ValueError):
            await callback_query.answer("Error: Misión no válida.", show_alert=True)
            return

        mission_service = MissionService(session)
        reward = await mission_service.complete_mission(user_id, mission_id)

        if reward is not None:
            user_service = UserService(session)
            # This assumes a method to add currency exists in UserService
            # If not, this line will need to be adjusted.
            await user_service.add_currency(user_id, reward)
            
            updated_mission = await mission_service.get_mission_by_id(user_id, mission_id)
            text, keyboard = create_mission_layout(updated_mission)

            await callback_query.message.edit_text(
                f"¡Felicidades! Has completado la misión y ganado **{reward} besitos**.\n\n{text}",
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            logger.info(f"User {user_id} claimed {reward} besitos from mission {mission_id}.")
        else:
            await callback_query.answer("Esta misión ya ha sido reclamada o no se puede completar.", show_alert=True)

    except Exception as e:
        logger.error(f"Error in handle_claim_mission for user {callback_query.from_user.id}: {e}", exc_info=True)
        await callback_query.answer("😕 Hubo un problema al reclamar la misión. Intenta de nuevo.", show_alert=True)

@router.callback_query(F.data == "main_menu")
async def handle_back_to_main_menu(callback_query: CallbackQuery):
    """
    Handles the 'Back to Menu' button, returning to the main menu.
    """
    try:
        username = callback_query.from_user.username or "Aventurero"
        title = f"BIENVENIDO, {username.upper()}"
        content = "Soy Diana, tu guía en este viaje. Usa el menú de abajo para explorar las opciones disponibles."
        
        welcome_text = format_section_message(title, content, emoji="✨")
        
        await callback_query.message.edit_text(
            text=welcome_text,
            reply_markup=get_main_menu(),
            parse_mode="Markdown"
        )
        logger.info(f"User {callback_query.from_user.id} returned to the main menu.")

    except Exception as e:
        logger.error(f"Error in handle_back_to_main_menu for user {callback_query.from_user.id}: {e}", exc_info=True)
        await callback_query.answer("😕 Hubo un problema al volver al menú. Intenta de nuevo.", show_alert=True)