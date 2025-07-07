from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config import ADMIN_IDS, FREE_CHANNEL_ID, VIP_CHANNEL_ID
from utils.states import TariffCreation, AddVipManual, RemoveVipManual
from utils.keyboards import admin_panel_keyboard, tariff_duration_keyboard, tariff_confirmation_keyboard, tariffs_keyboard, tariffs_selection_keyboard, confirm_user_action_keyboard
from services.subscription_service import create_tariff, get_all_tariffs, generate_invite_token, create_manual_subscription, remove_subscription
from services.user_service import get_user_by_telegram_id

# --- Router de Administración ---
# Este router manejará los comandos exclusivos para los administradores del bot.
admin_router = Router()
# Aplicamos un filtro a todo el router para asegurar que solo los admins pueden usar estos handlers.
admin_router.message.filter(F.from_user.id.in_(ADMIN_IDS))
admin_router.callback_query.filter(F.from_user.id.in_(ADMIN_IDS))


# --- Comando /admin ---
@admin_router.message(Command("admin"))
@admin_router.callback_query(F.data == "admin_panel")
async def admin_panel(update: types.Message | types.CallbackQuery):
    """
    Muestra el panel de administración principal.
    """
    if isinstance(update, types.Message):
        await update.answer("Bienvenido al Panel de Administración.", reply_markup=admin_panel_keyboard())
    elif isinstance(update, types.CallbackQuery):
        await update.message.edit_text("Bienvenido al Panel de Administración.", reply_markup=admin_panel_keyboard())
        await update.answer()

# --- Inicio del Flujo de Creación de Tarifas ---
@admin_router.callback_query(F.data == "create_tariff")
async def start_tariff_creation(callback: types.CallbackQuery, state: FSMContext):
    """
    Inicia el proceso de creación de una nueva tarifa.
    """
    await callback.message.edit_text(
        "Paso 1: Selecciona la duración de la suscripción.",
        reply_markup=tariff_duration_keyboard()
    )
    await state.set_state(TariffCreation.waiting_for_duration)
    await callback.answer()

# --- Manejo de la Duración ---
@admin_router.callback_query(TariffCreation.waiting_for_duration, F.data.startswith("duration_"))
async def process_duration(callback: types.CallbackQuery, state: FSMContext):
    duration = int(callback.data.split("_")[1])
    await state.update_data(duration=duration)
    await callback.message.edit_text("Paso 2: Ingresa el precio de la tarifa (ej: 9.99).")
    await state.set_state(TariffCreation.waiting_for_price)
    await callback.answer()

# --- Manejo del Precio ---
@admin_router.message(TariffCreation.waiting_for_price)
async def process_price(message: types.Message, state: FSMContext):
    try:
        price = float(message.text)
        await state.update_data(price=price)
        await message.answer("Paso 3: Ingresa un nombre para la tarifa (ej: 'Plan Mensual').")
        await state.set_state(TariffCreation.waiting_for_name)
    except ValueError:
        await message.answer("Por favor, ingresa un número válido para el precio.")

