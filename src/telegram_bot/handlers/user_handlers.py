from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from src.services import user_service
from src.telegram_bot.utils.keyboards import main_menu_keyboard, profile_menu_keyboard

router = Router()

@router.message(Command("start"))
async def start_cmd(message: Message):
    # Registrar usuario en el sistema
    await user_service.create_user(
        telegram_id=message.from_user.id,
        first_name=message.from_user.first_name,
        username=message.from_user.username
    )
    
    # Mostrar mensaje de bienvenida con teclado
    await message.answer(
        "✨ Bienvenido al universo exclusivo de Diana...",
        reply_markup=main_menu_keyboard()
    )

@router.callback_query(F.data == "show_profile")
async def show_profile(callback: CallbackQuery):
    user = await user_service.get_user(callback.from_user.id)
    await callback.message.edit_text(
        f" Tu perfil:\n\n"
        f" Besitos: {user.points}\n"
        f" Nivel: {user.level}\n"
        f" Fragmentos: {user.unlocked_fragments}",
        reply_markup=profile_menu_keyboard()
    )
