import logging
from typing import Dict, Optional
from src.database.repository import UserProgressRepository

logger = logging.getLogger(__name__)

class PersonaService:
    """
    Service for managing Diana's persona state and user resonance.
    
    This service handles the application of choice effects on Diana's emotional
    state and the user's resonance score, providing the core personality
    mechanics for the interactive story system.
    """
    
    def __init__(self, user_progress_repo: UserProgressRepository):
        """
        Initialize the PersonaService with a user progress repository.
        
        Args:
            user_progress_repo: Repository for accessing user progress data
        """
        self.user_progress_repo = user_progress_repo
    
    async def apply_choice_effects(self, user_id: int, effects: Dict) -> None:
        """
        Apply the effects of a user's choice to Diana's state and resonance score.
        
        Args:
            user_id: ID of the user who made the choice
            effects: Dictionary containing the effects to apply
                    Expected keys: 'diana_state', 'resonance_change'
                    
        Raises:
            ValueError: If user progress is not found or effects are invalid
        """
        # Validate effects dictionary
        if not isinstance(effects, dict):
            raise ValueError("Effects must be a dictionary")
        
        # Get current user progress
        user_progress = await self.user_progress_repo.get_by_user_id(user_id)
        if not user_progress:
            raise ValueError(f"User progress not found for user_id: {user_id}")
        
        # Extract effects with defaults
        diana_state = effects.get('diana_state')
        resonance_change = effects.get('resonance_change', 0)
        
        # Validate resonance_change
        if not isinstance(resonance_change, (int, float)):
            logger.warning(f"Invalid resonance_change type: {type(resonance_change)}, defaulting to 0")
            resonance_change = 0
        
        # Calculate new resonance score and clamp between 0.0 and 10.0
        current_resonance = getattr(user_progress, 'resonance_score', 0.0)
        new_resonance = current_resonance + resonance_change
        new_resonance = max(0.0, min(10.0, new_resonance))
        
        # Prepare update data
        update_data = {'resonance_score': new_resonance}
        
        # Update Diana state if provided
        if diana_state:
            if not isinstance(diana_state, str):
                logger.warning(f"Invalid diana_state type: {type(diana_state)}, skipping state update")
            else:
                update_data['diana_state'] = diana_state
                logger.info(f"Updating Diana state to: {diana_state} for user {user_id}")
        
        # Apply updates
        await self.user_progress_repo.update_progress(user_id, **update_data)
        
        logger.info(
            f"Applied choice effects for user {user_id}: "
            f"resonance {current_resonance} -> {new_resonance}, "
            f"diana_state: {diana_state or 'unchanged'}"
        )
    
    async def get_diana_state(self, user_id: int) -> str:
        """
        Get Diana's current emotional state for a specific user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            String representing Diana's current state
            
        Raises:
            ValueError: If user progress is not found
        """
        user_progress = await self.user_progress_repo.get_by_user_id(user_id)
        if not user_progress:
            raise ValueError(f"User progress not found for user_id: {user_id}")
        
        diana_state = getattr(user_progress, 'diana_state', 'enigmática')
        logger.info(f"Retrieved Diana state for user {user_id}: {diana_state}")
        return diana_state