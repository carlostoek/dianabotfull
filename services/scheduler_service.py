import datetime
import logging
from aiogram import Bot, types
from config import VIP_CHANNEL_ID
from services.subscription_service import get_subscriptions_expiring_on, get_expired_subscriptions_and_mark_inactive
from services.channel_service import get_pending_join_requests, mark_join_request_processed
from services.post_service import get_scheduled_posts_to_send, mark_post_as_sent

logger = logging.getLogger(__name__)

# --- Tarea Diaria para Suscripciones ---
async def daily_subscription_check(bot: Bot):
    """
    Tarea diaria que gestiona el ciclo de vida de las suscripciones:
    1. Notifica a usuarios con suscripciones prontas a expirar (3 días y 1 día).
    2. Procesa las suscripciones expiradas: notifica y expulsa del canal VIP.
    """
    logger.info("Ejecutando tarea diaria de verificación de suscripciones...")
    
    # --- Notificaciones de Próxima Expiración ---
    notification_days = [3, 1]
    for days in notification_days:
        target_date = datetime.date.today() + datetime.timedelta(days=days)
        expiring_soon = await get_subscriptions_expiring_on(target_date)
        for subscription, user in expiring_soon:
            try:
                await bot.send_message(
                    user.telegram_id,
                    f"¡Hola {user.first_name}! 👋\n\n"
                    f"Tu suscripción VIP está a punto de expirar. Termina en {days} día(s).\n\n"
                    "¡No pierdas el acceso al contenido exclusivo!"
                )
                logger.info(f"Notificación de {days}-días enviada a {user.telegram_id}")
            except Exception as e:
                logger.error(f"Error enviando notificación de expiración a {user.telegram_id}: {e}")

    # --- Procesamiento de Suscripciones Expiradas ---
    expired_subscriptions = await get_expired_subscriptions_and_mark_inactive()
    for subscription, user in expired_subscriptions:
        try:
            # 1. Notificar al usuario
            await bot.send_message(
                user.telegram_id,
                "Tu suscripción VIP ha expirado. Gracias por haber sido parte de la comunidad."
            )
            # 2. Expulsar del canal VIP
            if VIP_CHANNEL_ID:
                await bot.ban_chat_member(chat_id=VIP_CHANNEL_ID, user_id=user.telegram_id)
                logger.info(f"Usuario {user.telegram_id} expulsado del canal VIP por expiración.")
            else:
                logger.warning(f"No se pudo expulsar a {user.telegram_id}, VIP_CHANNEL_ID no configurado.")
        except Exception as e:
            logger.error(f"Error procesando expiración para {user.telegram_id}: {e}")

    logger.info("Tarea diaria de suscripciones finalizada.")


# --- Tareas Frecuentes ---
async def process_pending_join_requests(bot: Bot):
    """
    Procesa las solicitudes de unión pendientes al canal gratuito.
    Se ejecuta frecuentemente.
    """
    logger.info("Ejecutando tarea: process_pending_join_requests")
    requests_to_process = await get_pending_join_requests()
    for req in requests_to_process:
        try:
            await bot.approve_chat_join_request(chat_id=req.chat_id, user_id=req.user_id)
            await mark_join_request_processed(req.id, True)
            logger.info(f"Solicitud de {req.user_id} a {req.chat_id} aceptada.")
        except Exception as e:
            await mark_join_request_processed(req.id, False)
            logger.error(f"Error aceptando solicitud de {req.user_id}: {e}")

async def send_scheduled_posts(bot: Bot):
    """
    Envía las publicaciones programadas.
    Se ejecuta frecuentemente.
    """
    logger.info("Ejecutando tarea: send_scheduled_posts")
    posts_to_send = await get_scheduled_posts_to_send()
    for post in posts_to_send:
        try:
            # Lógica de envío (simplificada para brevedad, la original es más compleja)
            await bot.send_message(chat_id=post.channel_id, text=post.message_text or "Publicación programada.")
            await mark_post_as_sent(post.id)
            logger.info(f"Publicación {post.id} enviada al canal {post.channel_id}.")
        except Exception as e:
            logger.error(f"Error enviando publicación programada {post.id}: {e}")