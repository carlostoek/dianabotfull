
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from config import BOT_TOKEN
from database.database import create_tables
from handlers.public_handlers import public_router
from handlers.admin_handlers import admin_router
from services.scheduler_service import daily_subscription_check, process_pending_join_requests, send_scheduled_posts

# --- Configuración del Logging ---
# Configura el sistema de logging para mostrar información útil durante la ejecución.
# Esto es crucial para la depuración y el monitoreo del bot en producción.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

async def main():
    """
    Función principal que inicializa y ejecuta el bot.
    """
    logger.info("Iniciando el bot...")

    # --- Creación de Tablas ---
    # Llama a la función para asegurar que todas las tablas de la base de datos
    # estén creadas antes de que el bot comience a operar.
    logger.info("Creando tablas de la base de datos...")
    await create_tables()
    logger.info("Tablas creadas exitosamente.")

    # --- Inicialización del Bot y Dispatcher ---
    # `MemoryStorage` se usa para almacenar datos de estado finito (FSM). Es simple
    # y útil para empezar, pero para producción se podría considerar un almacenamiento
    # persistente como Redis.
    storage = MemoryStorage()
    
    # El objeto `Bot` es la interfaz principal para la API de Telegram.
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    
    # El `Dispatcher` es el responsable de procesar las actualizaciones (mensajes, etc.)
    # y distribuirlas a los manejadores (handlers) correspondientes.
    dp = Dispatcher(storage=storage)
    dp.allowed_updates = ["message", "chat_member", "chat_join_request"]

    # --- Registro de Routers ---
    # Aquí es donde conectamos los diferentes módulos de manejadores al dispatcher.
    dp.include_router(public_router)
    dp.include_router(admin_router)

    # --- Configuración y Arranque del Scheduler ---
    # El scheduler se encargará de ejecutar tareas programadas.
    scheduler = AsyncIOScheduler(timezone="UTC")
    
    # Tarea diaria para notificar y gestionar expiraciones de suscripciones.
    # Se ejecuta todos los días a las 09:00 UTC.
    scheduler.add_job(
        daily_subscription_check,
        trigger='cron',
        hour=9,
        minute=0,
        kwargs={'bot': bot},
        id='daily_subscription_check'
    )

    # Tareas frecuentes para solicitudes de unión y publicaciones programadas.
    scheduler.add_job(
        process_pending_join_requests,
        IntervalTrigger(minutes=1),
        kwargs={'bot': bot},
        id='process_join_requests'
    )
    scheduler.add_job(
        send_scheduled_posts,
        IntervalTrigger(minutes=1),
        kwargs={'bot': bot},
        id='send_scheduled_posts'
    )
    
    scheduler.start()
    logger.info("Scheduler iniciado.")

    # --- Arranque del Bot ---
    # `bot.delete_webhook` asegura que no haya un webhook configurado previamente.
    # `dp.start_polling` inicia el proceso de sondeo largo (long polling) para
    # recibir actualizaciones de Telegram.
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Bot iniciado y escuchando actualizaciones...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ocurrió un error durante la ejecución del bot: {e}")
    finally:
        # Cierre de la sesión del bot al finalizar y apagado del scheduler.
        scheduler.shutdown()
        await bot.session.close()
        logger.info("El bot se ha detenido.")

    

if __name__ == '__main__':
    # Punto de entrada para ejecutar el bot.
    # `asyncio.run` inicia el bucle de eventos de asyncio y ejecuta la corutina `main`.
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("El bot ha sido detenido manualmente.")
