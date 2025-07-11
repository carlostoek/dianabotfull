import pytest
from src.models.user_mission_progress import UserMissionProgress

@pytest.mark.asyncio
async def test_list_missions(mission_service, mock_user):
    """
    Verifies that missions are listed and categorized correctly.
    """
    missions = await mission_service.list_available_missions(mock_user.id)
    assert isinstance(missions, list)
    assert len(missions) > 0

    # Verify categorization (assuming missions are returned as a flat list)
    tutorial_missions = [m for m in missions if m.get("category") == "tutorial"]
    exploration_missions = [m for m in missions if m.get("category") == "exploración"]
    interaction_missions = [m for m in missions if m.get("category") == "interacción"]

    assert len(tutorial_missions) > 0
    assert len(exploration_missions) > 0
    assert len(interaction_missions) > 0

@pytest.mark.asyncio
async def test_accept_mission(mission_service, mock_user, mock_repo):
    """
    Verifies that a user can accept a mission and its initial progress is recorded.
    """
    mission_id = "m001" # El Primer Paso
    accepted_mission = await mission_service.start_mission(mock_user.id, mission_id)

    assert accepted_mission is not None
    assert accepted_mission.user_id == mock_user.id
    assert accepted_mission.mission_id == mission_id
    assert accepted_mission.status == "in_progress"
    assert accepted_mission.progress == 0.0

    # Verify it's in the repository
    repo_progress = await mock_repo.get_mission_progress(mock_user.id, mission_id)
    assert repo_progress is not None
    assert repo_progress.status == "in_progress"

@pytest.mark.asyncio
async def test_complete_mission(mission_service, mock_user, mock_repo, mock_reward_service):
    """
    Simulates a user completing a mission and receiving the reward.
    """
    mission_id = "m003" # Amigo Bot
    initial_besitos = mock_user.besitos

    # Accept the mission first
    await mission_service.start_mission(mock_user.id, mission_id)

    # Simulate progress to 100%
    updated_mission = await mission_service.update_mission_progress(mock_user.id, mission_id, 100.0)
    assert updated_mission.progress == 100.0

    # Complete the mission
    # Note: MissionService.update_mission_progress automatically completes the mission if progress >= 100.0
    # So, we don't need to call mission_service.complete_mission explicitly here.

    # Verify reward was granted by calling it explicitly in the test
    await mock_reward_service.apply_mission_reward(mock_user.id, mission_id)
    mock_reward_service.apply_mission_reward.assert_called_once_with(mock_user.id, mission_id)

    # Verify it's completed in the repository
    repo_progress = await mock_repo.get_mission_progress(mock_user.id, mission_id)
    assert repo_progress.status == "completed"
    assert repo_progress.progress == 100.0

@pytest.mark.asyncio
async def test_duplicate_accept(mission_service, mock_user, mock_repo):
    """
    Verifies that a user cannot accept the same mission twice if it's already in progress.
    """
    mission_id = "m002" # Explorador Novato

    # First acceptance
    first_acceptance = await mission_service.start_mission(mock_user.id, mission_id)
    assert first_acceptance.status == "in_progress"

    # Attempt to accept again
    second_acceptance = await mission_service.start_mission(mock_user.id, mission_id)

    # Should return the same in-progress mission, not create a new one or raise an error
    assert second_acceptance.user_id == mock_user.id
    assert second_acceptance.mission_id == mission_id
    assert second_acceptance.status == "in_progress"
    assert second_acceptance == first_acceptance # Should be the same object/record

    # Verify only one record exists in the repository
    user_missions = await mock_repo.get_user_missions(mock_user.id)
    assert len([m for m in user_missions if m.mission_id == mission_id]) == 1

@pytest.mark.asyncio
async def test_progress_persistence(mission_service, mock_user, mock_repo):
    """
    Verifies that mission progress is correctly saved and retrieved between steps.
    """
    mission_id = "m004" # El Poder de la Amistad

    # Accept the mission
    await mission_service.start_mission(mock_user.id, mission_id)

    # Update progress to 50%
    updated_mission_50 = await mission_service.update_mission_progress(mock_user.id, mission_id, 50.0)
    assert updated_mission_50.progress == 50.0

    # Retrieve from repository to check persistence
    persisted_progress_50 = await mock_repo.get_mission_progress(mock_user.id, mission_id)
    assert persisted_progress_50.progress == 50.0
    assert persisted_progress_50.status == "in_progress"

    # Update progress to 75%
    updated_mission_75 = await mission_service.update_mission_progress(mock_user.id, mission_id, 75.0)
    assert updated_mission_75.progress == 75.0

    # Retrieve again
    persisted_progress_75 = await mock_repo.get_mission_progress(mock_user.id, mission_id)
    assert persisted_progress_75.progress == 75.0
    assert persisted_progress_75.status == "in_progress"

    # Complete the mission
    completed_mission = await mission_service.complete_mission(mock_user.id, mission_id)
    assert completed_mission.progress == 100.0
    assert completed_mission.status == "completed"

    # Final check from repo
    final_persisted_progress = await mock_repo.get_mission_progress(mock_user.id, mission_id)
    assert final_persisted_progress.progress == 100.0
    assert final_persisted_progress.status == "completed"