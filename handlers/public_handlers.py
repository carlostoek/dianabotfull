
from aiogram import Router, types, F, Bot
from aiogram.filters import CommandStart, ChatMemberUpdatedFilter
from aiogram.types import ChatMemberUpdated, ChatJoinRequest

from config import FREE_CHANNEL_ID, VIP_CHANNEL_ID, FREE_CHANNEL_JOIN_DELAY_MINUTES
from services.user_service import get_or_create_user, ban_user
from services.subscription_service import validate_and_use_token
from services.channel_service import get_channel_by_id, create_join_request

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
    Si el comando /start incluye un token, intenta validarlo para una suscripción VIP.
    """
    # Extraer el argumento del comando /start (si existe)
    args = message.get_args()

    if args: # Si hay un argumento, asumimos que es un token de invitación
        user = await get_or_create_user(
            telegram_id=message.from_user.id,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            username=message.from_user.username
        )
        subscription = await validate_and_use_token(args, user)

        if subscription:
            # Generar un enlace de invitación al canal VIP
            # El bot debe ser administrador del canal VIP y tener el permiso 'Crear enlaces de invitación'
            try:
                invite_link = await message.bot.create_chat_invite_link(
                    chat_id=VIP_CHANNEL_ID,
                    member_limit=1, # Enlace de un solo uso
                    expire_date=subscription.end_date # Expira con la suscripción
                )
                await message.answer(
                    f"¡Felicidades, tu suscripción VIP ha sido activada! 🎉\n\n"
                    f"Aquí tienes tu enlace de acceso al canal VIP: {invite_link.invite_link}\n\n"
                    f"Este enlace es de un solo uso y expira con tu suscripción el {subscription.end_date.strftime('%d/%m/%Y %H:%M')}."
                )
            except Exception as e:
                await message.answer(
                    "Hubo un error al generar tu enlace de invitación al canal VIP. "
                    "Por favor, contacta a un administrador.\n\n" 
                    f"Error: {e}"
                )
        else:
            await message.answer(
                "El enlace de invitación no es válido, ha expirado o ya ha sido utilizado. "
                "Por favor, verifica tu enlace o contacta a un administrador."
            )
    else: # Comportamiento normal del comando /start sin argumentos
        welcome_message = (
            f"¡Hola, {message.from_user.first_name}! 👋\n\n"
            f"Bienvenido a Diana Bot, tu asistente para la gestión de canales.\n\n"
            f"Aquí podrás acceder a contenido exclusivo y mucho más."
        )
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

# --- Manejador de Solicitudes de Unión al Canal Gratuito ---
@public_router.chat_join_request(F.chat.id == int(FREE_CHANNEL_ID))
async def handle_join_request(request: ChatJoinRequest):
    """
    Maneja las solicitudes de unión al canal gratuito.

    Envía un mensaje de promoción de redes sociales al usuario y programa
    la aceptación automática después de un delay configurable.
    """
    user_info = request.from_user
    user = await get_or_create_user(
        telegram_id=user_info.id,
        first_name=user_info.first_name,
        last_name=user_info.last_name,
        username=user_info.username
    )

    # Obtener la configuración del canal para el delay
    free_channel_config = await get_channel_by_id(int(FREE_CHANNEL_ID))
    delay_minutes = free_channel_config.join_delay_minutes if free_channel_config else FREE_CHANNEL_JOIN_DELAY_MINUTES

    # Crear la solicitud de unión en la base de datos
    await create_join_request(
        user_id=user.telegram_id,
        chat_id=request.chat.id,
        delay_minutes=delay_minutes
    )

    # Mensaje de promoción de redes sociales
    await request.bot.send_message(
        user_info.id,
        f"¡Hola, {user_info.first_name}! 👋\n\n"
        f"Hemos recibido tu solicitud para unirte al canal gratuito. "
        f"Para agilizar tu acceso y no perderte nada, ¡síguenos en nuestras redes sociales!\n\n"
        f"[Enlace a Twitter]\n"
        f"[Enlace a Instagram]\n"
        f"[Enlace a Facebook]\n\n"
        f"Tu solicitud será procesada automáticamente en {delay_minutes} minutos. ¡Gracias por tu paciencia!"
    )

    # No aceptar la solicitud aquí, se hará automáticamente por el scheduler
    # await request.approve()
