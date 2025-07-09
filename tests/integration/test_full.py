# tests/integration/test_full_flow.py
import pytest
from src.database.models import User
from tests.mocks.mock_services import MockDatabase

@pytest.mark.asyncio
async def test_reaction_flow():
    db = MockDatabase()
    test_user = {
        "id": 1,
        "username": "test_user",
        "points": 0,
        "role": "free"
    }
    await db.update_user(1, **test_user)
    
    user = await db.get_user(1)
    assert user["points"] == 0
    assert user["role"] == "free"
