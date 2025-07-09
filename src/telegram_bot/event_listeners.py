from src.telegram_bot.core import TelegramBot
from src.telegram_bot.utils.keyboards import story_continue_keyboard

# This will be initialized in setup_telegram_event_listeners
bot = None

def setup_telegram_event_listeners(event_bus):
    global bot
    # Instantiate TelegramBot to access the bot instance
    telegram_bot_instance = TelegramBot(event_bus) # Pass event_bus here
    bot = telegram_bot_instance.bot

    @event_bus.subscribe("points_earned")
    async def send_points_notification(data):
        await bot.send_message(
            data["user_id"],
            f"✨ ¡Ganaste {data['amount']} besitos! "
        )
    
    @event_bus.subscribe("fragment_unlocked")
    async def send_fragment_notification(data):
        await bot.send_message(
            data["user_id"],
            f" ¡Nuevo fragmento desbloqueado!\n\n"
            f"{data['fragment_title']}",
            reply_markup=story_continue_keyboard(data["fragment_id"])
        )