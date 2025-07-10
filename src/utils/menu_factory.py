# src/utils/menu_factory.py
"""
Factory for creating common UI menus and keyboards.

This module centralizes the creation of frequently used keyboards,
ensuring consistency and simplifying handler logic.
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

def get_nav_menu() -> InlineKeyboardMarkup:
    """Creates an inline keyboard with secondary navigation buttons.

    This keyboard provides common actions like refreshing, closing, going back,
    or returning to the home menu, suitable for use in various sub-menus.

    The layout is structured as follows:
    - Row 1: Actualizar, Cerrar
    - Row 2: Volver, Inicio

    Returns:
        An InlineKeyboardMarkup object with the navigation buttons.
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=" Actualizar", callback_data="refresh"),
        InlineKeyboardButton(text="❌ Cerrar", callback_data="close")
    )
    builder.row(
        InlineKeyboardButton(text="↩️ Volver", callback_data="back"),
        InlineKeyboardButton(text=" Inicio", callback_data="home")
    )
    return builder.as_markup()
