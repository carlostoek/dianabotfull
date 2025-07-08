import logging
from typing import List, Dict
from src.core.event_bus import EventBus
from src.models.achievement import Achievement

logger = logging.getLogger(__name__)

class AchievementsService:
    """
    Manages the unlocking and tracking of user achievements.
    Emits 'achievement_unlocked' events.
    """
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        # In a real application, achievements would be loaded from a database.
        # For this example, we'll use a static list of achievements.
        self._available_achievements: List[Achievement] = [
            Achievement(id=1, name="first_login", description="First time logging in", icon="⭐"),
            Achievement(id=2, name="level_maestro", description="Reach Maestro level", icon="🏆"),
            Achievement(id=3, name="mission_master", description="Complete 10 missions", icon="✅"),
        ]
        # Simulate unlocked achievements for users (user_id: [achievement_id, ...])
        self._user_unlocked_achievements: Dict[int, List[int]] = {}

    async def unlock_achievement(self, user_id: int, achievement_name: str):
        """
        Unlocks an achievement for a user if not already unlocked and publishes an event.
        """
        achievement = next((a for a in self._available_achievements if a.name == achievement_name), None)
        if not achievement:
            logger.warning(f"Achievement '{achievement_name}' not found.")
            return

        if user_id not in self._user_unlocked_achievements:
            self._user_unlocked_achievements[user_id] = []

        if achievement.id in self._user_unlocked_achievements[user_id]:
            logger.info(f"User {user_id} already unlocked achievement '{achievement.name}'.")
            return

        self._user_unlocked_achievements[user_id].append(achievement.id)
        logger.info(f"User {user_id} unlocked achievement: {achievement.name}")
        await self.event_bus.publish("achievement_unlocked", user_id=user_id, achievement_id=achievement.id, achievement_name=achievement.name)

    def get_unlocked_for_user(self, user_id: int) -> List[Achievement]:
        """
        Returns a list of achievements unlocked by a specific user.
        """
        unlocked_ids = self._user_unlocked_achievements.get(user_id, [])
        return [a for a in self._available_achievements if a.id in unlocked_ids]