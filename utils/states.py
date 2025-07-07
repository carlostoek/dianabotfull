
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
