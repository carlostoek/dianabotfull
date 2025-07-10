import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
import json
import tempfile
import os

from src.services.story_service import StoryService
from src.services.persona_service import PersonaService

class MockUserProgress:
    """Mock class for UserProgress model."""
    
    def __init__(self, user_id: int, diana_state: str = "enigmática", resonance_score: float = 0.0):
        self.user_id = user_id
        self.diana_state = diana_state
        self.resonance_score = resonance_score

@pytest.fixture
def mock_user_progress_repo():
    """Create a mock UserProgressRepository."""
    repo = AsyncMock()
    
    # Setup default user progress
    default_progress = MockUserProgress(user_id=123)
    repo.get_by_user_id.return_value = default_progress
    repo.update_progress.return_value = default_progress
    
    return repo

@pytest.fixture
def test_story_data():
    """Create test story data."""
    return {
        "start": {
            "text": "Test story beginning",
            "choices": [
                {
                    "id": "choice_1",
                    "text": "Test choice 1",
                    "next_scene": "scene_2",
                    "impact": {
                        "diana_state": "happy",
                        "resonance_change": 2.0
                    }
                },
                {
                    "id": "choice_2", 
                    "text": "Test choice 2",
                    "next_scene": "scene_3",
                    "impact": {
                        "diana_state": "sad",
                        "resonance_change": -1.0
                    }
                }
            ],
            "meta": {
                "is_initial": True
            }
        },
        "scene_2": {
            "text": "Happy path scene",
            "choices": []
        },
        "scene_3": {
            "text": "Sad path scene", 
            "choices": []
        }
    }

