from aiogram import Router
from aiogram.types import MessageReactionUpdated
from src.core.event_bus import event_bus

router = Router()

@router.message_reaction()
async def handle_reaction(reaction: MessageReactionUpdated):
    if reaction.chat.type == "channel":
        await event_bus.publish(
            "reaction_added",
            {
                "user_id": reaction.user.id,
                "channel_id": reaction.chat.id,
                "emoji": reaction.new_reaction[0].emoji
            }
        )