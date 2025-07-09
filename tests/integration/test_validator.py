import pytest
from tests.mocks.mock_services import MockDatabase, MockEventBus
from tests.integration.test_scenarios import ScenarioRunner

class IntegrationValidator:
    @staticmethod
    async def validate_flow(flow_name: str):
        """Valida flujos clave del sistema"""
        db = MockDatabase()
        bus = MockEventBus()
        runner = ScenarioRunner(db, bus)
        
        # Registrar handlers reales (aquí pondrías tus handlers reales)
        bus.subscribe("points_earned", lambda data: db.update_user(data["user_id"], points=data["amount"]))
        
        # NEW: Handler for reaction_added to simulate points earning
        async def reaction_to_points_handler(data):
            user_id = data["user_id"]
            # Simulate points logic: 5 points per reaction
            await bus.publish("points_earned", {"user_id": user_id, "amount": 5})

        bus.subscribe("reaction_added", reaction_to_points_handler)

        results = await runner.run(flow_name)
        return all(results.values())

# Ejemplo de prueba
@pytest.mark.asyncio
async def test_reaction_flow():
    assert await IntegrationValidator.validate_flow("reaction_to_points")