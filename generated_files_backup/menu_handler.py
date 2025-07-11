from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from functools import partial

from src.telegram_bot.messages import (
    get_start_message,
    get_unavailable_section_message,
)

# Assuming MissionHandler is imported and its instance is passed or accessible
# from src.telegram_bot.handlers.mission_handler import MissionHandler

router = Router()

class MenuHandler:
    def __init__(self, mission_handler_instance=None):
        self.mission_handler = mission_handler_instance

    async def register_handlers(self):
        router.message.register(self.start_command_handler, Command("start"))
        router.callback_query.register(self.show_main_menu, F.data == "main_menu")

        # Register handlers for each main menu button
        router.callback_query.register(self.handle_missions_button, F.data == "missions_center")
        router.callback_query.register(partial(self.handle_unavailable_button, section_name="Regalo"), F.data == "daily_gift")
        router.callback_query.register(partial(self.handle_unavailable_button, section_name="Mi Perfil"), F.data == "profile")
        router.callback_query.register(partial(self.handle_unavailable_button, section_name="Mochila"), F.data == "backpack")
        router.callback_query.register(partial(self.handle_unavailable_button, section_name="Minijuegos"), F.data == "minijuegos")
        router.callback_query.register(partial(self.handle_unavailable_button, section_name="VIP Zone"), F.data == "vip_zone")
        router.callback_query.register(partial(self.handle_unavailable_button, section_name="Canales"), F.data == "channels")
        router.callback_query.register(partial(self.handle_unavailable_button, section_name="Admin"), F.data == "admin")

    async def start_command_handler(self, message: Message):
        username = message.from_user.first_name or message.from_user.full_name
        await message.answer(
            get_start_message(username),
            reply_markup=self._get_main_menu_keyboard()
        )

    async def show_main_menu(self, callback_query: CallbackQuery):
        username = callback_query.from_user.first_name or callback_query.from_user.full_name
        await callback_query.message.edit_text(
            get_start_message(username),
            reply_markup=self._get_main_menu_keyboard()
        )
        await callback_query.answer()

    async def handle_missions_button(self, callback_query: CallbackQuery):
        if self.mission_handler:
            # Delegate to MissionHandler's entry point
            await self.mission_handler.missions_command_handler(callback_query.message) # Pass message object
            await callback_query.answer()
        else:
            await self.handle_unavailable_button(callback_query, section_name="Misiones")

    async def handle_unavailable_button(self, callback_query: CallbackQuery, section_name: str):
        await callback_query.message.edit_text(
            get_unavailable_section_message(section_name),
            reply_markup=self._get_navigation_keyboard("main_menu") # Always provide navigation back to main menu
        )
        await callback_query.answer()

    def _get_main_menu_keyboard(self) -> InlineKeyboardMarkup:
        main_menu_buttons_data = [
            [{"text": " Misiones", "callback_data": "missions_center"}, {"text": " Regalo", "callback_data": "daily_gift"}],
            [{"text": " Mi Perfil", "callback_data": "profile"}, {"text": "️ Mochila", "callback_data": "backpack"}],
            [{"text": "️ Minijuegos", "callback_data": "minijuegos"}, {"text": " VIP Zone", "callback_data": "vip_zone"}],
            [{"text": " Canales", "callback_data": "channels"}, {"text": "⚙️ Admin", "callback_data": "admin"}]
        ]

        inline_keyboard = []
        for row in main_menu_buttons_data:
            current_row = []
            for button_text, callback_data in row:
                current_row.append(InlineKeyboardButton(text=button_text, callback_data=callback_data))
            inline_keyboard.append(current_row)
        
        # Add navigation row at the bottom
        inline_keyboard.append(self._get_navigation_keyboard_row("main_menu"))

        return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

    def _get_navigation_keyboard(self, current_context: str) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=[
            self._get_navigation_keyboard_row(current_context)
        ])

    def _get_navigation_keyboard_row(self, current_context: str) -> list[InlineKeyboardButton]:
        # For the main menu, 'Volver' just goes back to the main menu itself.
        # 'Inicio' also goes to the main menu.
        if current_context == "main_menu":
            return [
                InlineKeyboardButton(text="↩️ Volver", callback_data="main_menu"),
                InlineKeyboardButton(text="🏠 Inicio", callback_data="main_menu")
            ]
        # This part would be for other contexts, if this handler were to manage them.
        # For now, it's simplified to always return to main_menu.
        return [
            InlineKeyboardButton(text="↩️ Volver", callback_data="main_menu"),
            InlineKeyboardButton(text="🏠 Inicio", callback_data="main_menu")
        ]

# How to integrate in your main bot setup (e.g., main.py):
# from aiogram import Bot, Dispatcher
# from src.telegram_bot.handlers.menu_handler import MenuHandler
# from src.telegram_bot.handlers.mission_handler import MissionHandler
# from src.services.mission_service import MissionService

# bot = Bot(token="YOUR_BOT_TOKEN")
# dp = Dispatcher()

# mission_service = MissionService(...) # Initialize your MissionService
# mission_handler_instance = MissionHandler(mission_service) # Pass the service to mission handler
# menu_handler_instance = MenuHandler(mission_handler_instance) # Pass mission handler to menu handler

# await menu_handler_instance.register_handlers()
# await mission_handler_instance.register_handlers()

# dp.include_router(router) # This router is from menu_handler.py, but mission_handler also uses 'router'
# You should ensure only one router is included or merge them properly.
# A better approach might be to have a single main router and include sub-routers.
# For simplicity, I've used a single 'router' variable here, assuming it's shared or handled.
# If you have separate routers for each handler, you'd include both:
# dp.include_router(menu_handler_instance.router)
# dp.include_router(mission_handler_instance.router)
