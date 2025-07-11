import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types

# Importar los handlers
from src.telegram_bot.handlers.menu_handler import MenuHandler
from src.telegram_bot.handlers.mission_handler import MissionHandler

# Importar los servicios
from src.services.mission_service import MissionService

# Configuración básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)

# Obtener el token del bot desde una variable de entorno o directamente
# Es recomendable usar variables de entorno para tokens sensibles
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN") # Reemplaza YOUR_BOT_TOKEN con tu token real o configúralo en .env

async def main():
    logger.info("DianaBot: Iniciando operaciones...")

    # Inicializar el bot y el dispatcher
    bot = Bot(token=BOT_TOKEN, parse_mode="MarkdownV2") # Usamos MarkdownV2 para el formato de los mensajes
    dp = Dispatcher()

    # --- Inicialización de Servicios ---
    # Aquí inicializarías MissionService con sus dependencias reales (ej. base de datos)
    # Por ahora, una instancia simple para que el código compile.
    mission_service = MissionService() 

    # --- Inicialización de Handlers ---
    # Pasamos la instancia de MissionService a MissionHandler
    mission_handler_instance = MissionHandler(mission_service)
    # Pasamos la instancia de MissionHandler a MenuHandler
    menu_handler_instance = MenuHandler(mission_handler_instance)

    # --- Registro de Handlers y Routers ---
    # Registrar los handlers de cada clase
    await menu_handler_instance.register_handlers()
    await mission_handler_instance.register_handlers()

    # Incluir los routers de cada handler en el Dispatcher principal
    # Cada handler tiene su propio 'router' definido en su archivo.
    dp.include_router(menu_handler_instance.router)
    dp.include_router(mission_handler_instance.router)

    logger.info("Handlers y routers registrados. Iniciando polling...")
    # Iniciar el polling del bot
    # Esto hará que el bot escuche por nuevas actualizaciones
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot detenido manualmente.")
    except Exception as e:
        logger.error(f"Error inesperado al iniciar el bot: {e}")