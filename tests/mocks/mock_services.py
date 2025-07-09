from datetime import datetime, timedelta
from unittest.mock import AsyncMock

class MockDatabase:
    def __init__(self):
        self.users = {
            1: {"id": 1, "username": "test_user", "points": 0, "role": "free", "unlocked_fragments": []}
        }
    
    async def get_user(self, user_id: int):
        return self.users.get(user_id)

    async def update_user(self, user_id: int, **data):
        if user_id in self.users:
            self.users[user_id].update(data)

    async def get_unlocked_fragments(self, user_id: int):
        user = await self.get_user(user_id)
        return user.get("unlocked_fragments", []) if user else []

class MockEventBus:
    def __init__(self):
        self.handlers = {}
        self.published_events = []
    
    def subscribe(self, event_type, handler):
        self.handlers.setdefault(event_type, []).append(handler)
    
    async def publish(self, event_type, data):
        self.published_events.append((event_type, data))
        for handler in self.handlers.get(event_type, []):
            await handler(data)

# Fixture lista para usar en pruebas
mock_user = {
    "id": 999,
    "username": "test_user_vip",
    "points": 100,
    "role": "vip",
    "vip_expires_at": datetime.now() + timedelta(days=30)
}