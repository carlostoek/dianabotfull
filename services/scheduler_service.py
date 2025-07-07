import datetime
import logging

from aiogram import Bot
from sqlalchemy.future import select

from database.database import async_session
from database.models import Subscription, User
from config import VIP_CHANNEL_ID, FREE_CHANNEL_ID
from services.channel_service import get_pending_join_requests, mark_join_request_processed
from services.post_service import get_scheduled_posts_to_send, mark_post_as_sent

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

async def process_pending_join_requests(bot: Bot):
    """
    Procesa las solicitudes de unión pendientes al canal gratuito.

    Acepta automáticamente las solicitudes cuyo delay ha expirado.
    """
    logger.info("Ejecutando tarea: process_pending_join_requests")
    async with async_session() as session:
        requests_to_process = await get_pending_join_requests()

        for req in requests_to_process:
            try:
                # Intentar aceptar la solicitud
                await bot.approve_chat_join_request(chat_id=req.chat_id, user_id=req.user_id)
                await mark_join_request_processed(req.id, True)
                logger.info(f"Solicitud de unión de {req.user_id} al canal {req.chat_id} aceptada automáticamente.")
            except Exception as e:
                # Si falla (ej. usuario canceló la solicitud), marcar como procesada pero no aceptada
                await mark_join_request_processed(req.id, False)
                logger.error(f"Error al aceptar solicitud de unión de {req.user_id} al canal {req.chat_id}: {e}")

async def send_scheduled_posts(bot: Bot):
    """
    Envía las publicaciones programadas que ya han alcanzado su hora de envío.
    """
    logger.info("Ejecutando tarea: send_scheduled_posts")
    async with async_session() as session:
        posts_to_send = await get_scheduled_posts_to_send()

        for post in posts_to_send:
            try:
                # Construir el teclado inline si hay botones
                reply_markup = None
                if post.buttons:
                    keyboard_buttons = []
                    current_row = []
                    for btn in sorted(post.buttons, key=lambda x: (x.row_order, x.button_order)):
                        if btn.row_order != (current_row[0].row_order if current_row else btn.row_order):
                            keyboard_buttons.append(current_row)
                            current_row = []
                        
                        if btn.url:
                            current_row.append(types.InlineKeyboardButton(text=btn.text, url=btn.url))
                        elif btn.callback_data:
                            current_row.append(types.InlineKeyboardButton(text=btn.text, callback_data=btn.callback_data))
                    if current_row: # Add the last row
                        keyboard_buttons.append(current_row)
                    reply_markup = types.InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

                # Enviar el mensaje
                if post.media_type == 'photo':
                    await bot.send_photo(chat_id=post.channel_id, photo=post.media_file_id, caption=post.message_text, protect_content=post.is_protected, reply_markup=reply_markup)
                elif post.media_type == 'video':
                    await bot.send_video(chat_id=post.channel_id, video=post.media_file_id, caption=post.message_text, protect_content=post.is_protected, reply_markup=reply_markup)
                elif post.media_type == 'document':
                    await bot.send_document(chat_id=post.channel_id, document=post.media_file_id, caption=post.message_text, protect_content=post.is_protected, reply_markup=reply_markup)
                elif post.media_type == 'sticker':
                    await bot.send_sticker(chat_id=post.channel_id, sticker=post.media_file_id, protect_content=post.is_protected, reply_markup=reply_markup)
                elif post.media_type == 'animation':
                    await bot.send_animation(chat_id=post.channel_id, animation=post.media_file_id, caption=post.message_text, protect_content=post.is_protected, reply_markup=reply_markup)
                else: # Solo texto
                    await bot.send_message(chat_id=post.channel_id, text=post.message_text, protect_content=post.is_protected, reply_markup=reply_markup)
                
                await mark_post_as_sent(post.id)
                logger.info(f"Publicación {post.id} enviada al canal {post.channel_id}.")
            except Exception as e:
                logger.error(f"Error al enviar publicación {post.id} al canal {post.channel_id}: {e}")
