from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging

router = Router()
logger = logging.getLogger(__name__)

@router.message()
async def unrecognized_command_handler(message: types.Message):
    logger.warning(f"Comando no reconocido recibido de {message.from_user.id}: {message.text}")
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Di Hola", callback_data="say_hello")]
    ])
    
    await message.reply("Lo siento, no reconozco ese comando. Por favor, intenta de nuevo.", reply_markup=keyboard)

@router.callback_query(lambda c: c.data == 'say_hello')
async def say_hello_callback_handler(callback_query: types.CallbackQuery):
    await callback_query.answer("Hola!")
    await callback_query.message.answer("Hola!")
