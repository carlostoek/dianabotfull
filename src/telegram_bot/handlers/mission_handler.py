from telegram import Update, ParseMode
from telegram.ext import CallbackContext

from ...services.mission_service import MissionService
from ..menus.mission_menu import create_mission_layout

# In a real application, this service instance would be managed by a
# dependency injection container or a central app context.
mission_service = MissionService()

# This is a placeholder for updating the user's currency ("besitos").
# In a real implementation, this would call a dedicated ProfileService or UserRepository.
def _add_besitos_to_user(user_id: int, amount: int):
    """Simulates adding currency to a user's profile."""
    print(f"INFO: Adding {amount} besitos to user {user_id}. (Simulated)")
    # Example of what a real implementation would look like:
    # profile_service = ProfileService()
    # profile_service.add_besitos(user_id, amount)


def mission_command_handler(update: Update, context: CallbackContext) -> None:
    """
    Handles the /mision command, showing the user their daily mission.
    """
    user_id = update.effective_user.id
    mission = mission_service.get_daily_mission(user_id)

    if not mission:
        update.message.reply_text("Parece que no hay misiones disponibles hoy. ¡Vuelve mañana!")
        return

    text, keyboard = create_mission_layout(mission)
    update.message.reply_text(text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)


def claim_mission_callback_handler(update: Update, context: CallbackContext) -> None:
    """
    Handles the callback query for claiming a mission reward.
    """
    query = update.callback_query
    query.answer()  # Acknowledge the callback to remove the "loading" state on the client

    user_id = query.from_user.id
    callback_data = query.data
    
    # Expected callback_data format: "claim_mission_{mission_id}"
    try:
        mission_id = callback_data.split('_')[2]
    except IndexError:
        query.edit_message_text("Error: Callback inválido o malformado.")
        return

    reward = mission_service.complete_mission(user_id, mission_id)

    if reward is not None:
        # Add reward to the user's profile
        _add_besitos_to_user(user_id, reward)
        
        # Get the updated mission state to show the "Completed" view
        updated_mission = mission_service.get_daily_mission(user_id)
        text, keyboard = create_mission_layout(updated_mission)
        
        # Notify the user of their success and show the updated mission status
        query.edit_message_text(
            f"¡Felicidades! Has completado la misión y ganado **{reward} besitos**.\n\n{text}",
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        # This can happen if the mission was already claimed or if the state is inconsistent.
        query.edit_message_text(
            "Esta misión no se puede reclamar. Es posible que ya la hayas completado o que haya caducado.",
            reply_markup=query.message.reply_markup  # Keep the original keyboard
        )
