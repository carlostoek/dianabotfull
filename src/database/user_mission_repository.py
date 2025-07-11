import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.user_mission_progress import UserMissionProgress

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class UserMissionRepository:
    """Repository for managing user mission progress in the database.

    This class provides methods to interact with the UserMissionProgress model,
    handling creation, retrieval, and updates of user mission data.
    """

    def __init__(self, session: AsyncSession):
        """Initializes the UserMissionRepository with an SQLAlchemy async session.

        Args:
            session (AsyncSession): The SQLAlchemy asynchronous session object.
        """
        self.session = session

    async def get_user_missions(self, user_id: int) -> List[UserMissionProgress]:
        """Retrieves all mission progress records for a given user.

        Args:
            user_id (int): The ID of the user.

        Returns:
            List[UserMissionProgress]: A list of UserMissionProgress objects for the user.
        """
        logging.info(f"Fetching all missions for user_id: {user_id}")
        result = await self.session.execute(
            select(UserMissionProgress).filter_by(user_id=user_id)
        )
        return result.scalars().all()

    async def get_mission_progress(self, user_id: int, mission_id: str) -> Optional[UserMissionProgress]:
        """Retrieves the progress of a specific mission for a given user.

        Args:
            user_id (int): The ID of the user.
            mission_id (str): The ID of the mission.

        Returns:
            Optional[UserMissionProgress]: The UserMissionProgress object if found, otherwise None.
        """
        logging.info(f"Fetching progress for user_id: {user_id}, mission_id: {mission_id}")
        result = await self.session.execute(
            select(UserMissionProgress).filter_by(user_id=user_id, mission_id=mission_id)
        )
        return result.scalars().first()

    async def start_mission(self, user_id: int, mission_id: str) -> UserMissionProgress:
        """Starts a new mission for a user or resumes an existing one.

        If the mission already exists for the user, its status is set to 'in_progress'.
        Otherwise, a new UserMissionProgress record is created.

        Args:
            user_id (int): The ID of the user.
            mission_id (str): The ID of the mission to start.

        Returns:
            UserMissionProgress: The UserMissionProgress object after starting/resuming.
        
        Raises:
            ValueError: If the mission_id does not correspond to a valid mission.
        """
        logging.info(f"Attempting to start mission {mission_id} for user {user_id}")
        # In a real application, you'd validate mission_id against a MissionService
        # For now, we'll assume mission_id is valid if it's not found in progress.
        
        mission_progress = await self.get_mission_progress(user_id, mission_id)
        if mission_progress:
            if mission_progress.status == "completed":
                logging.info(f"Mission {mission_id} for user {user_id} is already completed. Not restarting.")
                return mission_progress
            logging.info(f"Resuming mission {mission_id} for user {user_id}")
            mission_progress.status = "in_progress"
            mission_progress.started_at = datetime.now() # Update started_at if resuming
        else:
            logging.info(f"Creating new mission progress for user {user_id}, mission {mission_id}")
            mission_progress = UserMissionProgress(
                user_id=user_id,
                mission_id=mission_id,
                status="in_progress",
                progress=0.0,
                started_at=datetime.now()
            )
            self.session.add(mission_progress)
        await self.session.commit()
        await self.session.refresh(mission_progress)
        logging.info(f"Mission {mission_id} for user {user_id} started/resumed successfully.")
        return mission_progress

    async def update_progress(self, user_id: int, mission_id: str, progress: float) -> UserMissionProgress:
        """Updates the progress of a specific mission for a user.

        Args:
            user_id (int): The ID of the user.
            mission_id (str): The ID of the mission.
            progress (float): The new progress value (0.0 to 100.0).

        Returns:
            UserMissionProgress: The updated UserMissionProgress object.

        Raises:
            ValueError: If the mission is not found or progress is invalid.
        """
        logging.info(f"Updating progress for user {user_id}, mission {mission_id} to {progress}")
        if not 0.0 <= progress <= 100.0:
            raise ValueError("Progress must be between 0.0 and 100.0")

        mission_progress = await self.get_mission_progress(user_id, mission_id)
        if not mission_progress:
            raise ValueError(f"Mission {mission_id} not found for user {user_id}. Cannot update progress.")

        if mission_progress.status == "completed":
            logging.warning(f"Attempted to update progress for already completed mission {mission_id} for user {user_id}.")
            return mission_progress

        mission_progress.progress = progress
        await self.session.commit()
        await self.session.refresh(mission_progress)
        logging.info(f"Progress for user {user_id}, mission {mission_id} updated to {progress}.")
        return mission_progress

    async def complete_mission(self, user_id: int, mission_id: str) -> UserMissionProgress:
        """Marks a mission as completed for a user.

        Args:
            user_id (int): The ID of the user.
            mission_id (str): The ID of the mission to complete.

        Returns:
            UserMissionProgress: The updated UserMissionProgress object.

        Raises:
            ValueError: If the mission is not found.
        """
        logging.info(f"Attempting to complete mission {mission_id} for user {user_id}")
        mission_progress = await self.get_mission_progress(user_id, mission_id)
        if not mission_progress:
            raise ValueError(f"Mission {mission_id} not found for user {user_id}. Cannot complete.")

        if mission_progress.status == "completed":
            logging.info(f"Mission {mission_id} for user {user_id} is already completed.")
            return mission_progress

        mission_progress.status = "completed"
        mission_progress.progress = 100.0
        mission_progress.completed_at = datetime.now()
        await self.session.commit()
        await self.session.refresh(mission_progress)
        logging.info(f"Mission {mission_id} for user {user_id} marked as completed.")
        return mission_progress

    async def fail_mission(self, user_id: int, mission_id: str) -> UserMissionProgress:
        """Marks a mission as failed for a user.

        Args:
            user_id (int): The ID of the user.
            mission_id (str): The ID of the mission to fail.

        Returns:
            UserMissionProgress: The updated UserMissionProgress object.

        Raises:
            ValueError: If the mission is not found.
        """
        logging.info(f"Attempting to fail mission {mission_id} for user {user_id}")
        mission_progress = await self.get_mission_progress(user_id, mission_id)
        if not mission_progress:
            raise ValueError(f"Mission {mission_id} not found for user {user_id}. Cannot fail.")

        if mission_progress.status in ["completed", "failed"]:
            logging.info(f"Mission {mission_id} for user {user_id} is already {mission_progress.status}. Not marking as failed.")
            return mission_progress

        mission_progress.status = "failed"
        await self.session.commit()
        await self.session.refresh(mission_progress)
        logging.info(f"Mission {mission_id} for user {user_id} marked as failed.")
        return mission_progress
