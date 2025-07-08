import logging
from src.core.event_bus import EventBus, AsyncCallback
from src.services import user_service

logger = logging.getLogger(__name__)

class RewardGateway:
    """
    Listens for game events and translates them into narrative rewards.
    """
    POINTS_FOR_FRAGMENT = 1000

    def __init__(self, event_bus: EventBus):
        self._event_bus = event_bus
        self._event_bus.subscribe("points_earned", self.on_points_earned)
        self._event_bus.subscribe("mission_completed", self.on_mission_completed)

    async def on_points_earned(self, user_id: int, points_awarded: int, **kwargs):
        """
        Handles the 'points_earned' event.
        Awards a narrative fragment if enough points are earned.
        """
        logger.info(f"Received points_earned event for user {user_id} with {points_awarded} points.")
        if points_awarded >= self.POINTS_FOR_FRAGMENT:
            user = user_service.get_user(user_id)
            if user:
                # Logic to determine which fragment to award
                new_fragment_id = f"fragment_from_{user.points}_points"
                if new_fragment_id not in user.unlocked_fragments:
                    user.unlocked_fragments.append(new_fragment_id)
                    user_service.save_user(user)
                    logger.info(f"Awarded fragment '{new_fragment_id}' to user {user.id}.")
                    # Publish an event about the new fragment
                    await self._event_bus.publish("fragment_unlocked", user_id=user.id, fragment_id=new_fragment_id)

    async def on_mission_completed(self, user_id: int, mission_type: str, **kwargs):
        """
        Handles the 'mission_completed' event.
        Unlocks a premium decision if a daily mission is completed.
        """
        logger.info(f"Received mission_completed event for user {user_id} of type '{mission_type}'.")
        if mission_type == "daily":
            user = user_service.get_user(user_id)
            if user:
                user.premium_decisions += 1
                user_service.save_user(user)
                logger.info(f"Awarded 1 premium decision to user {user_id}. Total: {user.premium_decisions}")
                # Optionally, publish an event
                # await self._event_bus.publish("premium_decision_unlocked", user_id=user_id, count=user.premium_decisions)

def setup_reward_gateway(event_bus: EventBus):
    """
    Initializes and registers the RewardGateway.
    """
    RewardGateway(event_bus)
    logger.info("RewardGateway initialized and subscribed to events.")

