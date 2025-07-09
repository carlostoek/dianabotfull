from aiogram import Router, F
from aiogram.types import CallbackQuery
from src.story_system import story_engine
from src.telegram_bot.utils.keyboards import story_choices_keyboard, continue_story_keyboard

router = Router()

@router.callback_query(F.data == "start_story")
async def start_story(callback: CallbackQuery):
    scene = await story_engine.get_current_scene(callback.from_user.id)
    await callback.message.edit_text(
        scene["text"],
        reply_markup=story_choices_keyboard(scene["choices"])
    )

@router.callback_query(F.data.startswith("story_choice_"))
async def handle_story_choice(callback: CallbackQuery):
    choice_id = callback.data.split("_")[-1]
    result = await story_engine.process_choice(
        user_id=callback.from_user.id,
        choice_id=choice_id
    )
    
    await callback.message.edit_text(
        result["text"],
        reply_markup=continue_story_keyboard()
    )