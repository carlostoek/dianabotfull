
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- Teclado del Panel de Administración ---
def admin_panel_keyboard() -> InlineKeyboardMarkup:
    """
    Genera el teclado principal para el panel de administración.
    """
    buttons = [
        [InlineKeyboardButton(text="📊 Crear Tarifa", callback_data="create_tariff")],
        [InlineKeyboardButton(text="🔗 Generar Enlace", callback_data="generate_link")],
        [InlineKeyboardButton(text="➕ Añadir VIP Manual", callback_data="add_vip_manual")],
        [InlineKeyboardButton(text="➖ Eliminar VIP Manual", callback_data="remove_vip_manual")],
        [InlineKeyboardButton(text="📋 Consultar Suscripciones", callback_data="view_subscriptions")],
        # [InlineKeyboardButton(text="📈 Ver Estadísticas", callback_data="view_stats")], # Ejemplo para futura expansión
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# --- Teclado para la Duración de la Tarifa ---
def tariff_duration_keyboard() -> InlineKeyboardMarkup:
    """
    Genera el teclado para seleccionar la duración de una nueva tarifa.
    """
    buttons = [
        [InlineKeyboardButton(text="1 Día", callback_data="duration_1"), InlineKeyboardButton(text="7 Días", callback_data="duration_7")],
        [InlineKeyboardButton(text="14 Días", callback_data="duration_14"), InlineKeyboardButton(text="30 Días", callback_data="duration_30")],
        [InlineKeyboardButton(text="Permanente (9999 días)", callback_data="duration_9999")],
        [InlineKeyboardButton(text="❌ Cancelar", callback_data="cancel_creation")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# --- Teclado de Confirmación de Tarifa ---
def tariff_confirmation_keyboard() -> InlineKeyboardMarkup:
    """
    Genera el teclado para confirmar o cancelar la creación de la tarifa.
    """
    buttons = [
        [InlineKeyboardButton(text="✅ Confirmar", callback_data="confirm_tariff")],
        [InlineKeyboardButton(text="❌ Cancelar", callback_data="cancel_creation")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def tariffs_keyboard(tariffs: list) -> InlineKeyboardMarkup:
    """
    Genera un teclado inline con las tarifas disponibles para seleccionar.
    """
    buttons = []
    for tariff in tariffs:
        buttons.append([InlineKeyboardButton(text=f"{tariff.name} (${tariff.price:.2f})", callback_data=f"select_tariff_{tariff.id}")])
    buttons.append([InlineKeyboardButton(text="↩️ Volver al Panel", callback_data="admin_panel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def tariffs_selection_keyboard(tariffs: list) -> InlineKeyboardMarkup:
    """
    Genera un teclado inline con las tarifas disponibles para seleccionar
    en el contexto de añadir un VIP manualmente.
    """
    buttons = []
    for tariff in tariffs:
        buttons.append([InlineKeyboardButton(text=f"{tariff.name} ({tariff.duration_days} días)", callback_data=f"select_manual_tariff_{tariff.id}")])
    buttons.append([InlineKeyboardButton(text="❌ Cancelar", callback_data="cancel_operation")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def confirm_user_action_keyboard(user_id: int, action: str) -> InlineKeyboardMarkup:
    """
    Genera un teclado para confirmar una acción sobre un usuario (ej. añadir/eliminar VIP).
    """
    buttons = [
        [InlineKeyboardButton(text="✅ Confirmar", callback_data=f"confirm_{action}_{user_id}")],
        [InlineKeyboardButton(text="❌ Cancelar", callback_data="cancel_operation")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
