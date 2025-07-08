import logging
from src.services import user_service
from src.models.user import User

logger = logging.getLogger(__name__)

class UnlockSystem:
    """
    Manages the unlocking of narrative content and the costs of choices.
    """

    def check_unlock(self, user_id: int, fragment_id: str) -> bool:
        """
        Checks if a user has unlocked a specific narrative fragment.

        Args:
            user_id: The ID of the user.
            fragment_id: The ID of the fragment to check.

        Returns:
            True if the user has unlocked the fragment, False otherwise.
        """
        user = user_service.get_user(user_id)
        if not user:
            logger.warning(f"Attempted to check fragment {fragment_id} for non-existent user {user_id}")
            return False
        
        is_unlocked = fragment_id in user.unlocked_fragments
        logger.info(f"User {user_id} check for fragment '{fragment_id}': {'Unlocked' if is_unlocked else 'Locked'}")
        return is_unlocked

    def apply_cost(self, user_id: int, choice_cost: int = 1) -> bool:
        """
        Applies the cost of a premium choice to a user.

        Args:
            user_id: The ID of the user making the choice.
            choice_cost: The number of premium decisions to consume.

        Returns:
            True if the cost was successfully applied, False otherwise.
        """
        user = user_service.get_user(user_id)
        if not user:
            logger.warning(f"Attempted to apply cost for non-existent user {user_id}")
            return False

        if user.premium_decisions >= choice_cost:
            user.premium_decisions -= choice_cost
            user_service.save_user(user)
            logger.info(f"User {user_id} spent {choice_cost} premium decision(s). Remaining: {user.premium_decisions}")
            return True
        else:
            logger.warning(f"User {user_id} has insufficient premium decisions for cost {choice_cost}. Has: {user.premium_decisions}")
            return False

unlock_system = UnlockSystem()
