import logging
from src.core.event_bus import EventBus
from src.core.config import Settings # Import Settings to access LEVEL_THRESHOLDS
from src.models.user import User # Assuming User model is needed for type hinting or direct manipulation

logger = logging.getLogger(__name__)

class LevelService:
    """
    Calculates user levels based on points and configured thresholds.
    Emits 'level_up' events.
    """
    def __init__(self, event_bus: EventBus, settings: Settings):
        self.event_bus = event_bus
        self.level_thresholds = sorted(settings.LEVEL_THRESHOLDS.items()) # Sort by points

    def get_level(self, points: int) -> str:
        """
        Determines the user's level based on their current points.
        """
        current_level = "Novato"
        for threshold_points, level_name in self.level_thresholds:
            if points >= threshold_points:
                current_level = level_name
            else:
                break # Points are less than the current threshold, so we have the level
        return current_level

    async def check_level_up(self, user_id: int, old_points: int, new_points: int):
        """
        Checks if a user has leveled up and publishes a 'level_up' event if so.
        """
        old_level = self.get_level(old_points)
        new_level = self.get_level(new_points)

        if new_level != old_level:
            logger.info(f"User {user_id} leveled up from {old_level} to {new_level} (Points: {new_points})")
            await self.event_bus.publish("level_up", user_id=user_id, old_level=old_level, new_level=new_level)
        else:
            logger.info(f"User {user_id} is still {new_level} (Points: {new_points})")