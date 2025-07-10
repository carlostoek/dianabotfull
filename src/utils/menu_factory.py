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
    Builds the main menu keyboard with a 4x2 grid layout and styled buttons.

    Returns:
        An InlineKeyboardMarkup object with the main navigation buttons.
    """
    builder = InlineKeyboardBuilder()
    buttons: List[List[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(text="🎯 Misiones", callback_data="missions"),
            InlineKeyboardButton(text="🎁 Regalo", callback_data="daily_gift")
        ],
        [
            InlineKeyboardButton(text="👤 Mi Perfil", callback_data="profile"),
            InlineKeyboardButton(text="🎒 Mochila", callback_data="backpack")
        ],
        [
            InlineKeyboardButton(text="🎮 Minijuegos", callback_data="minigames"),
            InlineKeyboardButton(text="💎 VIP Zone", callback_data="vip_zone")
        ],
        [
            InlineKeyboardButton(text="📺 Canales", callback_data="channels"),
            InlineKeyboardButton(text="⚙️ Admin", callback_data="admin")
        ]
    ]
    for row in buttons:
        builder.row(*row)
    return builder.as_markup()

def get_nav_menu() -> InlineKeyboardMarkup:
    """Creates an inline keyboard with secondary navigation buttons.

    Returns:
        An InlineKeyboardMarkup object with the navigation buttons.
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔄 Actualizar", callback_data="refresh"),
        InlineKeyboardButton(text="❌ Cerrar", callback_data="close")
    )
    builder.row(
        InlineKeyboardButton(text="↩️ Volver", callback_data="back"),
        InlineKeyboardButton(text="🏠 Inicio", callback_data="home")
    )
    return builder.as_markup()

def get_vip_menu(is_vip: bool) -> InlineKeyboardMarkup:
    """
    Builds the VIP menu keyboard, showing different options for VIPs and non-VIPs.

    Args:
        is_vip: A boolean indicating if the user has VIP status.

    Returns:
        An InlineKeyboardMarkup object with VIP-related buttons.
    """
    builder = InlineKeyboardBuilder()
    if is_vip:
        vip_buttons: List[List[InlineKeyboardButton]] = [
            [
                InlineKeyboardButton(text="🎁 Regalos VIP", callback_data="vip_gifts")
            ],
            [
                InlineKeyboardButton(text="📺 Canales VIP", callback_data="vip_channels"),
                InlineKeyboardButton(text="👥 Comunidad", callback_data="vip_community")
            ]
        ]
        for row in vip_buttons:
            builder.row(*row)
        builder.row(
            InlineKeyboardButton(text="💎 Mi Estado VIP", callback_data="vip_status"),
            InlineKeyboardButton(text="↩️ Volver", callback_data="main_menu")
        )
    else:
        builder.row(
            InlineKeyboardButton(text="💎 Hazte VIP", callback_data="become_vip"),
            InlineKeyboardButton(text="ℹ️ Beneficios VIP", callback_data="vip_benefits")
        )
        builder.row(
            InlineKeyboardButton(text="↩️ Volver", callback_data="main_menu")
        )
    return builder.as_markup()

def format_section_message(title: str, content: str, emoji: str = "🎯") -> str:
    """
    Formats a section message with a consistent style.
    
    Args:
        title: The title of the section.
        content: The main content of the message.
        emoji: The emoji to use for the section.
        
    Returns:
        A formatted string for the message.
    """
    separator = "─" * 30
    return f"""
{emoji} **{title.upper()}**

{separator}

{content}

{separator}
"""
