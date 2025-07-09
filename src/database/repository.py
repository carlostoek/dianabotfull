# src/database/repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from src.database.models import User, UserProgress

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, telegram_id: int, username: str) -> User:
        user = User(id=telegram_id, username=username)
        self.session.add(user)
        await self.session.flush() # Flush to get the user ID before creating UserProgress
        
        # Create associated UserProgress
        user_progress = UserProgress(user_id=telegram_id)
        self.session.add(user_progress)
        
        return user

    async def get_or_create(self, telegram_id: int, username: str) -> tuple[User, bool]:
        result = await self.session.execute(select(User).filter_by(id=telegram_id))
        user = result.scalar_one_or_none()

        if user:
            return user, False
        else:
            try:
                user = await self.create_user(telegram_id, username)
                await self.session.commit()
                return user, True
            except IntegrityError:
                await self.session.rollback()
                # This can happen in highly concurrent scenarios, try to fetch again
                result = await self.session.execute(select(User).filter_by(id=telegram_id))
                user = result.scalar_one_or_none()
                if user:
                    return user, False
                else:
                    raise # Re-raise if still can't find or create
