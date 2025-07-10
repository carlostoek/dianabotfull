from typing import Dict, Optional

# Assuming a repository exists to fetch user data.
# This import path is hypothetical and based on project structure.
from ..database.repository import UserProgressRepository

class ProfileService:
    """
    Service responsible for retrieving and formatting user profile data.
    """
    def __init__(self, user_progress_repo: UserProgressRepository):
        """
        Initializes the service with a repository for data access.

        Args:
            user_progress_repo: An instance of UserProgressRepository or a similar
                                data access object.
        """
        self.user_progress_repo = user_progress_repo

    async def get_user_profile(self, user_id: int, username: str) -> Optional[Dict]:
        """
        Retrieves and formats a user's profile for display.

        It fetches raw data from the repository and structures it into a
        dictionary suitable for the presentation layer (e.g., a menu handler).

        Args:
            user_id: The unique identifier of the user.
            username: The user's Telegram username.

        Returns:
            A dictionary containing the user's profile information or None if the
            user is not found.
        """
        user_progress = await self.user_progress_repo.get_by_user_id(user_id)

        if not user_progress:
            # Potentially create a new user profile here if that's the desired logic
            # For now, we'll just return None.
            return None

        # Map repository data to a structured profile dictionary.
        # getattr is used to safely access attributes that might not exist on the mock object.
        profile_data = {
            "username": username,
            "besitos": getattr(user_progress, 'besitos', 0),
            "level": getattr(user_progress, 'level', 1),
            "racha": getattr(user_progress, 'streak', 0),
            "diana_state": getattr(user_progress, 'diana_state', 'enigmática')
        }
        
        return profile_data
