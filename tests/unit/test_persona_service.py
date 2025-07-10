import pytest
from unittest.mock import AsyncMock, MagicMock
from src.services.persona_service import PersonaService
from src.database.models import UserProgress

@pytest.fixture
def mock_user_progress_repo():
    repo = AsyncMock()
    repo.get_by_user_id.return_value = UserProgress(
        user_id=123,
        diana_state="enigmática",
        resonance_score=50.0,
        unlocked_fragments=[],
        dominant_archetype=None,
        secondary_archetypes=[],
        significant_interactions=[],
        last_interaction_at=None
    )
    repo.update_progress.side_effect = lambda user_id, **kwargs: UserProgress(
        user_id=user_id,
        diana_state=kwargs.get('diana_state', "enigmática"),
        resonance_score=kwargs.get('resonance_score', 50.0),
        unlocked_fragments=[],
        dominant_archetype=None,
        secondary_archetypes=[],
        significant_interactions=[],
        last_interaction_at=None
    )
    return repo

@pytest.fixture
def persona_service(mock_user_progress_repo):
    return PersonaService(user_progress_repo=mock_user_progress_repo)

@pytest.mark.asyncio
async def test_update_diana_state_force_state(persona_service, mock_user_progress_repo):
    user_id = 123
    choice_impact = {
        "diana_state": "vulnerable",
        "resonance_change": 10,
        "archetype_unlock": ["perséfone"]
    }
    
    result = await persona_service.update_diana_state(user_id, choice_impact)
    
    assert result['new_state'] == "vulnerable"
    assert result['resonance_score'] == 60.0
    assert "perséfone" in result['unlocked_archetypes']
    mock_user_progress_repo.update_progress.assert_called_once()

@pytest.mark.asyncio
async def test_update_diana_state_transition(persona_service, mock_user_progress_repo):
    user_id = 123
    choice_impact = {
        "resonance_change": 5,
        "interaction_type": "empatía"
    }
    
    result = await persona_service.update_diana_state(user_id, choice_impact)
    
    assert result['new_state'] == "vulnerable"
    assert result['resonance_score'] == 55.0
    mock_user_progress_repo.update_progress.assert_called_once()

@pytest.mark.asyncio
async def test_update_diana_state_no_user_progress(persona_service, mock_user_progress_repo):
    user_id = 999
    mock_user_progress_repo.get_by_user_id.return_value = None
    choice_impact = {"diana_state": "vulnerable"}
    
    with pytest.raises(ValueError, match=f"No se encontró progreso para el usuario {user_id}"):
        await persona_service.update_diana_state(user_id, choice_impact)

@pytest.mark.asyncio
async def test_update_diana_state_resonance_limits(persona_service, mock_user_progress_repo):
    user_id = 123
    # Test upper limit
    mock_user_progress_repo.get_by_user_id.return_value.resonance_score = 95.0
    choice_impact = {"resonance_change": 10}
    result = await persona_service.update_diana_state(user_id, choice_impact)
    assert result['resonance_score'] == 100.0

    # Test lower limit
    mock_user_progress_repo.get_by_user_id.return_value.resonance_score = 5.0
    choice_impact = {"resonance_change": -10}
    result = await persona_service.update_diana_state(user_id, choice_impact)
    assert result['resonance_score'] == 0.0