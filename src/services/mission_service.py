import logging
from typing import List, Dict
from datetime import datetime, timedelta
from src.core.event_bus import EventBus
from src.models.mission import Mission

logger = logging.getLogger(__name__)

class MissionService:
    """
    Manages daily missions for users.
    Emits 'mission_completed' events.
    """
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        # In a real application, missions would be loaded from a database.
        # For this example, we'll use a static list of missions.
        self._available_missions: List[Mission] = [
            Mission(id=1, name="daily_login", description="Log in daily", reward_points=10),
            Mission(id=2, name="send_message", description="Send 5 messages", reward_points=20),
            Mission(id=3, name="complete_task", description="Complete a specific task", reward_points=50),
        ]
        # Simulate user mission progress/completion (user_id: {mission_id: completed_date})
        self._user_mission_status: Dict[int, Dict[int, datetime]] = {}

    def get_daily_missions(self, user_id: int) -> List[Mission]:
        """
        Returns a list of daily missions for a given user.
        In a real scenario, this would involve more complex logic for daily resets.
        """
        # For simplicity, all available missions are considered "daily" for now.
        # A more robust system would generate or select missions based on the day.
        return self._available_missions

    async def complete_mission(self, user_id: int, mission_name: str):
        """
        Marks a mission as completed for a user and publishes an event.
        """
        mission = next((m for m in self._available_missions if m.name == mission_name), None)
        if not mission:
            logger.warning(f"Mission '{mission_name}' not found.")
            return

        user_missions = self._user_mission_status.setdefault(user_id, {})
        # Check if mission was completed today (simple daily reset logic)
        if mission.id in user_missions and (datetime.now() - user_missions[mission.id]).days == 0:
            logger.info(f"User {user_id} already completed mission '{mission_name}' today.")
            return

        user_missions[mission.id] = datetime.now()
        logger.info(f"User {user_id} completed mission '{mission_name}'. Awarding {mission.reward_points} points.")
        await self.event_bus.publish("mission_completed", user_id=user_id, mission_id=mission.id, reward_points=mission.reward_points)