import logging
from src.services import user_service
from src.persona_system.emotion_engine import EmotionEngine
from src.persona_system.lucien_persona import LucienPersona
from src.persona_system.response_builder import ResponseBuilder

logger = logging.getLogger(__name__)

class PersonaService:
    """
    A facade that orchestrates the persona components to generate a complete response.
    """
    def __init__(self):
        self.emotion_engine = EmotionEngine()
        self.lucien_persona = LucienPersona()
        self.response_builder = ResponseBuilder()

    def create_response(self, user_id: int, context: str = "...") -> str:
        """
        Generates a fully-formed, personalized message from Lucien.

        Args:
            user_id: The ID of the user to address.
            context: A string describing the situation for the message.

        Returns:
            A formatted message string.
        """
        user = user_service.get_user(user_id)
        if not user:
            logger.warning(f"Could not generate persona message for non-existent user {user_id}")
            return "Un alma perdida busca respuestas en el vacío..."

        # 1. Determine the emotional tone
        tone = self.emotion_engine.get_tone(user)

        # 2. Generate the base message
        raw_message = self.lucien_persona.generate_message(user, tone, context)

        # 3. Build the final response with formatting
        final_response = self.response_builder.build(raw_message, tone)

        logger.info(f"Generated persona message for user {user_id} with tone '{tone.name}'.")
        return final_response

# Singleton instance for easy access across the application
persona_service = PersonaService()
