from typing import List, Optional
                InlineKeyboardButton(text="🎁 Regalos VIP", callback_data="vip_gifts")
            ],
            [
                InlineKeyboardButton(text="📺 Canales VIP", callback_data="vip_channels"),
                InlineKeyboardButton(text="👥 Comunidad", callback_data="vip_community")
            ]
        ]
        
        for row in vip_buttons:
            builder.row(*row)
            
        # Información del estado VIP
        builder.row(
            InlineKeyboardButton(text="💎 Mi Estado VIP", callback_data="vip_status"),
            InlineKeyboardButton(text="↩️ Volver", callback_data="main_menu")
        )
    else:
        # Menú para usuarios no VIP
        builder.row(
            InlineKeyboardButton(text="💎 Hazte VIP", callback_data="become_vip"),
            InlineKeyboardButton(text="ℹ️ Beneficios VIP", callback_data="vip_benefits")
        )
        builder.row(
            InlineKeyboardButton(text="↩️ Volver", callback_data="main_menu")
        )
    
    return builder.as_markup()

# Función helper para construir mensajes con formato consistente
def format_section_message(title: str, content: str, 
                          emoji: str = "🎯") -> str:
    """
    Formatea mensajes de sección con estilo consistente.
    
    Args:
        title (str): Título de la sección
        content (str): Contenido principal
        emoji (str): Emoji principal de la sección
        
    Returns:
        str: Mensaje formateado
    """
    separator = "─" * 30
    
    return f"""
{emoji} **{title.upper()}**

{separator}

{content}

{separator}
"""
