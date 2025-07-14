# src/telegram_bot/menus/mission_menu.py
"""
Creates the layout for a daily mission using aiogram.
"""
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import Dict, Tuple

def create_mission_layout(mission: Dict) -> Tuple[str, InlineKeyboardMarkup]:
    """
    Creates the text and keyboard for a daily mission.

    Args:
        mission: A dictionary containing mission details.

    Returns:
        A tuple with the formatted text and the inline keyboard.
    """
    if not mission:
        return "No hay misiones disponibles por hoy. Vuelve mañana.", None

    title = mission.get('title', 'Misión Desconocida')
    description = mission.get('description', 'Sin detalles.')
    reward = mission.get('reward', 0)
    completed = mission.get('completed', False)
    
    state_text = '✅ Completada' if completed else '⏳ Pendiente'
    text = (
        f"🌟 **Misión Diaria: {title}** 🌟\n\n"
        f"_{description}_\n\n"
        f"▫️ Recompensa: **{reward} besitos**\n"
        f"▫️ Estado: {state_text}"
    )

    builder = InlineKeyboardBuilder()
    if not completed:
        # Callback data format is crucial for the handler
        builder.button(text="✅ Reclamar Recompensa", callback_data=f"claim_mission_{mission['id']}")
    
    # Assuming a main menu callback exists
    builder.button(text="‹ Volver al Menú", callback_data="main_menu")
    builder.adjust(1) # Adjust to have one button per row

    return text, builder.as_markup()