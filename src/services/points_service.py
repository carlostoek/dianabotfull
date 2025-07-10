# src/services/points_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.repository import UserRepository, PointTransactionRepository
from src.database.models import Mission
from src.core.event_bus import event_bus

class PointsService:
    def __init__(self, session: AsyncSession):
        self.user_repo = UserRepository(session)
        self.transaction_repo = PointTransactionRepository(session)
        self.session = session

    async def award_points_for_mission(self, user_id: int, mission: Mission):
        user = await self.user_repo.get_user_by_id(user_id)
        if user:
            user.points += mission.reward_points
            await self.transaction_repo.create_transaction(
                user_id=user_id,
                points=mission.reward_points,
                reason=f"Completed mission: {mission.name}"
            )
            await self.session.commit()

    async def get_points(self, user_id: int) -> int:
        """
        Get the current point balance for a user.
        """
        user = await self.user_repo.get_user_by_id(user_id)
        return user.points if user else 0

def setup_points_listeners():
    event_bus.subscribe('mission_completed', on_mission_completed)

async def on_mission_completed(user_id: int, mission: Mission, session: AsyncSession, **kwargs):
    points_service = PointsService(session)
    await points_service.award_points_for_mission(user_id, mission)
