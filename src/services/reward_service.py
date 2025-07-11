import logging
from typing import Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.user_mission_repository import UserMissionRepository
from src.database.repository import UserProgressRepository, UserRepository # Assuming these are in repository.py
from src.data.mission_catalog import MissionCatalog
from src.models.user_mission_progress import UserMissionProgress
from src.database.models import UserProgress, User # Assuming User and UserProgress are in models.py

logger = logging.getLogger(__name__)

class RewardAlreadyClaimedError(Exception):
    """Exception raised when a reward for a mission has already been claimed."""
    pass

class MissionNotCompletedError(Exception):
    """Exception raised when attempting to claim a reward for an uncompleted mission."""
    pass

class MissionNotFoundError(Exception):
    """Exception raised when a mission is not found in the catalog."""
    pass

class RewardService:
    def __init__(self,
                 user_mission_repo: UserMissionRepository,
                 user_progress_repo: UserProgressRepository,
                 user_repo: UserRepository,
                 mission_catalog: MissionCatalog):
        self.user_mission_repo = user_mission_repo
        self.user_progress_repo = user_progress_repo
        self.user_repo = user_repo
        self.mission_catalog = mission_catalog

    async def apply_mission_reward(self, user_id: int, mission_id: str) -> Dict:
        """
        Applies the reward for a completed mission to the user's progress.

        Args:
            user_id (int): The ID of the user.
            mission_id (str): The ID of the mission.

        Returns:
            Dict: A summary of the rewards earned.

        Raises:
            MissionNotFoundError: If the mission does not exist in the catalog.
            MissionNotCompletedError: If the mission has not been completed by the user.
            RewardAlreadyClaimedError: If the reward for the mission has already been claimed.
        """
        # 1. Obtener la misión del catálogo para verificar su existencia y obtener la recompensa
        mission_data = self.mission_catalog.get_mission_by_id(mission_id)
        if not mission_data:
            raise MissionNotFoundError(f"Mission {mission_id} not found in catalog.")

        # 2. Verificar el estado de la misión del usuario
        user_mission: Optional[UserMissionProgress] = await self.user_mission_repo.get_mission_progress(user_id, mission_id)

        if not user_mission or user_mission.status != "completed":
            raise MissionNotCompletedError(f"Mission {mission_id} not completed by user {user_id}.")

        if user_mission.reward_claimed:
            raise RewardAlreadyClaimedError(f"Reward for mission {mission_id} already claimed by user {user_id}.")

        # 3. Obtener la recompensa asociada desde el catálogo.
        reward = mission_data.get("reward", {})
        besitos_earned = reward.get("besitos", 0)
        experience_earned = reward.get("experience", 0)

        # 4. Obtener el progreso del usuario y el usuario mismo
        user_progress: Optional[UserProgress] = await self.user_progress_repo.get_by_user_id(user_id)
        user: Optional[User] = await self.user_repo.get_user_by_id(user_id)

        if not user_progress:
            # This case should ideally not happen if user is created with progress
            logger.warning(f"UserProgress not found for user {user_id}. Initializing with default values.")
            user_progress = UserProgress(user_id=user_id, experience=0) # Assuming default values

        if not user:
            logger.error(f"User {user_id} not found. Cannot apply besitos reward.")
            # Depending on system design, might raise an error or proceed without besitos
            besitos_earned = 0 # Do not apply besitos if user not found

        # 5. Sumar los valores de besitos y experience al progreso del usuario.
        user_progress.experience += experience_earned
        if user: # Only update besitos if user object is valid
            user.points += besitos_earned

        # 6. Guardar los cambios mediante update_progress y update_user_points.
        await self.user_progress_repo.update_progress(user_id, experience=user_progress.experience)
        if user: # Only update user points if user object is valid
            await self.user_repo.update_user_points(user_id, user.points)

        # 7. Marcar la recompensa como reclamada en user_mission_progress
        user_mission.reward_claimed = True
        await self.user_mission_repo.update_user_mission_progress(user_mission)

        logger.info(f"User {user_id} claimed reward for mission {mission_id}: +{besitos_earned} besitos, +{experience_earned} experience.")

        # 8. Retornar un diccionario con el resumen de recompensa.
        # For now, level_up is always False, as level-up logic is not implemented yet.
        return {
            "besitos_earned": besitos_earned,
            "experience_earned": experience_earned,
            "level_up": False
        }