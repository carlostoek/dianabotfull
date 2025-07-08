from enum import Enum, auto
from src.models.user import User, UserRole

class EmotionTone(Enum):
    """
    Defines the emotional tones Lucien can adopt.
    """
    NEUTRAL = auto()
    PLAYFUL = auto()
    MYSTERIOUS = auto()
    INTIMATE = auto()
    CONGRATULATORY = auto()

class EmotionEngine:
    """
    Determines the appropriate emotional tone for a message based on user context.
    """
    def get_tone(self, user: User) -> EmotionTone:
        """
        Selects a tone based on the user's role and progress.
        """
        # Prioritize VIPs with more intimate tones
        if user.role == UserRole.VIP:
            # Check for specific milestones
            if "fragment_5" in user.unlocked_fragments:
                return EmotionTone.CONGRATULATORY
            return EmotionTone.INTIMATE

        # For free users, be more playful or mysterious
        if user.points > 500:
            return EmotionTone.MYSTERIOUS
        
        if len(user.unlocked_fragments) > 0:
            return EmotionTone.PLAYFUL

        return EmotionTone.NEUTRAL
