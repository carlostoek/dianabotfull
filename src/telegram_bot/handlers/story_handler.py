from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from src.services.story_service import StoryService
from src.services.persona_service import PersonaService
from src.telegram_bot.states.story_states import StoryStates

router = Router()

class StoryHandler:
    def __init__(self, story_service: StoryService, persona_service: PersonaService):
        self.story_service = story_service
        self.persona_service = persona_service
    
    async def start_story_command(self, message: Message, state: FSMContext):
        """Maneja el comando para iniciar la historia"""
        user_id = message.from_user.id
        
        # Iniciar la historia
        scene = await self.story_service.start_story(user_id)
        
        # Guardar estado
        await state.set_state(StoryStates.viewing_scene)
        await state.update_data(current_scene_id=scene['scene_id'])
        
        # Enviar escena
        await self._send_scene(message, scene)
    
    async def _send_scene(self, message: Message, scene: Dict):
        """Envía una escena al usuario con sus opciones"""
        text = scene['text']
        
        # Crear teclado con las opciones
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        
        for choice in scene.get('choices', []):
            button = InlineKeyboardButton(
                text=choice['text'],
                callback_data=f"choice_{choice['id']}"
            )
            keyboard.inline_keyboard.append([button])
        
        # Añadir botón de pausa
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text="⏸ Pausar", callback_data="pause_story")
        ])
        
        await message.answer(text, reply_markup=keyboard)
        
    async def handle_choice(self, callback: CallbackQuery, state: FSMContext):
        """Maneja la elección del usuario"""
        user_id = callback.from_user.id
        choice_id = callback.data.replace("choice_", "")
        
        # Procesar elección
        result = await self.story_service.process_choice(user_id, choice_id)
        
        # Actualizar estado de Diana
        diana_update = await self.persona_service.update_diana_state(
            user_id, 
            result['impact']
        )
        
        # Enviar siguiente escena
        next_scene = result['next_scene']
        
        if next_scene:
            await callback.message.edit_text(
                f"✨ Diana ahora está {diana_update['new_state']}\n"
                f"🔮 Resonancia: {diana_update['resonance_score']:.1f}%"
            )
            await self._send_scene(callback.message, next_scene)
        else:
            # Fin del nivel
            await callback.message.edit_text(
                "🌙 Has completado el Nivel 1\n"
                f"Estado final de Diana: {diana_update['new_state']}\n"
                f"Resonancia alcanzada: {diana_update['resonance_score']:.1f}%"
            )
            await state.clear()
