# tests/integration/test_full_flow.py
import pytest
from datetime import datetime
from src.database.models import User

@pytest.mark.asyncio
async def test_reaction_to_story_unlock(integration_hub, mock_db):
    # 1. Configuración inicial
    user_id = 1
    await mock_db.update_user(user_id, points=0, role="free")
    
    # 2. Disparar evento de reacción (como si viniera de Telegram)
    await integration_hub.event_bus.publish(
        "reaction_added",
        {"user_id": user_id, "emoji": "❤️", "channel_id": 1}
    )
    
    # 3. Verificar progresión esperada
    user = await mock_db.get_user(user_id)
    assert user["points"] == 5  # Verifica puntos
    
    # 4. Simular acumulación de puntos para logro
    await mock_db.update_user(user_id, points=100)
    await integration_hub.event_bus.publish(
        "POINTS_AWARDED",
        {"user_id": user_id, "amount": 100}
    )
    
    # 5. Verificar fragmento desbloqueado
    fragments = await mock_db.get_unlocked_fragments(user_id)
    assert "fragment_vip_1" in fragments
