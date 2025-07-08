import logging
# from src.core.event_bus import EventBus # Manteniendo la dependencia original por si se usa en otro lado
from src.models.user import User 
from src.core.integration_hub import IntegrationHub

logger = logging.getLogger(__name__)

class PointsService:
    """
    Manages the addition and deduction of points for users.
    """
    def __init__(self, event_bus=None, hub: IntegrationHub = None):
        self.event_bus = event_bus
        self.hub = hub
        self._user_points = {} 

    async def add_points(self, user: User, amount: int):
        if amount <= 0:
            logger.warning(f"Attempted to add non-positive points ({amount}) to user {user.id}.")
            return

        current_points = self._user_points.get(user.id, user.points)
        new_balance = current_points + amount
        self._user_points[user.id] = new_balance
        user.points = new_balance 

        logger.info(f"User {user.id} earned {amount} points. New balance: {new_balance}")
        if self.event_bus:
            await self.event_bus.publish("points_earned", user_id=user.id, amount=amount, new_balance=new_balance)

    async def deduct_points(self, user: User, amount: int):
        if amount <= 0:
            logger.warning(f"Attempted to deduct non-positive points ({amount}) from user {user.id}.")
            return

        current_points = self._user_points.get(user.id, user.points)
        if current_points < amount:
            logger.warning(f"User {user.id} has insufficient points ({current_points}) to deduct {amount}.")
            return

        new_balance = current_points - amount
        self._user_points[user.id] = new_balance
        user.points = new_balance

        logger.info(f"User {user.id} had {amount} points deducted. New balance: {new_balance}")

    # --- Nuevos métodos para IntegrationHub ---
    def add_points_for_reaction(self, data: dict):
        """
        Handler para el evento 'CHANNEL_REACTION'. Otorga puntos por una reacción.
        """
        user_id = data.get("user_id")
        reaction = data.get("reaction")
        points_to_add = 5  # 5 puntos por reacción
        
        logger.info(f"[HUB] PointsService: Añadiendo {points_to_add} puntos a user '{user_id}' por la reacción '{reaction}'.")
        # En un caso real, se actualizaría la base de datos.
        # Aquí simulamos la actualización y preparamos los datos para el siguiente evento.
        
        new_data = {
            "user_id": user_id,
            "points_awarded": points_to_add,
            "reason": "channel_reaction"
        }
        # Disparamos el siguiente evento en la cadena
        self.hub.route_event("POINTS_AWARDED", new_data)
