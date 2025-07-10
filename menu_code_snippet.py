"""
This file contains the code snippet for the main menu generator function.
"""
from typing import List
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_main_menu() -> InlineKeyboardMarkup:
    """
    Builds the main menu keyboard with a 4x2 grid layout.

    The layout is structured as follows:
    - Row 1: Misiones, Regalo
    - Row 2: Mi Perfil, Mochila
    - Row 3: Minijuegos, VIP Zone
    - Row 4: Canales, Admin

    Returns:
        An InlineKeyboardMarkup object with the main navigation buttons.
    """
    builder = InlineKeyboardBuilder()
    
    # Manually define the structure for clarity
    buttons: List[List[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(text=" Misiones", callback_data="missions"),
            InlineKeyboardButton(text=" Regalo", callback_data="daily_gift")
        ],
        [
            InlineKeyboardButton(text=" Mi Perfil", callback_data="profile"),
            InlineKeyboardButton(text="️ Mochila", callback_data="backpack")
        ],
        [
            InlineKeyboardButton(text="️ Minijuegos", callback_data="minigames"),
            InlineKeyboardButton(text=" VIP Zone", callback_data="vip_zone")
        ],
        [
            InlineKeyboardButton(text=" Canales", callback_data="channels"),
            InlineKeyboardButton(text="⚙️ Admin", callback_data="admin")
        ]
    ]
    
    for row in buttons:
        builder.row(*row)
        
    return builder.as_markup()