@pytest.fixture
def test_story_file(test_story_data):
    """Create a temporary story file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_story_data, f)
        temp_file_path = f.name
    
    yield temp_file_path
    
    # Cleanup
    os.unlink(temp_file_path)

@pytest.fixture
def story_service(test_story_file):
    """Create a StoryService instance with test data."""
    return StoryService(test_story_file)

@pytest.fixture
def persona_service(mock_user_progress_repo):
    """Create a PersonaService instance with mocked repository."""
    return PersonaService(mock_user_progress_repo)

class TestStoryFlow:
    """Integration tests for story flow functionality."""
    
    @pytest.mark.asyncio
    async def test_story_initialization(self, story_service):
        """Test that story initializes correctly."""
        # Should be able to get initial node
        initial_node_id = story_service.get_initial_node()
        assert initial_node_id == "start"
        
        # Should be able to get the initial node content
        initial_node = story_service.get_node(initial_node_id)
        assert initial_node is not None
        assert "text" in initial_node
        assert "choices" in initial_node
        assert len(initial_node["choices"]) == 2
    
    @pytest.mark.asyncio
    async def test_choice_effects_happy_path(self, persona_service, mock_user_progress_repo):
        """Test that a choice correctly changes diana_state and resonance_score (happy path)."""
        user_id = 123
        
        # Setup initial state
        initial_progress = MockUserProgress(user_id=user_id, diana_state="enigmática", resonance_score=5.0)
        mock_user_progress_repo.get_by_user_id.return_value = initial_progress
        
        # Define choice effects
        effects = {
            "diana_state": "happy",
            "resonance_change": 2.0
        }
        
        # Apply choice effects
        await persona_service.apply_choice_effects(user_id, effects)
        
        # Verify repository was called correctly
        mock_user_progress_repo.get_by_user_id.assert_called_once_with(user_id)
        mock_user_progress_repo.update_progress.assert_called_once_with(
            user_id,
            resonance_score=7.0,  # 5.0 + 2.0
            diana_state="happy"
        )
    
    @pytest.mark.asyncio
    async def test_choice_effects_negative_resonance(self, persona_service, mock_user_progress_repo):
        """Test that a choice correctly applies negative resonance change."""
        user_id = 123
        
        # Setup initial state
        initial_progress = MockUserProgress(user_id=user_id, diana_state="enigmática", resonance_score=3.0)
        mock_user_progress_repo.get_by_user_id.return_value = initial_progress
        
        # Define choice effects with negative resonance
        effects = {
            "diana_state": "sad",
            "resonance_change": -1.0
        }
        
        # Apply choice effects
        await persona_service.apply_choice_effects(user_id, effects)
        
        # Verify repository was called correctly
        mock_user_progress_repo.get_by_user_id.assert_called_once_with(user_id)
        mock_user_progress_repo.update_progress.assert_called_once_with(
            user_id,
            resonance_score=2.0,  # 3.0 - 1.0
            diana_state="sad"
        )
    
    @pytest.mark.asyncio
    async def test_resonance_score_clamping(self, persona_service, mock_user_progress_repo):
        """Test that resonance score is clamped between 0.0 and 10.0."""
        user_id = 123
        
        # Test upper bound clamping
        initial_progress = MockUserProgress(user_id=user_id, resonance_score=9.0)
        mock_user_progress_repo.get_by_user_id.return_value = initial_progress
        
        effects = {"resonance_change": 5.0}  # Would result in 14.0 without clamping
        await persona_service.apply_choice_effects(user_id, effects)
        
        # Should be clamped to 10.0
        args, kwargs = mock_user_progress_repo.update_progress.call_args
        assert kwargs['resonance_score'] == 10.0
        
        # Reset mock
        mock_user_progress_repo.reset_mock()
        
        # Test lower bound clamping
        initial_progress.resonance_score = 1.0
        effects = {"resonance_change": -5.0}  # Would result in -4.0 without clamping
        await persona_service.apply_choice_effects(user_id, effects)
        
        # Should be clamped to 0.0
        args, kwargs = mock_user_progress_repo.update_progress.call_args
        assert kwargs['resonance_score'] == 0.0
    
    @pytest.mark.asyncio
    async def test_get_diana_state(self, persona_service, mock_user_progress_repo):
        """Test getting Diana's current state."""
        user_id = 123
        expected_state = "mysterious"
        
        # Setup mock progress
        progress = MockUserProgress(user_id=user_id, diana_state=expected_state)
        mock_user_progress_repo.get_by_user_id.return_value = progress
        
        # Get Diana state
        result_state = await persona_service.get_diana_state(user_id)
        
        # Verify result
        assert result_state == expected_state
        mock_user_progress_repo.get_by_user_id.assert_called_once_with(user_id)
    
    @pytest.mark.asyncio
    async def test_user_not_found_error(self, persona_service, mock_user_progress_repo):
        """Test error handling when user progress is not found."""
        user_id = 999
        
        # Setup mock to return None (user not found)
        mock_user_progress_repo.get_by_user_id.return_value = None
        
        # Should raise ValueError for apply_choice_effects
        with pytest.raises(ValueError, match="User progress not found"):
            await persona_service.apply_choice_effects(user_id, {"resonance_change": 1.0})
        
        # Should raise ValueError for get_diana_state
        with pytest.raises(ValueError, match="User progress not found"):
            await persona_service.get_diana_state(user_id)
    
    @pytest.mark.asyncio
    async def test_invalid_effects_handling(self, persona_service, mock_user_progress_repo):
        """Test handling of invalid effects data."""
        user_id = 123
        
        # Setup mock progress
        progress = MockUserProgress(user_id=user_id)
        mock_user_progress_repo.get_by_user_id.return_value = progress
        
        # Test with non-dict effects
        with pytest.raises(ValueError, match="Effects must be a dictionary"):
            await persona_service.apply_choice_effects(user_id, "invalid")
        
        # Test with invalid resonance_change type (should default to 0)
        effects = {"resonance_change": "invalid_number"}
        await persona_service.apply_choice_effects(user_id, effects)
        
        # Should still update with resonance_change of 0
        args, kwargs = mock_user_progress_repo.update_progress.call_args
        assert kwargs['resonance_score'] == 0.0  # Original 0.0 + 0 (defaulted)
    
    @pytest.mark.asyncio 
    async def test_story_node_retrieval(self, story_service):
        """Test retrieving specific story nodes."""
        # Test existing node
        node = story_service.get_node("start")
        assert node is not None
        assert node["text"] == "Test story beginning"
        
        # Test non-existing node
        node = story_service.get_node("nonexistent")
        assert node is None
    
    @pytest.mark.asyncio
    async def test_story_validation_error(self):
        """Test story validation with invalid data."""
        # Create invalid story data (missing 'text' field)
        invalid_data = {
            "start": {
                "choices": []  # Missing required 'text' field
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(invalid_data, f)
            temp_file = f.name
        
        try:
            # Should raise ValueError due to validation
            with pytest.raises(ValueError, match="missing required 'text' field"):
                StoryService(temp_file)
        finally:
            os.unlink(temp_file)
    
    @pytest.mark.asyncio
    async def test_story_file_not_found(self):
        """Test error handling when story file doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Story file not found"):
            StoryService("nonexistent_file.json")