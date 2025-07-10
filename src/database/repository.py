from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from src.database.models import User, UserProgress, Mission, Achievement, UserAchievement, UserMission, PointTransaction
from datetime import datetime, date

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
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        result = await self.session.execute(select(User).filter_by(id=user_id))
        return result.scalar_one_or_none()

class MissionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_missions(self) -> List[Mission]:
        result = await self.session.execute(select(Mission))
        return result.scalars().all()

    async def get_mission_by_id(self, mission_id: int) -> Optional[Mission]:
        result = await self.session.execute(select(Mission).filter_by(id=mission_id))
        return result.scalar_one_or_none()

    async def get_mission_by_name(self, name: str) -> Optional[Mission]:
        result = await self.session.execute(select(Mission).filter_by(name=name))
        return result.scalar_one_or_none()

class UserMissionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def has_completed_mission_today(self, user_id: int, mission_id: int) -> bool:
        today = date.today()
        result = await self.session.execute(
            select(UserMission).filter_by(user_id=user_id, mission_id=mission_id)
            .filter(UserMission.completed_at >= today)
        )
        return result.scalar_one_or_none() is not None

    async def complete_mission(self, user_id: int, mission_id: int) -> UserMission:
        user_mission = UserMission(user_id=user_id, mission_id=mission_id, completed_at=datetime.utcnow())
        self.session.add(user_mission)
        await self.session.commit()
        return user_mission

class AchievementRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_achievements(self, user_id: int) -> List[Achievement]:
        result = await self.session.execute(
            select(Achievement)
            .join(UserAchievement)
            .filter(UserAchievement.user_id == user_id)
        )
        return result.scalars().all()

class PointTransactionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_transaction(self, user_id: int, points: int, reason: str) -> PointTransaction:
        transaction = PointTransaction(user_id=user_id, points=points, reason=reason)
        self.session.add(transaction)
        await self.session.commit()
        return transaction

class UserProgressRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user_id(self, user_id: int) -> Optional[UserProgress]:
        result = await self.session.execute(select(UserProgress).filter_by(user_id=user_id))
        return result.scalar_one_or_none()

    async def update_progress(self, user_id: int, **kwargs) -> UserProgress:
        user_progress = await self.get_by_user_id(user_id)
        if not user_progress:
            raise ValueError(f"UserProgress for user_id {user_id} not found.")

        for key, value in kwargs.items():
            setattr(user_progress, key, value)
        
        await self.session.commit()
        await self.session.refresh(user_progress)
        return user_progress