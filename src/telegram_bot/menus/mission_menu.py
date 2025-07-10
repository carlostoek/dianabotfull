from telegram import InlineKeyboardButton, InlineKeyboardMarkup
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

    keyboard = []
    if not completed:
        # Callback data format is crucial for the handler
        keyboard.append([
            InlineKeyboardButton("✅ Reclamar Recompensa", callback_data=f"claim_mission_{mission['id']}")
        ])
    
    # Assuming a main menu callback exists
    keyboard.append([InlineKeyboardButton("‹ Volver al Menú", callback_data="main_menu")])

    return text, InlineKeyboardMarkup(keyboard)
