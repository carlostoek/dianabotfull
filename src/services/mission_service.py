# src/services/mission_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.repository import MissionRepository, UserMissionRepository
from src.core.event_bus import event_bus

class MissionService:
    def __init__(self, session: AsyncSession):
        self.mission_repo = MissionRepository(session)
        self.user_mission_repo = UserMissionRepository(session)
        self.session = session

    async def check_daily_login(self, user_id: int) -> bool:
        mission = await self.mission_repo.get_mission_by_name('Daily Login')
        if not mission:
            # Maybe log that the mission doesn't exist
            return False

        has_completed = await self.user_mission_repo.has_completed_mission_today(user_id, mission.id)
        if not has_completed:
            await self.user_mission_repo.complete_mission(user_id, mission.id)
            await event_bus.publish('mission_completed', user_id=user_id, mission=mission, session=self.session)
            return True
        return False
