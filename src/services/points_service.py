# src/services/points_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.repository import UserRepository, PointTransactionRepository
from src.database.models import Mission, User
from src.core.event_bus import event_bus

class PointsService:
    def __init__(self, user_repo: UserRepository, transaction_repo: PointTransactionRepository):
        self.user_repo = user_repo
        self.transaction_repo = transaction_repo

    async def add_points(self, user_id: int, amount: int, reason: str = "Generic") -> None:
        """
        Add or remove points for a user and create a transaction record.
        """
        user = await self.user_repo.get_user_by_id(user_id)
        if user:
            user.points += amount
            await self.transaction_repo.create_transaction(
                user_id=user_id,
                points=amount,
                reason=reason
            )
            # The session commit should be handled by the middleware

    async def get_points(self, user_id: int) -> int:
        """
        Get the current point balance for a user.
        """
        user = await self.user_repo.get_user_by_id(user_id)
        return user.points if user else 0

    async def award_points_for_mission(self, user_id: int, mission: Mission):
        """
        Award points for completing a mission.
        """
        await self.add_points(user_id, mission.reward_points, f"Completed mission: {mission.name}")

def setup_points_listeners():
    event_bus.subscribe('mission_completed', on_mission_completed)

async def on_mission_completed(user_id: int, mission: Mission, session: AsyncSession, **kwargs):
    # This part might need adjustment depending on how services are instantiated globally
    user_repo = UserRepository(session)
    transaction_repo = PointTransactionRepository(session)
    points_service = PointsService(user_repo, transaction_repo)
    await points_service.award_points_for_mission(user_id, mission)
