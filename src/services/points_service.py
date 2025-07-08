import logging
from src.core.event_bus import EventBus
from src.models.user import User # Assuming User model is needed for type hinting or direct manipulation

logger = logging.getLogger(__name__)

class PointsService:
    """
    Manages the addition and deduction of points for users.
    Emits 'points_earned' events.
    """
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        # In a real application, you would interact with a database here
        # to store and retrieve user points. For this example, we'll
        # simulate it with a simple in-memory dictionary.
        self._user_points = {} # user_id: points

    async def add_points(self, user: User, amount: int):
        """
        Adds points to a user's balance and publishes a points_earned event.
        """
        if amount <= 0:
            logger.warning(f"Attempted to add non-positive points ({amount}) to user {user.id}.")
            return

        # Simulate database interaction: get current points, update, save
        current_points = self._user_points.get(user.id, user.points) # Use user.points as initial if not in dict
        new_balance = current_points + amount
        self._user_points[user.id] = new_balance
        user.points = new_balance # Update the user object directly for consistency

        logger.info(f"User {user.id} earned {amount} points. New balance: {new_balance}")
        await self.event_bus.publish("points_earned", user_id=user.id, amount=amount, new_balance=new_balance)

    async def deduct_points(self, user: User, amount: int):
        """
        Deducts points from a user's balance.
        """
        if amount <= 0:
            logger.warning(f"Attempted to deduct non-positive points ({amount}) from user {user.id}.")
            return

        current_points = self._user_points.get(user.id, user.points)
        if current_points < amount:
            logger.warning(f"User {user.id} has insufficient points ({current_points}) to deduct {amount}.")
            return

        new_balance = current_points - amount
        self._user_points[user.id] = new_balance
        user.points = new_balance # Update the user object directly for consistency

        logger.info(f"User {user.id} had {amount} points deducted. New balance: {new_balance}")
        # Optionally, you could publish a 'points_deducted' event here if needed