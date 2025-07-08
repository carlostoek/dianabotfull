import logging
from datetime import datetime, timedelta
from typing import Dict
from src.core.event_bus import EventBus
from src.models.user import User, UserRole # Assuming User and UserRole are defined

logger = logging.getLogger(__name__)

class SubscriptionService:
    """
    Manages VIP subscriptions for users.
    Emits 'vip_access_granted' events.
    """
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        # In-memory storage for VIP subscriptions: {user_id: expiration_datetime}
        self._vip_subscriptions: Dict[int, datetime] = {}

    async def grant_vip(self, user: User, days: int):
        """
        Grants VIP access to a user for a specified number of days.
        """
        if days <= 0:
            logger.warning(f"Attempted to grant VIP for non-positive days ({days}) to user {user.id}.")
            return

        expiration_date = datetime.now() + timedelta(days=days)
        self._vip_subscriptions[user.id] = expiration_date
        user.role = UserRole.VIP # Update user role directly for consistency

        logger.info(f"VIP access granted to user {user.id} until {expiration_date}.")
        await self.event_bus.publish("vip_access_granted", user_id=user.id, expiration_date=expiration_date)

    async def revoke_vip(self, user: User):
        """
        Revokes VIP access from a user.
        """
        if user.id in self._vip_subscriptions:
            del self._vip_subscriptions[user.id]
            user.role = UserRole.FREE # Update user role directly for consistency
            logger.info(f"VIP access revoked for user {user.id}.")
        else:
            logger.info(f"User {user.id} does not have active VIP subscription.")

    def is_vip(self, user_id: int) -> bool:
        """
        Checks if a user has active VIP access.
        """
        expiration_date = self._vip_subscriptions.get(user_id)
        return expiration_date is not None and expiration_date > datetime.now()
