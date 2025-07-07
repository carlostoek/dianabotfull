
from aiogram.fsm.state import State, StatesGroup

class TariffCreation(StatesGroup):
    """
    Define los estados para el proceso de creación de una nueva tarifa.
    """
    waiting_for_duration = State()  # Esperando que el admin elija la duración
    waiting_for_price = State()     # Esperando que el admin ingrese el precio
    waiting_for_name = State()      # Esperando que el admin ingrese el nombre
    waiting_for_confirmation = State() # Esperando la confirmación final

class AddVipManual(StatesGroup):
    """
    Define los estados para el proceso de añadir un usuario VIP manualmente.
    """
    waiting_for_user_id = State() # Esperando el ID de Telegram del usuario
    waiting_for_tariff_selection = State() # Esperando la selección de la tarifa

class RemoveVipManual(StatesGroup):
    """
    Define los estados para el proceso de eliminar un usuario VIP manualmente.
    """
    waiting_for_user_id = State() # Esperando el ID de Telegram del usuario a eliminar

class ChannelConfig(StatesGroup):
    """
    Define los estados para el proceso de configuración de canales.
    """
    waiting_for_free_channel_id = State()
    waiting_for_vip_channel_id = State()
    waiting_for_free_channel_delay = State()

class PostCreation(StatesGroup):
    """
    Define los estados para el proceso de creación de una nueva publicación.
    """
    waiting_for_channel = State()
    waiting_for_type = State()
    waiting_for_text = State()
    waiting_for_media = State()
    waiting_for_options = State()
    waiting_for_button_type = State()
    waiting_for_button_text = State()
    waiting_for_button_url = State()
    waiting_for_button_callback = State()
    waiting_for_button_row_order = State()
    waiting_for_button_col_order = State()
    waiting_for_reaction_emoji = State()
    waiting_for_schedule_time = State()
    waiting_for_channel_selection = State()

class PostEditing(StatesGroup):
    """
    Define los estados para el proceso de edición de una publicación existente.
    """
    waiting_for_post_selection = State()
    waiting_for_edit_option = State()
    waiting_for_new_text = State()
    waiting_for_new_media = State()
    waiting_for_new_schedule_time = State()
    waiting_for_button_edit_selection = State()
    waiting_for_reaction_edit_selection = State()

class PostButtonCreation(StatesGroup):
    """
    Define los estados para la creación de botones dentro de una publicación.
    """
    waiting_for_type = State()
    waiting_for_text = State()
    waiting_for_url = State()
    waiting_for_callback = State()
    waiting_for_row_order = State()
    waiting_for_button_order = State()

class PostReactionCreation(StatesGroup):
    """
    Define los estados para la creación de reacciones dentro de una publicación.
    """
    waiting_for_emoji = State()

class PostScheduling(StatesGroup):
    """
    Define los estados para la programación de una publicación.
    """
    waiting_for_time = State()
