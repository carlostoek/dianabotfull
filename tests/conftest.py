import pytest
import pytest_asyncio
from unittest.mock import AsyncMock
from src.core.event_bus import EventBus # Assuming EventBus is in src.core.event_bus
from tests.mocks.mock_services import MockDatabase, MockEventBus

@pytest_asyncio.fixture
async def mock_db():
    return MockDatabase()

@pytest_asyncio.fixture
async def integration_hub(mock_db):
    # This mock will simulate the integration hub's event bus
    # You might need to adjust this based on the actual structure of your integration_hub
    class MockIntegrationHub:
        def __init__(self, db):
            self.event_bus = MockEventBus()
            self.db = db # Store db reference

            # Add reaction_to_points_handler to this event_bus
            async def reaction_to_points_handler(data):
                user_id = data["user_id"]
                # Simulate points logic: 5 points per reaction
                await self.event_bus.publish("points_earned", {"user_id": user_id, "amount": 5})

            self.event_bus.subscribe("reaction_added", reaction_to_points_handler)

            # Add points_earned handler to update the database
            self.event_bus.subscribe("points_earned", lambda data: self.db.update_user(data["user_id"], points=data["amount"]))

            # Add points_awarded handler to simulate fragment unlock
            async def points_awarded_handler(data):
                user_id = data["user_id"]
                amount = data["amount"]
                if amount >= 100: # Example condition for unlocking fragment
                    user = await self.db.get_user(user_id)
                    if user and "fragment_vip_1" not in user.get("unlocked_fragments", []):
                        user["unlocked_fragments"].append("fragment_vip_1")
                        await self.db.update_user(user_id, unlocked_fragments=user["unlocked_fragments"])

            self.event_bus.subscribe("POINTS_AWARDED", points_awarded_handler)

    return MockIntegrationHub(mock_db)