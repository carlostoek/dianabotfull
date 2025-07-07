from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config import ADMIN_IDS
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