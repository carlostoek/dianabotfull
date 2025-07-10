import pytest
from unittest.mock import AsyncMock, MagicMock
from src.services.story_service import StoryService

@pytest.fixture
def mock_story_data():
    return {
        "level_1_intro": {
            "text": "Intro text",
            "choices": [
                {"id": "choice_1", "text": "Choice 1", "next_scene": "level_1_scene_2", "impact": {}},
                {"id": "choice_2", "text": "Choice 2", "next_scene": "level_1_scene_3", "impact": {}}
            ]
        },
        "level_1_scene_2": {
            "text": "Scene 2 text",
            "choices": []
        },
        "level_1_scene_3": {
            "text": "Scene 3 text",
            "choices": []
        }
    }

@pytest.fixture
def story_service(mock_story_data):
    service = StoryService(story_file_path="dummy_path")
    service._load_story_json = MagicMock(return_value=mock_story_data)
    service.story_data = mock_story_data # Ensure story_data is set after mocking
    return service

@pytest.mark.asyncio
async def test_get_scene(story_service):
    scene = await story_service.get_scene("level_1_intro")
    assert scene["text"] == "Intro text"

@pytest.mark.asyncio
async def test_start_story(story_service):
    user_id = 123
    scene = await story_service.start_story(user_id)
    assert scene["text"] == "Intro text"
    assert story_service.current_sessions[user_id] == "level_1_intro"

@pytest.mark.asyncio
async def test_process_choice(story_service):
    user_id = 123
    await story_service.start_story(user_id) # Start story to set current_scene_id
    
    result = await story_service.process_choice(user_id, "choice_1")
    assert result['next_scene']['text'] == "Scene 2 text"
    assert story_service.current_sessions[user_id] == "level_1_scene_2"

@pytest.mark.asyncio
async def test_process_choice_invalid(story_service):
    user_id = 123
    await story_service.start_story(user_id)
    
    with pytest.raises(ValueError, match="Elección invalid_choice no válida para la escena level_1_intro"):
        await story_service.process_choice(user_id, "invalid_choice")

@pytest.mark.asyncio
async def test_process_choice_no_active_session(story_service):
    user_id = 999 # User without active session
    with pytest.raises(ValueError, match="No hay sesión activa para este usuario"):
        await story_service.process_choice(user_id, "choice_1")