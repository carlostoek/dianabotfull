from aiogram.fsm.state import State, StatesGroup

class StoryStates(StatesGroup):
    viewing_scene = State()
    waiting_choice = State()
    story_paused = State()