# --- Manejo del Nombre y Confirmación ---
@admin_router.message(TariffCreation.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    name = message.text
    data = await state.get_data()
    duration = data.get("duration")
    price = data.get("price")

    await state.update_data(name=name)

    confirmation_text = (
        f"Resumen de la Tarifa:\n"
        f"- Nombre: {name}\n"
        f"- Duración: {duration} días\n"
        f"- Precio: ${price:.2f}\n\n"
        f"¿Confirmas la creación de esta tarifa?"
    )
    await message.answer(confirmation_text, reply_markup=tariff_confirmation_keyboard())
    await state.set_state(TariffCreation.waiting_for_confirmation)

# --- Finalización del Flujo ---
@admin_router.callback_query(TariffCreation.waiting_for_confirmation, F.data == "confirm_tariff")
async def confirm_creation(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await create_tariff(
        name=data.get("name"),
        duration_days=data.get("duration"),
        price=data.get("price")
    )
    await callback.message.edit_text("✅ ¡Tarifa creada exitosamente!")
    await state.clear()
    await callback.answer()

# --- Cancelación de Operación General ---
@admin_router.callback_query(F.data == "cancel_operation")
async def cancel_operation(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await callback.answer()
        return
    
    await state.clear()
    await callback.message.edit_text("Operación cancelada.", reply_markup=admin_panel_keyboard())
    await callback.answer()

# --- Añadir VIP Manualmente ---
@admin_router.callback_query(F.data == "add_vip_manual")
async def start_add_vip_manual(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Por favor, envía el ID de Telegram del usuario al que deseas añadir como VIP.")
    await state.set_state(AddVipManual.waiting_for_user_id)
    await callback.answer()

@admin_router.message(AddVipManual.waiting_for_user_id)
async def process_add_vip_user_id(message: types.Message, state: FSMContext):
    try:
        user_telegram_id = int(message.text)
        user = await get_user_by_telegram_id(user_telegram_id)
        if not user:
            await message.answer("Usuario no encontrado en la base de datos. Asegúrate de que el usuario haya interactuado con el bot al menos una vez.")
            return
        
        tariffs = await get_all_tariffs()
        if not tariffs:
            await message.answer("No hay tarifas creadas. Por favor, crea una tarifa primero.", reply_markup=admin_panel_keyboard())
            await state.clear()
            return

        await state.update_data(user_id=user_telegram_id)
        await message.answer(
            f"Usuario: {user.first_name} ({user.telegram_id}). Selecciona la tarifa para la suscripción:",
            reply_markup=tariffs_selection_keyboard(tariffs)
        )
        await state.set_state(AddVipManual.waiting_for_tariff_selection)
    except ValueError:
        await message.answer("ID de usuario inválido. Por favor, envía un número entero.")

@admin_router.callback_query(AddVipManual.waiting_for_tariff_selection, F.data.startswith("select_manual_tariff_"))
async def process_add_vip_tariff_selection(callback: types.CallbackQuery, state: FSMContext):
    tariff_id = int(callback.data.split("_")[3])
    data = await state.get_data()
    user_telegram_id = data.get("user_id")

    user = await get_user_by_telegram_id(user_telegram_id)
    if not user:
        await callback.message.edit_text("Error: Usuario no encontrado.", reply_markup=admin_panel_keyboard())
        await state.clear()
        await callback.answer()
        return

    subscription = await create_manual_subscription(user.id, tariff_id)
    if subscription:
        await callback.message.edit_text(f"✅ Suscripción VIP añadida manualmente para {user.first_name} ({user.telegram_id}). Expira el {subscription.end_date.strftime('%d/%m/%Y %H:%M')}.", reply_markup=admin_panel_keyboard())
    else:
        await callback.message.edit_text("Error al añadir la suscripción VIP. El usuario ya podría tener una suscripción activa.", reply_markup=admin_panel_keyboard())
    
    await state.clear()
    await callback.answer()

# --- Eliminar VIP Manualmente ---
@admin_router.callback_query(F.data == "remove_vip_manual")
async def start_remove_vip_manual(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Por favor, envía el ID de Telegram del usuario al que deseas eliminar como VIP.")
    await state.set_state(RemoveVipManual.waiting_for_user_id)
    await callback.answer()

@admin_router.message(RemoveVipManual.waiting_for_user_id)
async def process_remove_vip_user_id(message: types.Message, state: FSMContext):
    try:
        user_telegram_id = int(message.text)
        user = await get_user_by_telegram_id(user_telegram_id)
        if not user:
            await message.answer("Usuario no encontrado en la base de datos.")
            return
        
        # Confirmación antes de eliminar
        await message.answer(
            f"¿Estás seguro de que deseas eliminar la suscripción VIP de {user.first_name} ({user.telegram_id})?",
            reply_markup=confirm_user_action_keyboard(user_telegram_id, "remove_vip")
        )
        await state.clear() # Limpiamos el estado después de pedir confirmación
    except ValueError:
        await message.answer("ID de usuario inválido. Por favor, envía un número entero.")

@admin_router.callback_query(F.data.startswith("confirm_remove_vip_"))
async def confirm_remove_vip(callback: types.CallbackQuery, state: FSMContext):
    user_telegram_id = int(callback.data.split("_")[3])
    user = await get_user_by_telegram_id(user_telegram_id)

    if not user:
        await callback.message.edit_text("Error: Usuario no encontrado.", reply_markup=admin_panel_keyboard())
        await callback.answer()
        return

    success = await remove_subscription(user.id)
    if success:
        await callback.message.edit_text(f"✅ Suscripción VIP eliminada para {user.first_name} ({user.telegram_id}).", reply_markup=admin_panel_keyboard())
        # Opcional: Expulsar al usuario del canal VIP si estaba dentro
        # try:
        #     await callback.bot.ban_chat_member(chat_id=VIP_CHANNEL_ID, user_id=user.telegram_id)
        # except Exception as e:
        #     logger.error(f"Error al expulsar a {user.telegram_id} del canal VIP: {e}")
    else:
        await callback.message.edit_text("Error al eliminar la suscripción VIP o el usuario no tenía una suscripción activa.", reply_markup=admin_panel_keyboard())
    
    await callback.answer()

# --- Generación de Enlace ---
@admin_router.callback_query(F.data == "generate_link")
async def start_generate_link(callback: types.CallbackQuery):
    tariffs = await get_all_tariffs()
    if not tariffs:
        await callback.message.edit_text("No hay tarifas creadas. Por favor, crea una tarifa primero.", reply_markup=admin_panel_keyboard())
        await callback.answer()
        return
    
    await callback.message.edit_text(
        "Selecciona la tarifa para la que deseas generar un enlace:",
        reply_markup=tariffs_keyboard(tariffs)
    )
    await callback.answer()

@admin_router.callback_query(F.data.startswith("select_tariff_"))
async def process_select_tariff(callback: types.CallbackQuery):
    tariff_id = int(callback.data.split("_")[2])
    invite_token = await generate_invite_token(tariff_id=tariff_id)
    
    # Construir el enlace profundo. El nombre de usuario del bot se obtiene de la API de Telegram.
    # Es importante que el bot tenga un nombre de usuario para que este enlace funcione.
    bot_info = await callback.bot.get_me()
    deep_link = f"https://t.me/{bot_info.username}?start={invite_token.token}"
    
    await callback.message.edit_text(
        f"Aquí tienes el enlace de invitación para la tarifa seleccionada:\n\n`{deep_link}`\n\n" \
        f"Comparte este enlace con el usuario. Es de un solo uso y expira en 7 días.",
        parse_mode="Markdown",
        reply_markup=admin_panel_keyboard()
    )
    await callback.answer()

# --- Consultar Suscripciones Activas ---
@admin_router.callback_query(F.data == "view_subscriptions")
async def view_active_subscriptions(callback: types.CallbackQuery):
    subscriptions = await get_active_subscriptions()
    
    if not subscriptions:
        await callback.message.edit_text("No hay suscripciones VIP activas en este momento.", reply_markup=admin_panel_keyboard())
        await callback.answer()
        return

    response_text = "📋 **Suscripciones VIP Activas:**\n\n"
    for sub, user in subscriptions:
        response_text += (
            f"👤 Usuario: {user.first_name} ({user.telegram_id})\n"
            f"  - Inicio: {sub.start_date.strftime('%d/%m/%Y %H:%M')}\n"
            f"  - Fin: {sub.end_date.strftime('%d/%m/%Y %H:%M')}\n"
            f"  - Activa: {'Sí' if sub.is_active else 'No'}\n\n"
        )
    
    await callback.message.edit_text(response_text, parse_mode="Markdown", reply_markup=admin_panel_keyboard())
    await callback.answer()

# --- Configuración de Canales ---
@admin_router.callback_query(F.data == "configure_channels")
async def configure_channels(callback: types.CallbackQuery):
    await callback.message.edit_text("Selecciona la configuración de canal que deseas modificar:", reply_markup=channel_config_keyboard())
    await callback.answer()

@admin_router.callback_query(F.data == "set_free_channel_id")
async def set_free_channel_id(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Por favor, envía el ID del canal gratuito.")
    await state.set_state(ChannelConfig.waiting_for_free_channel_id)
    await callback.answer()

@admin_router.message(ChannelConfig.waiting_for_free_channel_id)
async def process_free_channel_id(message: types.Message, state: FSMContext):
    try:
        channel_id = int(message.text)
        await create_or_update_channel(name="free_channel", channel_id=channel_id)
        await message.answer("✅ ID del canal gratuito configurado exitosamente.", reply_markup=admin_panel_keyboard())
        await state.clear()
    except ValueError:
        await message.answer("ID de canal inválido. Por favor, envía un número entero.")

@admin_router.callback_query(F.data == "set_vip_channel_id")
async def set_vip_channel_id(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Por favor, envía el ID del canal VIP.")
    await state.set_state(ChannelConfig.waiting_for_vip_channel_id)
    await callback.answer()

@admin_router.message(ChannelConfig.waiting_for_vip_channel_id)
async def process_vip_channel_id(message: types.Message, state: FSMContext):
    try:
        channel_id = int(message.text)
        await create_or_update_channel(name="vip_channel", channel_id=channel_id)
        await message.answer("✅ ID del canal VIP configurado exitosamente.", reply_markup=admin_panel_keyboard())
        await state.clear()
    except ValueError:
        await message.answer("ID de canal inválido. Por favor, envía un número entero.")

@admin_router.callback_query(F.data == "set_free_channel_delay")
async def set_free_channel_delay(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Por favor, envía el delay en minutos para las solicitudes de unión al canal gratuito.")
    await state.set_state(ChannelConfig.waiting_for_free_channel_delay)
    await callback.answer()

@admin_router.message(ChannelConfig.waiting_for_free_channel_delay)
async def process_free_channel_delay(message: types.Message, state: FSMContext):
    try:
        delay = int(message.text)
        # Actualizar el canal gratuito con el nuevo delay
        free_channel = await get_channel_by_name("free_channel")
        if free_channel:
            await create_or_update_channel(name="free_channel", channel_id=free_channel.channel_id, join_delay_minutes=delay)
        else:
            await message.answer("Primero configura el ID del canal gratuito.", reply_markup=admin_panel_keyboard())
            await state.clear()
            return

        await message.answer(f"✅ Delay del canal gratuito configurado a {delay} minutos.", reply_markup=admin_panel_keyboard())
        await state.clear()
    except ValueError:
        await message.answer("Delay inválido. Por favor, envía un número entero.")

# --- Gestión de Publicaciones ---
@admin_router.callback_query(F.data == "manage_posts")
async def manage_posts(callback: types.CallbackQuery):
    await callback.message.edit_text("Selecciona una opción para gestionar publicaciones:", reply_markup=post_management_keyboard())
    await callback.answer()

@admin_router.callback_query(F.data == "create_post")
async def start_create_post(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Selecciona el tipo de contenido para la publicación:", reply_markup=post_type_selection_keyboard())
    await state.set_state(PostCreation.waiting_for_type)
    await callback.answer()

@admin_router.callback_query(PostCreation.waiting_for_type, F.data.startswith("post_type_"))
async def process_post_type(callback: types.CallbackQuery, state: FSMContext):
    post_type = callback.data.split("_")[2]
    await state.update_data(media_type=post_type)

    if post_type == "text":
        await callback.message.edit_text("Por favor, envía el texto de la publicación.")
        await state.set_state(PostCreation.waiting_for_text)
    else:
        await callback.message.edit_text(f"Por favor, envía el {post_type} para la publicación.")
        await state.set_state(PostCreation.waiting_for_media)
    await callback.answer()

@admin_router.message(PostCreation.waiting_for_text)
async def process_post_text(message: types.Message, state: FSMContext):
    await state.update_data(message_text=message.text)
    await message.answer("Texto recibido. Ahora puedes añadir opciones adicionales:", reply_markup=post_options_keyboard())
    await state.set_state(PostCreation.waiting_for_options)

@admin_router.message(PostCreation.waiting_for_media, F.photo | F.video | F.document | F.sticker | F.animation)
async def process_post_media(message: types.Message, state: FSMContext):
    media_type = (await state.get_data()).get("media_type")
    file_id = None
    if message.photo: file_id = message.photo[-1].file_id
    elif message.video: file_id = message.video.file_id
    elif message.document: file_id = message.document.file_id
    elif message.sticker: file_id = message.sticker.file_id
    elif message.animation: file_id = message.animation.file_id

    if file_id:
        await state.update_data(media_file_id=file_id, message_text=message.caption)
        await message.answer("Media recibida. Ahora puedes añadir opciones adicionales:", reply_markup=post_options_keyboard())
        await state.set_state(PostCreation.waiting_for_options)
    else:
        await message.answer("No se pudo obtener el ID del archivo. Por favor, intenta de nuevo.")

@admin_router.callback_query(PostCreation.waiting_for_options, F.data == "toggle_protect_post")
async def toggle_protect_post(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    is_protected = not data.get("is_protected", False)
    await state.update_data(is_protected=is_protected)
    status = "activada" if is_protected else "desactivada"
    await callback.message.edit_text(f"Protección de contenido {status}.", reply_markup=post_options_keyboard())
    await callback.answer()

@admin_router.callback_query(PostCreation.waiting_for_options, F.data == "add_post_buttons")
async def add_post_buttons(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(buttons=[]) # Inicializar lista de botones
    await callback.message.edit_text("Selecciona el tipo de botón que deseas añadir:", reply_markup=post_button_type_keyboard())
    await state.set_state(PostCreation.waiting_for_button_type)
    await callback.answer()

@admin_router.callback_query(PostCreation.waiting_for_button_type, F.data.startswith("button_type_"))
async def process_button_type(callback: types.CallbackQuery, state: FSMContext):
    button_type = callback.data.split("_")[2]
    await state.update_data(current_button_type=button_type)
    await callback.message.edit_text("Por favor, envía el texto del botón.")
    await state.set_state(PostCreation.waiting_for_button_text)
    await callback.answer()

@admin_router.message(PostCreation.waiting_for_button_text)
async def process_button_text(message: types.Message, state: FSMContext):
    await state.update_data(current_button_text=message.text)
    data = await state.get_data()
    button_type = data.get("current_button_type")

    if button_type == "url":
        await message.answer("Por favor, envía la URL para el botón.")
        await state.set_state(PostCreation.waiting_for_button_url)
    elif button_type == "callback":
        await message.answer("Por favor, envía el callback_data para el botón.")
        await state.set_state(PostCreation.waiting_for_button_callback)

@admin_router.message(PostCreation.waiting_for_button_url)
async def process_button_url(message: types.Message, state: FSMContext):
    data = await state.get_data()
    buttons = data.get("buttons", [])
    buttons.append({
        "text": data.get("current_button_text"),
        "url": message.text,
        "callback_data": None
    })
    await state.update_data(buttons=buttons)
    await message.answer("Botón URL añadido. ¿Deseas añadir más botones?", reply_markup=post_button_type_keyboard())
    await state.set_state(PostCreation.waiting_for_button_type)

@admin_router.message(PostCreation.waiting_for_button_callback)
async def process_button_callback(message: types.Message, state: FSMContext):
    data = await state.get_data()
    buttons = data.get("buttons", [])
    buttons.append({
        "text": data.get("current_button_text"),
        "url": None,
        "callback_data": message.text
    })
    await state.update_data(buttons=buttons)
    await message.answer("Botón Callback añadido. ¿Deseas añadir más botones?", reply_markup=post_button_type_keyboard())
    await state.set_state(PostCreation.waiting_for_button_type)

@admin_router.callback_query(PostCreation.waiting_for_button_type, F.data == "finish_adding_buttons")
async def finish_adding_buttons(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Botones configurados. Ahora puedes añadir más opciones:", reply_markup=post_options_keyboard())
    await state.set_state(PostCreation.waiting_for_options)
    await callback.answer()

@admin_router.callback_query(PostCreation.waiting_for_options, F.data == "add_post_reactions")
async def add_post_reactions(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(reactions=[]) # Inicializar lista de reacciones
    await callback.message.edit_text("Selecciona las reacciones que deseas añadir o envía un emoji personalizado:", reply_markup=post_reactions_keyboard())
    await state.set_state(PostCreation.waiting_for_reaction_emoji)
    await callback.answer()

@admin_router.callback_query(PostCreation.waiting_for_reaction_emoji, F.data.startswith("add_reaction_"))
async def process_predefined_reaction(callback: types.CallbackQuery, state: FSMContext):
    emoji = callback.data.split("_")[2]
    data = await state.get_data()
    reactions = data.get("reactions", [])
    reactions.append(emoji)
    await state.update_data(reactions=reactions)
    await callback.message.edit_text(f"Reacción {emoji} añadida. ¿Deseas añadir más reacciones?", reply_markup=post_reactions_keyboard())
    await callback.answer()

@admin_router.callback_query(PostCreation.waiting_for_reaction_emoji, F.data == "add_custom_reaction")
async def add_custom_reaction(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Por favor, envía el emoji personalizado para la reacción.")
    await state.set_state(PostCreation.waiting_for_reaction_emoji) # Permanece en el mismo estado para recibir el emoji
    await callback.answer()

@admin_router.message(PostCreation.waiting_for_reaction_emoji)
async def process_custom_reaction(message: types.Message, state: FSMContext):
    # Validar que el mensaje es un emoji
    if message.text and len(message.text) <= 2 and any(char in message.text for char in "😀😁😂🤣😃😄😅😆😉😊😋😎😏😒😞😔😟😠😡😤😢😭😦😧😨😩😫😮😱😲😳😴😵🤯🤠🥳🥸😎🤓🧐😕😟🙁☹️😮‍💨😤😠😡🤬🤯😳🥺🥹🥲😂🤣😃😄😅😆😉😊😋😎😏😒😞😔😟😠😡😤😢😭😦😧😨😩😫😮😱😲😳😴😵🤯🤠🥳🥸😎🤓🧐😕😟🙁☹️😮‍💨😤😠😡🤬🤯😳🥺🥹🥲"): # Simplificado, se puede mejorar la validación de emojis
        data = await state.get_data()
        reactions = data.get("reactions", [])
        reactions.append(message.text)
        await state.update_data(reactions=reactions)
        await message.answer(f"Reacción {message.text} añadida. ¿Deseas añadir más reacciones?", reply_markup=post_reactions_keyboard())
    else:
        await message.answer("Por favor, envía un emoji válido.")

@admin_router.callback_query(PostCreation.waiting_for_reaction_emoji, F.data == "finish_adding_reactions")
async def finish_adding_reactions(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Reacciones configuradas. Ahora puedes añadir más opciones:", reply_markup=post_options_keyboard())
    await state.set_state(PostCreation.waiting_for_options)
    await callback.answer()

@admin_router.callback_query(PostCreation.waiting_for_options, F.data == "schedule_post")
async def schedule_post(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Por favor, envía la fecha y hora de envío (YYYY-MM-DD HH:MM). Ejemplo: 2025-07-20 14:30")
    await state.set_state(PostCreation.waiting_for_schedule_time)
    await callback.answer()

@admin_router.message(PostCreation.waiting_for_schedule_time)
async def process_schedule_time(message: types.Message, state: FSMContext):
    try:
        scheduled_time = datetime.datetime.strptime(message.text, "%Y-%m-%d %H:%M")
        await state.update_data(scheduled_time=scheduled_time)
        await message.answer("Hora de envío programada. Ahora puedes añadir más opciones:", reply_markup=post_options_keyboard())
        await state.set_state(PostCreation.waiting_for_options)
    except ValueError:
        await message.answer("Formato de fecha y hora inválido. Por favor, usa YYYY-MM-DD HH:MM.")

@admin_router.callback_query(PostCreation.waiting_for_options, F.data == "finish_post_creation")
async def finish_post_creation(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    # Aquí se debería seleccionar el canal al que se enviará la publicación
    # Por ahora, usaremos el FREE_CHANNEL_ID como ejemplo.
    # En futuras fases, se podría añadir un paso para seleccionar el canal.
    channel_id = FREE_CHANNEL_ID # O VIP_CHANNEL_ID, o un ID seleccionado por el admin

    data = await state.get_data()
    
    # Determinar qué canales están configurados
    free_configured = FREE_CHANNEL_ID is not None
    vip_configured = VIP_CHANNEL_ID is not None

    if not free_configured and not vip_configured:
        await callback.message.edit_text(
            "❌ No hay canales configurados. Por favor, configura al menos un canal (gratuito o VIP) en la sección de 'Configuración de Canales' para poder enviar publicaciones.",
            reply_markup=admin_panel_keyboard()
        )
        await state.clear()
        await callback.answer()
        return
    
    if free_configured and not vip_configured:
        channel_id = FREE_CHANNEL_ID
        await callback.message.edit_text(
            "✅ Solo el canal gratuito está configurado. La publicación se enviará al canal gratuito.",
            reply_markup=admin_panel_keyboard()
        )
        # Proceder con la creación de la publicación para el canal gratuito
        post = await create_post(
            channel_id=channel_id,
            message_text=data.get("message_text"),
            media_type=data.get("media_type"),
            media_file_id=data.get("media_file_id"),
            is_protected=data.get("is_protected", False),
            scheduled_time=data.get("scheduled_time"),
            buttons_data=data.get("buttons"),
            reactions_data=data.get("reactions")
        )
        await callback.message.edit_text(f"✅ Publicación creada exitosamente con ID: {post.id}.", reply_markup=admin_panel_keyboard())
        await state.clear()
        await callback.answer()
        return

    if not free_configured and vip_configured:
        channel_id = VIP_CHANNEL_ID
        await callback.message.edit_text(
            "✅ Solo el canal VIP está configurado. La publicación se enviará al canal VIP.",
            reply_markup=admin_panel_keyboard()
        )
        # Proceder con la creación de la publicación para el canal VIP
        post = await create_post(
            channel_id=channel_id,
            message_text=data.get("message_text"),
            media_type=data.get("media_type"),
            media_file_id=data.get("media_file_id"),
            is_protected=data.get("is_protected", False),
            scheduled_time=data.get("scheduled_time"),
            buttons_data=data.get("buttons"),
            reactions_data=data.get("reactions")
        )
        await callback.message.edit_text(f"✅ Publicación creada exitosamente con ID: {post.id}.", reply_markup=admin_panel_keyboard())
        await state.clear()
        await callback.answer()
        return

    if free_configured and vip_configured:
        # Ambos canales configurados, pedir al admin que seleccione
        await callback.message.edit_text(
            "Ambos canales (gratuito y VIP) están configurados. Por favor, selecciona el canal al que deseas enviar la publicación:",
            reply_markup=send_post_channel_selection_keyboard() # Necesitamos crear este teclado
        )
        await state.set_state(PostCreation.waiting_for_channel_selection) # Necesitamos crear este estado
        await callback.answer()
        return

@admin_router.callback_query(PostCreation.waiting_for_channel_selection, F.data.startswith("select_send_channel_"))
async def process_channel_selection_for_post(callback: types.CallbackQuery, state: FSMContext):
    selected_channel_type = callback.data.split("_")[3]
    data = await state.get_data()

    channel_id = None
    if selected_channel_type == "free":
        channel_id = FREE_CHANNEL_ID
    elif selected_channel_type == "vip":
        channel_id = VIP_CHANNEL_ID

    if channel_id is None:
        await callback.message.edit_text("❌ Error: El canal seleccionado no está configurado. Por favor, inténtalo de nuevo o configura el canal.", reply_markup=admin_panel_keyboard())
        await state.clear()
        await callback.answer()
        return

    post = await create_post(
        channel_id=channel_id,
        message_text=data.get("message_text"),
        media_type=data.get("media_type"),
        media_file_id=data.get("media_file_id"),
        is_protected=data.get("is_protected", False),
        scheduled_time=data.get("scheduled_time"),
        buttons_data=data.get("buttons"),
        reactions_data=data.get("reactions")
    )
    await callback.message.edit_text(f"✅ Publicación creada exitosamente con ID: {post.id}.", reply_markup=admin_panel_keyboard())
    await state.clear()
    await callback.answer()

@admin_router.callback_query(F.data == "edit_post")
async def start_edit_post(callback: types.CallbackQuery, state: FSMContext):
    posts = await get_all_posts() # Necesitamos una función para obtener todas las publicaciones
    if not posts:
        await callback.message.edit_text("No hay publicaciones para editar.", reply_markup=post_management_keyboard())
        await callback.answer()
        return
    
    await callback.message.edit_text("Selecciona la publicación que deseas editar:", reply_markup=post_list_keyboard(posts))
    await state.set_state(PostEditing.waiting_for_post_selection)
    await callback.answer()

@admin_router.callback_query(PostEditing.waiting_for_post_selection, F.data.startswith("select_post_"))
async def select_post_to_edit(callback: types.CallbackQuery, state: FSMContext):
    post_id = int(callback.data.split("_")[2])
    post = await get_post_by_id(post_id)
    if not post:
        await callback.message.edit_text("Publicación no encontrada.", reply_markup=post_management_keyboard())
        await state.clear()
        await callback.answer()
        return
    
    await state.update_data(current_post_id=post_id)
    await callback.message.edit_text(f"Has seleccionado la publicación ID: {post_id}. ¿Qué deseas editar?", reply_markup=post_edit_options_keyboard(post_id))
    await state.set_state(PostEditing.waiting_for_edit_option)
    await callback.answer()

@admin_router.callback_query(PostEditing.waiting_for_edit_option, F.data.startswith("edit_post_text_"))
async def edit_post_text(callback: types.CallbackQuery, state: FSMContext):
    post_id = int(callback.data.split("_")[3])
    await state.update_data(current_post_id=post_id)
    await callback.message.edit_text("Por favor, envía el nuevo texto para la publicación.")
    await state.set_state(PostEditing.waiting_for_new_text)
    await callback.answer()

@admin_router.message(PostEditing.waiting_for_new_text)
async def process_new_post_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    post_id = data.get("current_post_id")
    await update_post(post_id, message_text=message.text)
    await message.answer("Texto de la publicación actualizado.", reply_markup=post_edit_options_keyboard(post_id))
    await state.set_state(PostEditing.waiting_for_edit_option)

@admin_router.callback_query(PostEditing.waiting_for_edit_option, F.data.startswith("edit_post_media_"))
async def edit_post_media(callback: types.CallbackQuery, state: FSMContext):
    post_id = int(callback.data.split("_")[3])
    await state.update_data(current_post_id=post_id)
    await callback.message.edit_text("Por favor, envía el nuevo archivo multimedia (foto, video, documento, sticker, animación) para la publicación.")
    await state.set_state(PostEditing.waiting_for_new_media)
    await callback.answer()

@admin_router.message(PostEditing.waiting_for_new_media, F.photo | F.video | F.document | F.sticker | F.animation)
async def process_new_post_media(message: types.Message, state: FSMContext):
    data = await state.get_data()
    post_id = data.get("current_post_id")
    file_id = None
    media_type = None

    if message.photo: 
        file_id = message.photo[-1].file_id
        media_type = "photo"
    elif message.video: 
        file_id = message.video.file_id
        media_type = "video"
    elif message.document: 
        file_id = message.document.file_id
        media_type = "document"
    elif message.sticker: 
        file_id = message.sticker.file_id
        media_type = "sticker"
    elif message.animation: 
        file_id = message.animation.file_id
        media_type = "animation"

    if file_id:
        await update_post(post_id, media_type=media_type, media_file_id=file_id, message_text=message.caption)
        await message.answer("Multimedia de la publicación actualizada.", reply_markup=post_edit_options_keyboard(post_id))
        await state.set_state(PostEditing.waiting_for_edit_option)
    else:
        await message.answer("No se pudo obtener el ID del archivo. Por favor, intenta de nuevo.")

@admin_router.callback_query(PostEditing.waiting_for_edit_option, F.data.startswith("toggle_protect_post_"))
async def toggle_edit_post_protect(callback: types.CallbackQuery, state: FSMContext):
    post_id = int(callback.data.split("_")[3])
    post = await get_post_by_id(post_id)
    if post:
        new_protected_status = not post.is_protected
        await update_post(post_id, is_protected=new_protected_status)
        status = "activada" if new_protected_status else "desactivada"
        await callback.message.edit_text(f"Protección de contenido {status} para la publicación ID: {post_id}.", reply_markup=post_edit_options_keyboard(post_id))
    else:
        await callback.message.edit_text("Publicación no encontrada.")
    await callback.answer()

@admin_router.callback_query(PostEditing.waiting_for_edit_option, F.data.startswith("edit_post_buttons_"))
async def edit_post_buttons(callback: types.CallbackQuery, state: FSMContext):
    post_id = int(callback.data.split("_")[3])
    await state.update_data(current_post_id=post_id)
    # Aquí se podría mostrar los botones actuales y opciones para añadir/eliminar/editar
    await callback.message.edit_text("Funcionalidad de edición de botones en desarrollo. Por ahora, puedes añadir nuevos botones.", reply_markup=post_button_type_keyboard())
    await state.set_state(PostCreation.waiting_for_button_type) # Reutilizamos el estado de creación de botones
    await callback.answer()

@admin_router.callback_query(PostEditing.waiting_for_edit_option, F.data.startswith("edit_post_reactions_"))
async def edit_post_reactions(callback: types.CallbackQuery, state: FSMContext):
    post_id = int(callback.data.split("_")[3])
    await state.update_data(current_post_id=post_id)
    # Aquí se podría mostrar las reacciones actuales y opciones para añadir/eliminar
    await callback.message.edit_text("Funcionalidad de edición de reacciones en desarrollo. Por ahora, puedes añadir nuevas reacciones.", reply_markup=post_reactions_keyboard())
    await state.set_state(PostCreation.waiting_for_reaction_emoji) # Reutilizamos el estado de creación de reacciones
    await callback.answer()

@admin_router.callback_query(PostEditing.waiting_for_edit_option, F.data.startswith("reschedule_post_"))
async def reschedule_post(callback: types.CallbackQuery, state: FSMContext):
    post_id = int(callback.data.split("_")[2])
    await state.update_data(current_post_id=post_id)
    await callback.message.edit_text("Por favor, envía la nueva fecha y hora de envío (YYYY-MM-DD HH:MM). Ejemplo: 2025-07-20 14:30")
    await state.set_state(PostEditing.waiting_for_new_schedule_time)
    await callback.answer()

@admin_router.message(PostEditing.waiting_for_new_schedule_time)
async def process_new_schedule_time(message: types.Message, state: FSMContext):
    data = await state.get_data()
    post_id = data.get("current_post_id")
    try:
        scheduled_time = datetime.datetime.strptime(message.text, "%Y-%m-%d %H:%M")
        await update_post(post_id, scheduled_time=scheduled_time, is_sent=False) # Resetear is_sent si se reprograma
        await message.answer("Hora de envío reprogramada.", reply_markup=post_edit_options_keyboard(post_id))
        await state.set_state(PostEditing.waiting_for_edit_option)
    except ValueError:
        await message.answer("Formato de fecha y hora inválido. Por favor, usa YYYY-MM-DD HH:MM.")

@admin_router.callback_query(F.data.startswith("confirm_delete_post_"))
async def confirm_delete_post(callback: types.CallbackQuery):
    post_id = int(callback.data.split("_")[3])
    await callback.message.edit_text(f"¿Estás seguro de que deseas eliminar la publicación ID: {post_id}?", reply_markup=confirm_delete_post_keyboard(post_id))
    await callback.answer()

@admin_router.callback_query(F.data.startswith("delete_post_confirmed_"))
async def delete_post_confirmed(callback: types.CallbackQuery, state: FSMContext):
    post_id = int(callback.data.split("_")[3])
    success = await delete_post(post_id)
    if success:
        await callback.message.edit_text(f"✅ Publicación ID: {post_id} eliminada exitosamente.", reply_markup=admin_panel_keyboard())
    else:
        await callback.message.edit_text("Error al eliminar la publicación.", reply_markup=admin_panel_keyboard())
    await state.clear()
    await callback.answer()

# --- Configuración de Canales ---
@admin_router.callback_query(F.data == "configure_channels")
async def configure_channels(callback: types.CallbackQuery):
    await callback.message.edit_text("Selecciona la configuración de canal que deseas modificar:", reply_markup=channel_config_keyboard())
    await callback.answer()

@admin_router.callback_query(F.data == "set_free_channel_id")
async def set_free_channel_id(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Por favor, envía el ID del canal gratuito.")
    await state.set_state(ChannelConfig.waiting_for_free_channel_id)
    await callback.answer()

@admin_router.message(ChannelConfig.waiting_for_free_channel_id)
async def process_free_channel_id(message: types.Message, state: FSMContext):
    try:
        channel_id = int(message.text)
        await create_or_update_channel(name="free_channel", channel_id=channel_id)
        await message.answer("✅ ID del canal gratuito configurado exitosamente.", reply_markup=admin_panel_keyboard())
        await state.clear()
    except ValueError:
        await message.answer("ID de canal inválido. Por favor, envía un número entero.")

@admin_router.callback_query(F.data == "set_vip_channel_id")
async def set_vip_channel_id(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Por favor, envía el ID del canal VIP.")
    await state.set_state(ChannelConfig.waiting_for_vip_channel_id)
    await callback.answer()

@admin_router.message(ChannelConfig.waiting_for_vip_channel_id)
async def process_vip_channel_id(message: types.Message, state: FSMContext):
    try:
        channel_id = int(message.text)
        await create_or_update_channel(name="vip_channel", channel_id=channel_id)
        await message.answer("✅ ID del canal VIP configurado exitosamente.", reply_markup=admin_panel_keyboard())
        await state.clear()
    except ValueError:
        await message.answer("ID de canal inválido. Por favor, envía un número entero.")

@admin_router.callback_query(F.data == "set_free_channel_delay")
async def set_free_channel_delay(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Por favor, envía el delay en minutos para las solicitudes de unión al canal gratuito.")
    await state.set_state(ChannelConfig.waiting_for_free_channel_delay)
    await callback.answer()

@admin_router.message(ChannelConfig.waiting_for_free_channel_delay)
async def process_free_channel_delay(message: types.Message, state: FSMContext):
    try:
        delay = int(message.text)
        # Actualizar el canal gratuito con el nuevo delay
        free_channel = await get_channel_by_name("free_channel")
        if free_channel:
            await create_or_update_channel(name="free_channel", channel_id=free_channel.channel_id, join_delay_minutes=delay)
        else:
            await message.answer("Primero configura el ID del canal gratuito.", reply_markup=admin_panel_keyboard())
            await state.clear()
            return

        await message.answer(f"✅ Delay del canal gratuito configurado a {delay} minutos.", reply_markup=admin_panel_keyboard())
        await state.clear()
    except ValueError:
        await message.answer("Delay inválido. Por favor, envía un número entero.")