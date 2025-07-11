import logging
from typing import Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.user_mission_repository import UserMissionRepository
from src.data.mission_catalog import MissionCatalog
from src.models.user_mission_progress import UserMissionProgress

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MissionService:
    """Service layer for managing user missions and their progress.

    This service acts as an intermediary between the bot/application logic
    and the data repositories (MissionCatalog and UserMissionRepository).
    It handles business logic related to mission availability, starting,
    updating progress, and status retrieval.
    """

    def __init__(self, session: AsyncSession, mission_catalog: MissionCatalog):
        """Initializes the MissionService.

        Args:
            session (AsyncSession): The SQLAlchemy asynchronous session for database operations.
            mission_catalog (MissionCatalog): The catalog providing mission definitions.
        """
        self.user_mission_repo = UserMissionRepository(session)
        self.mission_catalog = mission_catalog

    async def list_available_missions(self, user_id: int) -> List[Dict]:
        """Lists missions available to a user that are not yet completed.

        Args:
            user_id (int): The ID of the user.

        Returns:
            List[Dict]: A list of mission dictionaries, each including 'status'.
        """
        logging.info(f"Listing available missions for user {user_id}")
        all_missions = self.mission_catalog.get_all_missions()
        user_progress_records = await self.user_mission_repo.get_user_missions(user_id)
        
        completed_mission_ids = {m.mission_id for m in user_progress_records if m.status == "completed"}

        available_missions = []
        for mission in all_missions:
            if mission["id"] not in completed_mission_ids:
                mission_status = await self.get_mission_status(user_id, mission["id"])
                mission_with_status = mission.copy()
                mission_with_status["status"] = mission_status
                available_missions.append(mission_with_status)
        
        logging.info(f"Found {len(available_missions)} available missions for user {user_id}")
        return available_missions

    async def start_mission(self, user_id: int, mission_id: str) -> None:
        """Starts a mission for a user.

        Args:
            user_id (int): The ID of the user.
            mission_id (str): The ID of the mission to start.

        Raises:
            ValueError: If the mission_id is invalid or the mission is already in progress/completed.
        """
        logging.info(f"Attempting to start mission {mission_id} for user {user_id}")
        mission_definition = self.mission_catalog.get_mission_by_id(mission_id)
        if not mission_definition:
            raise ValueError(f"Mission with ID {mission_id} does not exist in the catalog.")

        current_progress = await self.user_mission_repo.get_mission_progress(user_id, mission_id)
        if current_progress:
            if current_progress.status == "in_progress":
                raise ValueError(f"Mission {mission_id} is already in progress for user {user_id}.")
            elif current_progress.status == "completed":
                raise ValueError(f"Mission {mission_id} is already completed for user {user_id}.")
            elif current_progress.status == "failed":
                # Allow restarting a failed mission
                logging.info(f"Mission {mission_id} for user {user_id} was failed, restarting.")
                await self.user_mission_repo.start_mission(user_id, mission_id)
                return

        started_mission = await self.user_mission_repo.start_mission(user_id, mission_id)
        logging.info(f"Mission {mission_id} successfully started for user {user_id}.")
        return started_mission

    async def update_mission_progress(self, user_id: int, mission_id: str, progress_delta: float) -> None:
        """Updates the progress of a mission for a user.

        Args:
            user_id (int): The ID of the user.
            mission_id (str): The ID of the mission.
            progress_delta (float): The amount to add to the current progress.

        Raises:
            ValueError: If the mission_id is invalid or the mission is not in progress.
        """
        logging.info(f"Updating progress for user {user_id}, mission {mission_id} by {progress_delta}")
        mission_definition = self.mission_catalog.get_mission_by_id(mission_id)
        if not mission_definition:
            raise ValueError(f"Mission with ID {mission_id} does not exist in the catalog.")

        current_progress_record = await self.user_mission_repo.get_mission_progress(user_id, mission_id)
        if not current_progress_record or current_progress_record.status != "in_progress":
            raise ValueError(f"Mission {mission_id} is not in progress for user {user_id}. Cannot update.")

        new_progress = min(100.0, current_progress_record.progress + progress_delta)
        
        updated_record = await self.user_mission_repo.update_progress(user_id, mission_id, new_progress)

        if new_progress >= 100.0:
            await self.user_mission_repo.complete_mission(user_id, mission_id)
            logging.info(f"Mission {mission_id} for user {user_id} automatically completed.")
        logging.info(f"Progress for user {user_id}, mission {mission_id} updated to {new_progress}.")
        return updated_record

    async def get_mission_status(self, user_id: int, mission_id: str) -> str:
        """Retrieves the current status of a mission for a user.

        Args:
            user_id (int): The ID of the user.
            mission_id (str): The ID of the mission.

        Returns:
            str: The status of the mission (pending, in_progress, completed, failed).
        """
        logging.info(f"Getting status for user {user_id}, mission {mission_id}")
        mission_definition = self.mission_catalog.get_mission_by_id(mission_id)
        if not mission_definition:
            # If mission doesn't exist in catalog, it's not a valid mission to track
            return "invalid"

        progress_record = await self.user_mission_repo.get_mission_progress(user_id, mission_id)
        if progress_record:
            return progress_record.status
        else:
            return "pending" # Mission exists in catalog but no progress record for user
