from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text=" Comenzar Historia", callback_data="start_story")
    builder.button(text=" Juegos", callback_data="show_games")
    builder.button(text=" Mi Perfil", callback_data="show_profile")
    builder.button(text=" VIP", callback_data="show_vip")
    builder.adjust(2)
    return builder.as_markup()

def story_choices_keyboard(choices):
    builder = InlineKeyboardBuilder()
    for choice in choices:
        builder.button(
            text=f"{choice['emoji']} {choice['text']}", 
            callback_data=f"story_choice_{choice['id']}"
        )
    return builder.as_markup()

def profile_menu_keyboard():
    builder = InlineKeyboardBuilder()
    # Add buttons for profile menu
    return builder.as_markup()

def continue_story_keyboard():
    builder = InlineKeyboardBuilder()
    # Add buttons for continuing story
    return builder.as_markup()

def story_continue_keyboard(fragment_id):
    builder = InlineKeyboardBuilder()
    # Add buttons for story continue
    return builder.as_markup()