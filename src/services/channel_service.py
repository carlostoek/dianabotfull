import logging
from typing import Dict, List, Any
from src.core.event_bus import EventBus

logger = logging.getLogger(__name__)

class ChannelService:
    """
    Manages channel registration and settings.
    """
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        # In-memory storage for channels: {chat_id: {is_vip: bool, reactions: List[str]}}
        self._channels: Dict[int, Dict[str, Any]] = {}

    async def add_channel(self, chat_id: int, is_vip: bool = False):
        """
        Adds a new channel to the system.
        """
        if chat_id in self._channels:
            logger.warning(f"Channel {chat_id} already exists.")
            return

        self._channels[chat_id] = {"is_vip": is_vip, "reactions": []}
        logger.info(f"Channel {chat_id} added. VIP status: {is_vip}")

    async def set_reactions(self, chat_id: int, reactions: List[str]):
        """
        Sets allowed reactions for a specific channel.
        """
        if chat_id not in self._channels:
            logger.warning(f"Channel {chat_id} not found. Cannot set reactions.")
            return

        self._channels[chat_id]["reactions"] = reactions
        logger.info(f"Reactions {reactions} set for channel {chat_id}.")
        # As per prompt, 'reaction_added' event is for actual reactions, not setting them.
        # This service configures, a lower-level integration would emit the event.
