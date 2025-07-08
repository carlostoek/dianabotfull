import logging
from datetime import datetime
from typing import Dict, Any
from src.core.event_bus import EventBus

logger = logging.getLogger(__name__)

class ContentService:
    """
    Manages scheduled content publications and tracks engagement.
    """
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        # In-memory storage for scheduled posts: {post_id: {content: str, schedule_time: datetime, channel_id: int}}
        self._scheduled_posts: Dict[int, Dict[str, Any]] = {}
        self._next_post_id = 1

    async def schedule_post(self, content: str, schedule_time: datetime, channel_id: int):
        """
        Schedules a post to be published at a specific time in a given channel.
        """
        post_id = self._next_post_id
        self._next_post_id += 1
        self._scheduled_posts[post_id] = {
            "content": content,
            "schedule_time": schedule_time,
            "channel_id": channel_id
        }
        logger.info(f"Post {post_id} scheduled for channel {channel_id} at {schedule_time}.")
        # In a real system, a background task would pick up and publish these posts.

    async def track_engagement(self, post_id: int, user_id: int, engagement_type: str, value: Any = None):
        """
        Tracks user engagement with a specific post (e.g., reactions, views).
        """
        if post_id not in self._scheduled_posts:
            logger.warning(f"Post {post_id} not found. Cannot track engagement.")
            return

        # This is a simplified tracking. In a real system, this would update
        # a database or a dedicated analytics service.
        logger.info(f"Engagement tracked for post {post_id} by user {user_id}: {engagement_type} (Value: {value})")
        # Example: if engagement_type is 'reaction_added', you might publish an event
        if engagement_type == "reaction_added":
            await self.event_bus.publish("reaction_added", post_id=post_id, user_id=user_id, reaction=value)
