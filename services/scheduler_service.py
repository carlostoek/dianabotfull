import datetime
import logging

from aiogram import Bot
from sqlalchemy.future import select

from database.database import async_session
from database.models import Subscription, User
from config import VIP_CHANNEL_ID

logger = logging.getLogger(__name__)

async def check_and_notify_expirations(bot: Bot):
    """
    Verifica las suscripciones que están a punto de expirar y envía recordatorios.
    """
    logger.info("Ejecutando tarea: check_and_notify_expirations")
    async with async_session() as session:
        # Buscar suscripciones activas que expiran en las próximas 24 horas
        # y que aún no han sido notificadas (se podría añadir un campo `notified_for_expiration`)
        tomorrow = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        result = await session.execute(
            select(Subscription, User)
            .join(User)
            .filter(
                Subscription.is_active == True,
                Subscription.end_date <= tomorrow,
                Subscription.end_date > datetime.datetime.utcnow() # Que no haya expirado aún
            )
        )
        subscriptions_to_notify = result.all()

        for subscription, user in subscriptions_to_notify:
            try:
                await bot.send_message(
                    user.telegram_id,
                    f"¡Hola {user.first_name}! Tu suscripción VIP expira pronto.\n\n"
                    f"Expira el {subscription.end_date.strftime('%d/%m/%Y %H:%M')}. "
                    f"¡Renueva ahora para no perder el acceso!"
                    # Aquí se podría añadir un botón para renovar
                )
                logger.info(f"Notificación de expiración enviada a {user.telegram_id}")
            except Exception as e:
                logger.error(f"Error al enviar notificación a {user.telegram_id}: {e}")

async def check_and_expire_subscriptions(bot: Bot):
    """
    Verifica las suscripciones caducadas, expulsa a los usuarios del canal VIP
    y marca la suscripción como inactiva.
    """
    logger.info("Ejecutando tarea: check_and_expire_subscriptions")
    async with async_session() as session:
        # Buscar suscripciones activas que ya han expirado
        result = await session.execute(
            select(Subscription, User)
            .join(User)
            .filter(
                Subscription.is_active == True,
                Subscription.end_date <= datetime.datetime.utcnow()
            )
        )
        expired_subscriptions = result.all()

        for subscription, user in expired_subscriptions:
            try:
                # Expulsar al usuario del canal VIP
                await bot.ban_chat_member(chat_id=VIP_CHANNEL_ID, user_id=user.telegram_id)
                logger.info(f"Usuario {user.telegram_id} expulsado del canal VIP.")

                # Marcar suscripción como inactiva
                subscription.is_active = False
                await session.commit()
                logger.info(f"Suscripción de {user.telegram_id} marcada como inactiva.")

                # Notificar al usuario
                await bot.send_message(
                    user.telegram_id,
                    f"Tu suscripción VIP ha expirado. Has sido eliminado del canal VIP.\n\n"
                    f"¡Esperamos verte de nuevo pronto!"
                )
            except Exception as e:
                logger.error(f"Error al procesar expiración para {user.telegram_id}: {e}")
