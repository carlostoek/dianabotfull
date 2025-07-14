# src/telegram_bot/handlers/__init__.py
"""Exposes all routers for easy registration."""
from . import (
    admin_handlers,
    game_handlers,
    main_menu_handlers,
    mission_handler,
    profile_handler,
    seed_handlers,
    start,
    story_handlers,
    unrecognized_handlers,
    user_handlers,
)

# List of all routers to be registered in the dispatcher
all_routers = [
    start.router,
    main_menu_handlers.router,
    user_handlers.router,
    admin_handlers.router,
    story_handlers.router,
    game_handlers.router,
    seed_handlers.router,
    profile_handler.profile_router,
    mission_handler.router,
    unrecognized_handlers.router,
]
