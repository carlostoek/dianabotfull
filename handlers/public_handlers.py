
from aiogram import Router, types
from aiogram.filters import CommandStart

# --- Router Público ---
# Este router manejará los comandos y mensajes de usuarios no administradores.
# Es el punto de entrada para la mayoría de las interacciones del bot.
public_router = Router()

# --- Comando /start ---
@public_router.message(CommandStart())
async def handle_start(message: types.Message):
    """
    Manejador para el comando /start.

    Saluda al usuario y le da la bienvenida al bot.
    Este es el primer punto de contacto y una buena forma de verificar
    que el bot está funcionando correctamente.
    """
    # Construimos el mensaje de bienvenida.
    # Usamos el nombre del usuario para personalizar el saludo.
    welcome_message = (
        f"¡Hola, {message.from_user.first_name}! 👋\n\n"
        f"Bienvenido a Diana Bot, tu asistente para la gestión de canales.\n\n"
        f"Aquí podrás acceder a contenido exclusivo y mucho más."
    )
    
    # Enviamos la respuesta al usuario.
    await message.answer(welcome_message)
