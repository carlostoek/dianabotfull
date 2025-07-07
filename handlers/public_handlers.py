
from aiogram import Router, types, F
from aiogram.filters import CommandStart, ChatMemberUpdatedFilter
from aiogram.types import ChatMemberUpdated

from config import FREE_CHANNEL_ID
from services.user_service import get_or_create_user, ban_user

# --- Router Público ---
# Este router manejará los comandos y mensajes de usuarios no administradores.
# Es el punto de entrada para la mayoría de las interacciones del bot.
public_router = Router()

# --- Filtro para el Canal Gratuito ---
# Este filtro asegura que los manejadores de miembros del chat solo se ejecuten
# para eventos que ocurran en el canal gratuito especificado en la configuración.
public_router.chat_member.filter(F.chat.id == int(FREE_CHANNEL_ID))


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

# --- Manejador de Nuevos Miembros ---
@public_router.chat_member(ChatMemberUpdatedFilter(member_status_changed=(F.status == "member") | (F.status == "administrator")))
async def handle_new_member(event: ChatMemberUpdated):
    """
    Se activa cuando un usuario se une al canal gratuito.

    Registra al usuario en la base de datos y le envía un mensaje privado
    para iniciar el flujo de bienvenida y redes sociales.
    """
    user_info = event.new_chat_member.user
    await get_or_create_user(
        telegram_id=user_info.id,
        first_name=user_info.first_name,
        last_name=user_info.last_name,
        username=user_info.username
    )
    
    # Mensaje de bienvenida e inicio del flujo de redes sociales
    # (Aquí se puede añadir un delay configurable si se desea)
    await event.bot.send_message(
        user_info.id,
        f"¡Bienvenido al canal, {user_info.first_name}! 🎉\n\n"
        f"Nos alegra tenerte aquí. Síguenos en nuestras redes para no perderte nada:"
        # f"\n- Twitter: [Enlace a Twitter]"
        # f"\n- Instagram: [Enlace a Instagram]"
    )

# --- Manejador de Salidas o Expulsiones ---
@public_router.chat_member(ChatMemberUpdatedFilter(member_status_changed=(F.status == "left") | (F.status == "kicked")))
async def handle_member_left(event: ChatMemberUpdated):
    """
    Se activa cuando un usuario abandona o es expulsado del canal gratuito.

    Marca al usuario como baneado en el sistema para controlar su reingreso.
    """
    user_id = event.new_chat_member.user.id
    await ban_user(telegram_id=user_id)
    # Opcional: Registrar este evento en un canal de logs para administradores.
    # logger.info(f"El usuario {user_id} ha abandonado el canal y ha sido marcado como baneado.")
