# src/services/user_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.repository import UserRepository
from src.database.models import User
from src.core.event_bus import event_bus

class UserService:
    def __init__(self, session: AsyncSession):
        self.user_repo = UserRepository(session)

    async def get_or_create_user(self, telegram_id: int, username: str) -> tuple[User, bool]:
        user, created = await self.user_repo.get_or_create(telegram_id, username)
        if created:
            await event_bus.publish('user_created', user=user)
        return user, created