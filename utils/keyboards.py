
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- Teclado del Panel de Administración ---
def admin_panel_keyboard() -> InlineKeyboardMarkup:
    """
    Genera el teclado principal para el panel de administración.
    """
    buttons = [
        [InlineKeyboardButton(text="📊 Crear Tarifa", callback_data="create_tariff")],
        [InlineKeyboardButton(text="🔗 Generar Enlace", callback_data="generate_link")],
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
