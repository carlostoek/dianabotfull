from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config import ADMIN_IDS
from utils.states import TariffCreation
from utils.keyboards import admin_panel_keyboard, tariff_duration_keyboard, tariff_confirmation_keyboard, tariffs_keyboard
from services.subscription_service import create_tariff, get_all_tariffs, generate_invite_token

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

# --- Cancelación del Flujo ---
@admin_router.callback_query(F.data == "cancel_creation")
async def cancel_creation(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await callback.answer()
        return
    
    await state.clear()
    await callback.message.edit_text("Creación de tarifa cancelada.")
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