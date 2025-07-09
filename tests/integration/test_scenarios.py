import asyncio
import json
from pathlib import Path
from tests.mocks.mock_services import MockDatabase, MockEventBus

class ScenarioRunner:
    def __init__(self, db: MockDatabase, event_bus: MockEventBus):
        self.db = db
        self.event_bus = event_bus
        self.scenarios = self._load_scenarios()
    
    def _load_scenarios(self):
        scenarios_path = Path(__file__).parent / "data" / "scenarios.json"
        with open(scenarios_path) as f:
            return json.load(f)
    
    async def run(self, scenario_name: str):
        """Ejecuta un escenario paso a paso"""
        scenario = self.scenarios[scenario_name]
        
        # 1. Setup inicial
        if "setup" in scenario:
            for user_data in scenario["setup"].get("users", []):
                await self.db.update_user(user_data["id"], **user_data)
        
        # 2. Ejecutar pasos
        for step in scenario["steps"]:
            await self._execute_step(step)
        
        # 3. Validar resultados
        results = {}
        for assertion in scenario["assertions"]:
            results[assertion["name"]] = await self._check_assertion(assertion)
        
        return results
    
    async def _execute_step(self, step: dict):
        step_type = step["type"]
        if step_type == "publish_event":
            await self.event_bus.publish(step["event"], step.get("data", {}))
        elif step_type == "db_update":
            await self.db.update_user(step["user_id"], **step["data"])
        await asyncio.sleep(0.05)  # Pequeño delay para async

    async def _check_assertion(self, assertion: dict):
        assertion_type = assertion["type"]
        if assertion_type == "db_value":
            user_id = assertion.get("user_id", 1) # Assuming user_id 1 for now, or get from assertion
            user = await self.db.get_user(user_id)
            if user:
                # Evaluate the check string, e.g., "user.points == 5"
                # This is a simplified evaluation and might need a more robust solution
                # for complex expressions. For now, assuming simple direct checks.
                check_str = assertion["check"]
                # Replace 'user.points' with actual user points
                if "user.points" in check_str:
                    return eval(check_str.replace("user.points", str(user["points"]))) # nosec
                # Add other checks as needed
            return False
        # Add other assertion types as needed
        return False