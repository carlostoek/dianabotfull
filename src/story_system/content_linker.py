import logging
from datetime import datetime, timedelta
from src.core.event_bus import EventBus
from src.services import content_service

logger = logging.getLogger(__name__)

# This map defines which decision triggers what content in which channel.
# Format: { "decision_id": ("content to post", channel_id) }
CONTENT_MAP = {
    "decision_X": ("Una consecuencia inesperada de tu elección se ha manifestado en el canal...", 12345),
    # Add other decision-to-content mappings here
}

class ContentLinker:
    """
    Links narrative events (like decisions) to content publications in channels.
    """
    def __init__(self, event_bus: EventBus):
        self._event_bus = event_bus
        # We need a 'decision_made' event to trigger content.
        self._event_bus.subscribe("decision_made", self.on_decision_made)

    async def trigger_content(self, decision_id: str):
        """
        Triggers a content publication based on a narrative decision.
        """
        if decision_id in CONTENT_MAP:
            content, channel_id = CONTENT_MAP[decision_id]
            logger.info(f"Triggering content for decision '{decision_id}' in channel {channel_id}.")
            # Schedule the post to appear almost immediately
            await content_service.schedule_post(
                content=content,
                schedule_time=datetime.now() + timedelta(seconds=5),
                channel_id=channel_id
            )
        else:
            logger.debug(f"No content mapped for decision '{decision_id}'.")

    async def lock_content(self, fragment_id: str):
        """
        Protects or archives content related to a narrative fragment.
        (Placeholder implementation)
        """
        # In a real system, this might archive posts, change permissions, etc.
        logger.info(f"Content related to fragment '{fragment_id}' is now locked/archived.")

    async def on_decision_made(self, user_id: int, decision_id: str, **kwargs):
        """
        Handles the 'decision_made' event.
        """
        logger.info(f"ContentLinker received decision_made event from user {user_id} for decision '{decision_id}'.")
        await self.trigger_content(decision_id)

def setup_content_linker(event_bus: EventBus):
    """Initializes and registers the ContentLinker."""
    ContentLinker(event_bus)
    logger.info("ContentLinker initialized and subscribed to events.")
