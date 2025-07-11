from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from src.services.mission_service import MissionService
from src.core.models import MissionType, MissionStatus # Assuming these enums are here
from src.telegram_bot.messages import (
    get_missions_center_message,
    format_mission_message,
    get_mission_accepted_message,
    get_no_missions_message,
)
from src.utils.text_utils import create_progress_bar # Assuming this utility is here

router = Router()

class MissionHandler:
    def __init__(self, mission_service: MissionService):
        self.mission_service = mission_service

    async def register_handlers(self):
        router.message.register(self.missions_command_handler, Command("misiones"))
        router.callback_query.register(self.show_missions_list, F.data == "missions_list")
        router.callback_query.register(self.show_mission_details, F.data.startswith("mission_details_"))
        router.callback_query.register(self.accept_mission, F.data.startswith("mission_accept_"))
        router.callback_query.register(self.show_active_missions, F.data == "missions_active")
        # Assuming 'main_menu' callback is handled elsewhere or leads to a main menu handler
        # For now, just ensure it's a valid callback_data

    async def missions_command_handler(self, message: Message):
        user_id = message.from_user.id
        username = message.from_user.first_name # Or full_name

        await message.answer(
            get_missions_center_message(username),
            reply_markup=self._get_missions_center_keyboard()
        )

    async def show_missions_list(self, callback_query: CallbackQuery):
        user_id = callback_query.from_user.id
        available_missions = self.mission_service.get_available_missions(user_id)

        if not available_missions:
            await callback_query.message.edit_text(
                get_no_missions_message("disponibles"),
                reply_markup=self._get_navigation_keyboard("missions_list")
            )
            await callback_query.answer()
            return

        # Display one mission at a time, or a list of buttons to view each
        # For simplicity, let's list them as buttons first
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        for mission_id, mission_data in available_missions.items():
            keyboard.inline_keyboard.append([
                InlineKeyboardButton(
                    text=f"🌟 {mission_data['title']}",
                    callback_data=f"mission_details_{mission_id}"
                )
            ])
        
        keyboard.inline_keyboard.append(self._get_navigation_keyboard_row("missions_list"))

        await callback_query.message.edit_text(
            "Aquí están las misiones que te esperan. Elige sabiamente, o no.",
            reply_markup=keyboard
        )
        await callback_query.answer()

    async def show_mission_details(self, callback_query: CallbackQuery):
        user_id = callback_query.from_user.id
        mission_id = callback_query.data.split("_")[2]

        mission_data = self.mission_service.get_mission_data(mission_id) # Assuming a method to get full mission data
        if not mission_data:
            await callback_query.message.edit_text(
                "Esa misión... no la encuentro. ¿Quizás nunca existió?",
                reply_markup=self._get_navigation_keyboard("missions_list")
            )
            await callback_query.answer()
            return

        # Check if mission is available for the user (e.g., not accepted yet, prerequisites met)
        # This logic should ideally be in MissionService.get_mission_data_for_user
        # For now, we'll assume mission_data includes status for the current user
        # Or we fetch it separately
        user_mission_status = self.mission_service.get_user_mission_status(user_id, mission_id)
        mission_data['status'] = user_mission_status # Update status for formatting

        # Add progress if accepted
        if user_mission_status == MissionStatus.ACCEPTED:
            progress_info = self.mission_service.get_mission_progress(user_id, mission_id)
            if progress_info:
                mission_data['progress'] = progress_info['current']
                mission_data['max_progress'] = progress_info['target']

        message_text = format_mission_message(mission_data)
        keyboard = self._get_mission_details_keyboard(mission_id, user_mission_status)

        await callback_query.message.edit_text(
            message_text,
            reply_markup=keyboard
        )
        await callback_query.answer()

    async def accept_mission(self, callback_query: CallbackQuery):
        user_id = callback_query.from_user.id
        mission_id = callback_query.data.split("_")[2]
        username = callback_query.from_user.first_name

        success, message = self.mission_service.accept_mission(user_id, mission_id)

        if success:
            mission_data = self.mission_service.get_mission_data(mission_id)
            await callback_query.message.edit_text(
                get_mission_accepted_message(username, mission_data['title']),
                reply_markup=self._get_navigation_keyboard("missions_list") # Go back to list or active missions
            )
        else:
            await callback_query.message.edit_text(
                f"No. No puedes aceptar esa misión. {message}", # Use the message from service
                reply_markup=self._get_navigation_keyboard("missions_list")
            )
        await callback_query.answer()

    async def show_active_missions(self, callback_query: CallbackQuery):
        user_id = callback_query.from_user.id
        active_missions = self.mission_service.get_user_active_missions(user_id) # Assuming this method exists

        if not active_missions:
            await callback_query.message.edit_text(
                get_no_missions_message("activas"),
                reply_markup=self._get_navigation_keyboard("missions_list")
            )
            await callback_query.answer()
            return

        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        for mission_id, mission_data in active_missions.items():
            # Fetch progress for active missions
            progress_info = self.mission_service.get_mission_progress(user_id, mission_id)
            progress_text = ""
            if progress_info:
                progress_text = f" ({progress_info['current']}/{progress_info['target']})"
            
            keyboard.inline_keyboard.append([
                InlineKeyboardButton(
                    text=f"⏳ {mission_data['title']}{progress_text}",
                    callback_data=f"mission_details_{mission_id}"
                )
            ])
        
        keyboard.inline_keyboard.append(self._get_navigation_keyboard_row("missions_list"))

        await callback_query.message.edit_text(
            "Tus desafíos actuales. No los descuides.",
            reply_markup=keyboard
        )
        await callback_query.answer()


    def _get_missions_center_keyboard(self) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🌟 Ver Misiones Disponibles", callback_data="missions_list")],
            [InlineKeyboardButton(text="🏆 Mis Misiones Activas", callback_data="missions_active")],
            self._get_navigation_keyboard_row("main_menu")
        ])

    def _get_mission_details_keyboard(self, mission_id: str, status: MissionStatus) -> InlineKeyboardMarkup:
        buttons = []
        if status == MissionStatus.AVAILABLE:
            buttons.append(InlineKeyboardButton(text="✅ Aceptar Misión", callback_data=f"mission_accept_{mission_id}"))
        elif status == MissionStatus.ACCEPTED:
            buttons.append(InlineKeyboardButton(text="⏳ Ver Progreso", callback_data=f"mission_details_{mission_id}")) # Re-show details with updated progress

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            buttons,
            self._get_navigation_keyboard_row("missions_list")
        ])
        return keyboard

    def _get_navigation_keyboard(self, current_context: str) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=[
            self._get_navigation_keyboard_row(current_context)
        ])

    def _get_navigation_keyboard_row(self, current_context: str) -> list[InlineKeyboardButton]:
        if current_context == "missions_list":
            return [
                InlineKeyboardButton(text="↩️ Volver al Centro", callback_data="missions_center"), # New callback for center
                InlineKeyboardButton(text="🏠 Inicio", callback_data="main_menu")
            ]
        elif current_context == "main_menu":
            return [
                InlineKeyboardButton(text="↩️ Volver al Menú Principal", callback_data="main_menu")
            ]
        elif current_context == "missions_center":
            return [
                InlineKeyboardButton(text="↩️ Volver al Menú Principal", callback_data="main_menu")
            ]
        return [
            InlineKeyboardButton(text="↩️ Volver", callback_data="missions_list"),
            InlineKeyboardButton(text="🏠 Inicio", callback_data="main_menu")
        ]

# You would instantiate and register this in your main bot setup:
# from src.services.mission_service import MissionService
# mission_service = MissionService(...) # Initialize with dependencies
# mission_handler = MissionHandler(mission_service)
# await mission_handler.register_handlers()
# dp.include_router(router) # dp is your Dispatcher