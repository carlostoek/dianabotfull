import asyncio
import logging
from src.core.config import setup_logging
from src.core.event_bus import EventBus
from src.telegram_bot.core import TelegramBot
from src.telegram_bot.event_listeners import setup_telegram_event_listeners

# Initialize logger
setup_logging()
logger = logging.getLogger(__name__)

async def main():
    """Asynchronous entry point."""
    logger.info("Application starting up...")

    event_bus = EventBus()

    # Configure Telegram listeners for internal events
    setup_telegram_event_listeners(event_bus)
    
    # Initialize and start Telegram bot
    bot = TelegramBot(event_bus)
    await bot.start()

if __name__ == "__main__":
    asyncio.run(main())