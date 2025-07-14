import os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from src.core.config import settings

class TelegramBot:
    def __init__(self, event_bus):
        self.bot = Bot(token=settings.TELEGRAM_TOKEN, parse_mode=ParseMode.HTML)
        self.dp = Dispatcher(storage=MemoryStorage())
        self.event_bus = event_bus # Store event_bus
        self.setup_handlers()

    def setup_handlers(self):
        # Aquí registraremos todos los handlers
        from .handlers import all_routers
        for router in all_routers:
            self.dp.include_router(router)

    async def start(self):
        await self.dp.start_polling(self.bot)