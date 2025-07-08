import logging
from datetime import datetime
from typing import Dict, Any
# from src.core.event_bus import EventBus
from src.core.integration_hub import IntegrationHub

logger = logging.getLogger(__name__)

class ContentService:
    """
    Manages content publications and engagement.
    """
    def __init__(self, event_bus=None, hub: IntegrationHub = None):
        self.event_bus = event_bus
        self.hub = hub
        self._scheduled_posts: Dict[int, Dict[str, Any]] = {}
        self._next_post_id = 1

    async def schedule_post(self, content: str, schedule_time: datetime, channel_id: int):
        post_id = self._next_post_id
        self._next_post_id += 1
        self._scheduled_posts[post_id] = {
            "content": content,
            "schedule_time": schedule_time,
            "channel_id": channel_id
        }
        logger.info(f"Post {post_id} scheduled for channel {channel_id} at {schedule_time}.")

    async def track_engagement(self, post_id: int, user_id: int, engagement_type: str, value: Any = None):
        if post_id not in self._scheduled_posts:
            logger.warning(f"Post {post_id} not found. Cannot track engagement.")
            return

        logger.info(f"Engagement tracked for post {post_id} by user {user_id}: {engagement_type} (Value: {value})")
        if self.event_bus and engagement_type == "reaction_added":
            await self.event_bus.publish("reaction_added", post_id=post_id, user_id=user_id, reaction=value)

    # --- Nuevos métodos para IntegrationHub ---
    def deliver_exclusive_content(self, data: dict):
        """
        Handler para 'VIP_STATUS_GRANTED'. Entrega contenido exclusivo a un nuevo VIP.
        """
        user_id = data.get("user_id")
        
        logger.info(f"[HUB] ContentService: Entregando contenido exclusivo a user '{user_id}'.")
        
        exclusive_content = "Aquí tienes un enlace a un capítulo secreto de la historia: /story/secret_chapter_1"
        
        # En una aplicación real, esto podría ser un mensaje directo, un post en un canal privado, etc.
        logger.info(f"[HUB] ContentService: Mensaje para user '{user_id}': '{exclusive_content}'")
        
        # Este es el final del segundo flujo.