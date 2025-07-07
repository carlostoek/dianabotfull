
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database.database import create_tables
from handlers.public_handlers import public_router

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
    bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
    
    # El `Dispatcher` es el responsable de procesar las actualizaciones (mensajes, etc.)
    # y distribuirlas a los manejadores (handlers) correspondientes.
    dp = Dispatcher(storage=storage)
    dp.allowed_updates = ["message", "chat_member"]

    # --- Registro de Routers ---
    # Aquí es donde conectamos los diferentes módulos de manejadores al dispatcher.
    # Por ahora, solo tenemos el router público.
    dp.include_router(public_router)
    # Próximamente añadiremos más routers aquí (admin_router, subscription_router, etc.)

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
        # Cierre de la sesión del bot al finalizar.
        await bot.session.close()
        logger.info("El bot se ha detenido.")

if __name__ == '__main__':
    # Punto de entrada para ejecutar el bot.
    # `asyncio.run` inicia el bucle de eventos de asyncio y ejecuta la corutina `main`.
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("El bot ha sido detenido manualmente.")
