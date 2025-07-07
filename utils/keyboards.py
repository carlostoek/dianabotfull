
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
        [InlineKeyboardButton(text="⚙️ Configurar Canales", callback_data="configure_channels")],
        [InlineKeyboardButton(text="📝 Gestionar Publicaciones", callback_data="manage_posts")],
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

# --- Teclado de Configuración de Canales ---
def channel_config_keyboard() -> InlineKeyboardMarkup:
    """
    Genera el teclado para las opciones de configuración de canales.
    """
    buttons = [
        [InlineKeyboardButton(text="🆔 Configurar Canal Gratuito", callback_data="set_free_channel_id")],
        [InlineKeyboardButton(text="🆔 Configurar Canal VIP", callback_data="set_vip_channel_id")],
        [InlineKeyboardButton(text="⏳ Configurar Delay Canal Gratuito", callback_data="set_free_channel_delay")],
        [InlineKeyboardButton(text="↩️ Volver al Panel", callback_data="admin_panel")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# --- Teclado de Gestión de Publicaciones ---
def post_management_keyboard() -> InlineKeyboardMarkup:
    """
    Genera el teclado para las opciones de gestión de publicaciones.
    """
    buttons = [
        [InlineKeyboardButton(text="➕ Crear Publicación", callback_data="create_post")],
        [InlineKeyboardButton(text="✏️ Editar Publicación", callback_data="edit_post")],
        [InlineKeyboardButton(text="🗑️ Eliminar Publicación", callback_data="delete_post")],
        [InlineKeyboardButton(text="↩️ Volver al Panel", callback_data="admin_panel")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def post_type_selection_keyboard() -> InlineKeyboardMarkup:
    """
    Genera el teclado para seleccionar el tipo de contenido de la publicación.
    """
    buttons = [
        [InlineKeyboardButton(text="📝 Texto", callback_data="post_type_text")],
        [InlineKeyboardButton(text="📸 Foto", callback_data="post_type_photo")],
        [InlineKeyboardButton(text="🎥 Video", callback_data="post_type_video")],
        [InlineKeyboardButton(text="📄 Archivo", callback_data="post_type_document")],
        [InlineKeyboardButton(text="✨ Sticker/Animación", callback_data="post_type_animation")],
        [InlineKeyboardButton(text="❌ Cancelar", callback_data="cancel_operation")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def post_options_keyboard() -> InlineKeyboardMarkup:
    """
    Genera el teclado para las opciones adicionales de la publicación (protección, botones, reacciones).
    """
    buttons = [
        [InlineKeyboardButton(text="🔒 Proteger Mensaje", callback_data="toggle_protect_post")],
        [InlineKeyboardButton(text="🔗 Añadir Botones", callback_data="add_post_buttons")],
        [InlineKeyboardButton(text="😊 Añadir Reacciones", callback_data="add_post_reactions")],
        [InlineKeyboardButton(text="⏰ Programar Envío", callback_data="schedule_post")],
        [InlineKeyboardButton(text="✅ Finalizar Publicación", callback_data="finish_post_creation")],
        [InlineKeyboardButton(text="❌ Cancelar", callback_data="cancel_operation")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def post_button_type_keyboard() -> InlineKeyboardMarkup:
    """
    Genera el teclado para seleccionar el tipo de botón inline (URL o Callback).
    """
    buttons = [
        [InlineKeyboardButton(text="🌐 URL", callback_data="button_type_url")],
        [InlineKeyboardButton(text="↩️ Callback", callback_data="button_type_callback")],
        [InlineKeyboardButton(text="✅ Terminar Botones", callback_data="finish_adding_buttons")],
        [InlineKeyboardButton(text="❌ Cancelar", callback_data="cancel_operation")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def post_reactions_keyboard() -> InlineKeyboardMarkup:
    """
    Genera el teclado para añadir reacciones predefinidas o personalizadas.
    """
    buttons = [
        [InlineKeyboardButton(text="👍", callback_data="add_reaction_👍"), InlineKeyboardButton(text="❤️", callback_data="add_reaction_❤️")],
        [InlineKeyboardButton(text="🔥", callback_data="add_reaction_🔥"), InlineKeyboardButton(text="🎉", callback_data="add_reaction_🎉")],
        [InlineKeyboardButton(text="✍️ Personalizar", callback_data="add_custom_reaction")],
        [InlineKeyboardButton(text="✅ Terminar Reacciones", callback_data="finish_adding_reactions")],
        [InlineKeyboardButton(text="❌ Cancelar", callback_data="cancel_operation")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def post_list_keyboard(posts: list) -> InlineKeyboardMarkup:
    """
    Genera un teclado inline con una lista de publicaciones para seleccionar.
    """
    buttons = []
    for post in posts:
        status = "✅ Enviado" if post.is_sent else "⏰ Programado" if post.scheduled_time else "📝 Borrador"
        buttons.append([InlineKeyboardButton(text=f"ID: {post.id} - {status} - {post.message_text[:30]}...", callback_data=f"select_post_{post.id}")])
    buttons.append([InlineKeyboardButton(text="↩️ Volver a Gestión de Publicaciones", callback_data="manage_posts")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def post_edit_options_keyboard(post_id: int) -> InlineKeyboardMarkup:
    """
    Genera el teclado para las opciones de edición de una publicación específica.
    """
    buttons = [
        [InlineKeyboardButton(text="✏️ Editar Texto", callback_data=f"edit_post_text_{post_id}")],
        [InlineKeyboardButton(text="🖼️ Cambiar Media", callback_data=f"edit_post_media_{post_id}")],
        [InlineKeyboardButton(text="🔒 Proteger/Desproteger", callback_data=f"toggle_protect_post_{post_id}")],
        [InlineKeyboardButton(text="🔗 Editar Botones", callback_data=f"edit_post_buttons_{post_id}")],
        [InlineKeyboardButton(text="😊 Editar Reacciones", callback_data=f"edit_post_reactions_{post_id}")],
        [InlineKeyboardButton(text="⏰ Reprogramar Envío", callback_data=f"reschedule_post_{post_id}")],
        [InlineKeyboardButton(text="🗑️ Eliminar", callback_data=f"confirm_delete_post_{post_id}")],
        [InlineKeyboardButton(text="↩️ Volver a Lista de Publicaciones", callback_data="edit_post")],
        [InlineKeyboardButton(text="↩️ Volver al Panel", callback_data="admin_panel")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def confirm_delete_post_keyboard(post_id: int) -> InlineKeyboardMarkup:
    """
    Genera el teclado para confirmar la eliminación de una publicación.
    """
    buttons = [
        [InlineKeyboardButton(text="✅ Confirmar Eliminación", callback_data=f"delete_post_confirmed_{post_id}")],
        [InlineKeyboardButton(text="❌ Cancelar", callback_data="cancel_operation")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def send_post_channel_selection_keyboard() -> InlineKeyboardMarkup:
    """
    Genera el teclado para seleccionar el canal al que se enviará la publicación.
    """
    buttons = [
        [InlineKeyboardButton(text="Canal Gratuito", callback_data="select_send_channel_free")],
        [InlineKeyboardButton(text="Canal VIP", callback_data="select_send_channel_vip")],
        [InlineKeyboardButton(text="❌ Cancelar", callback_data="cancel_operation")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
