import logging
from src.core.event_bus import EventBus
from src.services import user_service, subscription_service
from src.models.user import User

logger = logging.getLogger(__name__)

class AccessManager:
    """
    Manages user access to special content based on narrative progress.
    """
    VIP_ACCESS_FRAGMENT = "fragment_5"
    TEMPORARY_ACCESS_DAYS = 7

    def __init__(self, event_bus: EventBus):
        self._event_bus = event_bus
        self._event_bus.subscribe("fragment_unlocked", self.on_fragment_unlocked)

    def can_access_vip(self, user_id: int) -> bool:
        """
        Checks if the user has unlocked the required fragment for VIP access.
        """
        user = user_service.get_user(user_id)
        if not user:
            return False
        
        has_access = self.VIP_ACCESS_FRAGMENT in user.unlocked_fragments
        logger.info(f"User {user_id} VIP access check based on fragment '{self.VIP_ACCESS_FRAGMENT}': {'Granted' if has_access else 'Denied'}")
        return has_access

    async def grant_temporary_access(self, user_id: int):
        """
        Grants temporary VIP access to a user.
        """
        user = user_service.get_user(user_id)
        if user and not subscription_service.is_vip(user.id):
            logger.info(f"Granting {self.TEMPORARY_ACCESS_DAYS}-day temporary VIP access to user {user_id}.")
            await subscription_service.grant_vip(user, days=self.TEMPORARY_ACCESS_DAYS)
        elif not user:
            logger.warning(f"Cannot grant temporary access to non-existent user {user_id}.")
        else:
            logger.info(f"User {user_id} already has VIP access. No temporary access granted.")

    async def on_fragment_unlocked(self, user_id: int, fragment_id: str, **kwargs):
        """
        Handles the 'fragment_unlocked' event to grant access if rules are met.
        """
        logger.info(f"AccessManager received fragment_unlocked event for user {user_id}, fragment '{fragment_id}'.")
        if fragment_id == self.VIP_ACCESS_FRAGMENT:
            await self.grant_temporary_access(user_id)

def setup_access_manager(event_bus: EventBus):
    """Initializes and registers the AccessManager."""
    AccessManager(event_bus)
    logger.info("AccessManager initialized and subscribed to events.")
