# src/telegram_bot/handlers/main_menu_handlers.py
"""
Handlers for the main menu buttons.
"""
import logging
from aiogram import Router
from aiogram.types import CallbackQuery
from src.utils.menu_factory import get_missions_menu, get_vip_menu, format_section_message

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = Router()

@router.callback_query(lambda c: c.data == "missions")
async def handle_missions(callback_query: CallbackQuery):
    """
    Handles the 'Misiones' button from the main menu.
    """
    try:
        title = "Centro de Misiones"
        content = "Aquí puedes ver tus misiones diarias, semanales y logros."
        
        message_text = format_section_message(title, content, emoji="🎯")
        
        await callback_query.message.edit_text(
            text=message_text,
            reply_markup=get_missions_menu(),
            parse_mode="Markdown"
        )
        logger.info(f"User {callback_query.from_user.id} accessed the missions center.")
    except Exception as e:
        logger.error(f"Error in handle_missions for user {callback_query.from_user.id}: {e}", exc_info=True)
        await callback_query.answer("😕 Hubo un problema al cargar las misiones. Intenta de nuevo.", show_alert=True)

@router.callback_query(lambda c: c.data == "daily_gift")
async def handle_daily_gift(callback_query: CallbackQuery):
    """
    Handles the 'Regalo' button from the main menu.
    """
    await callback_query.answer("¡Has reclamado tu regalo diario!", show_alert=True)

@router.callback_query(lambda c: c.data == "profile")
async def handle_profile(callback_query: CallbackQuery):
    """
    Handles the 'Mi Perfil' button from the main menu.
    """
    await callback_query.answer("Aquí se mostrará tu perfil.", show_alert=True)

@router.callback_query(lambda c: c.data == "backpack")
async def handle_backpack(callback_query: CallbackQuery):
    """
    Handles the 'Mochila' button from the main menu.
    """
    await callback_query.answer("Aquí se mostrará tu mochila.", show_alert=True)

@router.callback_query(lambda c: c.data == "minigames")
async def handle_minigames(callback_query: CallbackQuery):
    """
    Handles the 'Minijuegos' button from the main menu.
    """
    await callback_query.answer("Aquí se mostrarán los minijuegos.", show_alert=True)

@router.callback_query(lambda c: c.data == "vip_zone")
async def handle_vip_zone(callback_query: CallbackQuery):
    """
    Handles the 'VIP Zone' button from the main menu.
    """
    try:
        # For now, we assume the user is not a VIP.
        is_vip = False
        
        title = "Zona VIP"
        content = "Bienvenido a la Zona VIP. Aquí encontrarás contenido exclusivo."
        
        message_text = format_section_message(title, content, emoji="💎")
        
        await callback_query.message.edit_text(
            text=message_text,
            reply_markup=get_vip_menu(is_vip),
            parse_mode="Markdown"
        )
        logger.info(f"User {callback_query.from_user.id} accessed the VIP zone.")
    except Exception as e:
        logger.error(f"Error in handle_vip_zone for user {callback_query.from_user.id}: {e}", exc_info=True)
        await callback_query.answer("😕 Hubo un problema al acceder a la Zona VIP. Intenta de nuevo.", show_alert=True)

@router.callback_query(lambda c: c.data == "channels")
async def handle_channels(callback_query: CallbackQuery):
    """
    Handles the 'Canales' button from the main menu.
    """
    await callback_query.answer("Aquí se mostrarán los canales.", show_alert=True)

@router.callback_query(lambda c: c.data == "admin")
async def handle_admin(callback_query: CallbackQuery):
    """
    Handles the 'Admin' button from the main menu.
    """
    await callback_query.answer("Aquí se mostrarán las opciones de administrador.", show_alert=True)
