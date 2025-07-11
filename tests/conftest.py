import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

# Import actual classes to mock them
from src.services.mission_catalog_service import MissionCatalogService
from src.services.mission_service import MissionService
from src.database.user_mission_repository import UserMissionRepository
from src.services.reward_service import RewardService
from src.models.user_mission_progress import UserMissionProgress
from src.models.user import User # Assuming a User model exists for mock_user
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.fixture
async def mock_async_session():
    """
    Fixture for a mock SQLAlchemy AsyncSession.
    """
    session = AsyncMock(spec=AsyncSession)
    session.commit.return_value = None
    session.refresh.return_value = None
    session.add.return_value = None
    return session

@pytest.fixture
def mock_user():
    """
    Fixture for a mock user with ID 42 and initial besitos.
    """
    user = MagicMock(spec=User)
    user.id = 42
    user.besitos = 0
    return user

@pytest.fixture
def mock_catalog():
    """
    Fixture for a mock MissionCatalog loaded from missions.json.
    """
    with open("/data/data/com.termux/files/home/repos/dianabotfull/data/missions.json", "r") as f:
        missions_data = json.load(f)
    
    # Simulate MissionCatalogService's internal structure if needed,
    # but for integration tests, we'll just return the raw data
    # or a simplified object that behaves like the catalog.
    # For now, a simple list of dicts is sufficient.
    return missions_data

@pytest.fixture
def mock_repo():
    """
    Fixture for a mock UserMissionRepository with in-memory storage.
    """
    repo = AsyncMock(spec=UserMissionRepository)
    
    # In-memory storage for user mission progress
    _in_memory_db = {} # {user_id: {mission_id: UserMissionProgress}}

    async def _get_user_missions(user_id: int):
        return list(_in_memory_db.get(user_id, {}).values())

    async def _get_mission_progress(user_id: int, mission_id: str):
        return _in_memory_db.get(user_id, {}).get(mission_id)

    async def _start_mission(user_id: int, mission_id: str):
        if user_id not in _in_memory_db:
            _in_memory_db[user_id] = {}
        
        progress = _in_memory_db[user_id].get(mission_id)
        if progress:
            if progress.status == "completed":
                return progress # Already completed, don't restart
            progress.status = "in_progress"
            progress.started_at = datetime.now()
        else:
            progress = UserMissionProgress(
                user_id=user_id,
                mission_id=mission_id,
                status="in_progress",
                progress=0.0,
                started_at=datetime.now()
            )
        _in_memory_db[user_id][mission_id] = progress
        return progress

    async def _update_progress(user_id: int, mission_id: str, progress_value: float):
        progress = _in_memory_db.get(user_id, {}).get(mission_id)
        if not progress:
            raise ValueError(f"Mission {mission_id} not found for user {user_id}.")
        if progress.status == "completed":
            return progress # Cannot update completed mission
        progress.progress = progress_value
        return progress

    async def _complete_mission(user_id: int, mission_id: str):
        progress = _in_memory_db.get(user_id, {}).get(mission_id)
        if not progress:
            raise ValueError(f"Mission {mission_id} not found for user {user_id}.")
        if progress.status == "completed":
            return progress
        progress.status = "completed"
        progress.progress = 100.0
        progress.completed_at = datetime.now()
        return progress

    repo.get_user_missions.side_effect = _get_user_missions
    repo.get_mission_progress.side_effect = _get_mission_progress
    repo.start_mission.side_effect = _start_mission
    repo.update_progress.side_effect = _update_progress
    repo.complete_mission.side_effect = _complete_mission
    
    # Clear the in-memory db after each test
    _in_memory_db.clear()
    return repo

@pytest.fixture
def mock_reward_service():
    """
    Fixture for a mock RewardService.
    """
    service = AsyncMock(spec=RewardService)
    async def mock_apply_mission_reward(user_id, mission_id):
        # Simulate the reward application based on mission_id
        # For simplicity, we'll hardcode rewards based on the missions.json
        rewards = {
            "m001": {"besitos_earned": 100, "experience_earned": 0, "level_up": False},
            "m002": {"besitos_earned": 250, "experience_earned": 0, "level_up": False},
            "m003": {"besitos_earned": 50, "experience_earned": 0, "level_up": False},
            "m004": {"besitos_earned": 500, "experience_earned": 0, "level_up": False},
            "m005": {"besitos_earned": 150, "experience_earned": 0, "level_up": False},
        }
        return rewards.get(mission_id, {"besitos_earned": 0, "experience_earned": 0, "level_up": False})

    service.apply_mission_reward.side_effect = mock_apply_mission_reward
    return service

@pytest.fixture
def mission_catalog_service(mock_catalog):
    """
    Fixture for MissionCatalogService using the mock catalog.
    """
    service = MissionCatalogService()
    # Override the internal catalog with our mock data
    service._missions = mock_catalog
    return service

@pytest.fixture
def mission_service(mock_async_session, mission_catalog_service, mock_repo, mocker):
    """
    Fixture for MissionService with mocked dependencies.
    """
    # Patch the UserMissionRepository within the mission_service module
    mocker.patch('src.services.mission_service.UserMissionRepository', return_value=mock_repo)
    
    return MissionService(
        session=mock_async_session,
        mission_catalog=mission_catalog_service
    )
