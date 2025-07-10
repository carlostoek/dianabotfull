# src/services/user_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.repository import UserRepository
from src.database.models import User
from src.core.event_bus import event_bus

class UserService:
    def __init__(self, session: AsyncSession):
        self.user_repo = UserRepository(session)

    async def create_user_if_not_exists(self, user_id: int, username: str) -> None:
        """
        Creates a user if they do not already exist in the database.
        Publishes a 'user_created' event if a new user is created.

        Args:
            user_id: The Telegram user ID.
            username: The user's Telegram username.
        """
        user, created = await self.user_repo.get_or_create(user_id, username)
        if created:
            await event_bus.publish('user_created', user=user)

    async def get_user(self, user_id: int) -> User | None:
        """
        Retrieves a user by their ID.

        Args:
            user_id: The Telegram user ID.

        Returns:
            The User object or None if not found.
        """
        return await self.user_repo.get_user_by_id(user_id)
