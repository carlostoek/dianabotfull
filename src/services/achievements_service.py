import logging
from typing import List, Dict
# from src.core.event_bus import EventBus
from src.models.achievement import Achievement
from src.core.integration_hub import IntegrationHub

logger = logging.getLogger(__name__)

class AchievementsService:
    """
    Manages the unlocking and tracking of user achievements.
    """
    def __init__(self, event_bus=None, hub: IntegrationHub = None):
        self.event_bus = event_bus
        self.hub = hub
        self._available_achievements: List[Achievement] = [
            Achievement(id=1, name="first_login", description="First time logging in", icon="⭐"),
            Achievement(id=2, name="level_maestro", description="Reach Maestro level", icon="🏆"),
            Achievement(id=3, name="mission_master", description="Complete 10 missions", icon="✅"),
            Achievement(id=4, name="community_contributor", description="Reacted to a message", icon="❤️"),
        ]
        self._user_unlocked_achievements: Dict[int, List[int]] = {}

    async def unlock_achievement(self, user_id: int, achievement_name: str):
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
        if self.event_bus:
            await self.event_bus.publish("achievement_unlocked", user_id=user_id, achievement_id=achievement.id, achievement_name=achievement.name)

    def get_unlocked_for_user(self, user_id: int) -> List[Achievement]:
        unlocked_ids = self._user_unlocked_achievements.get(user_id, [])
        return [a for a in self._available_achievements if a.id in unlocked_ids]

    # --- Nuevos métodos para IntegrationHub ---
    def check_for_achievement(self, data: dict):
        """
        Handler para el evento 'POINTS_AWARDED'. Revisa si se debe desbloquear un logro.
        """
        user_id = data.get("user_id")
        reason = data.get("reason")
        
        logger.info(f"[HUB] AchievementsService: Revisando logros para user '{user_id}' por motivo '{reason}'.")
        
        # Lógica de ejemplo: si los puntos fueron por una reacción, se da un logro.
        if reason == "channel_reaction":
            achievement_to_unlock = "community_contributor"
            achievement = next((a for a in self._available_achievements if a.name == achievement_to_unlock), None)
            
            if achievement and achievement.id not in self._user_unlocked_achievements.get(user_id, []):
                # Desbloquear el logro (simulado)
                if user_id not in self._user_unlocked_achievements:
                    self._user_unlocked_achievements[user_id] = []
                self._user_unlocked_achievements[user_id].append(achievement.id)
                
                logger.info(f"[HUB] AchievementsService: ¡Logro '{achievement.name}' desbloqueado para user '{user_id}'!")
                
                new_data = {
                    "user_id": user_id,
                    "achievement_id": achievement.id,
                    "achievement_name": achievement.name,
                    "reward_type": "story_fragment" 
                }
                # Disparamos el siguiente evento
                self.hub.route_event("ACHIEVEMENT_UNLOCKED", new_data)
            else:
                logger.info(f"[HUB] AchievementsService: El usuario ya tiene el logro o no es elegible.")
