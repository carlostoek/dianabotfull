import random
from src.models.user import User
from src.persona_system.emotion_engine import EmotionTone

class LucienPersona:
    """
    Generates messages with Lucien's unique, elegant, and erotic voice.
    """
    _templates = {
        EmotionTone.NEUTRAL: [
            "Saludos, {username}. ¿En qué puedo asistirte hoy?",
            "Hola, {username}. El sistema está a tu disposición.",
        ],
        EmotionTone.PLAYFUL: [
            "Vaya, vaya, {username}... Veo que has estado explorando. ¿Descubriste algo... interesante? 😉",
            "Ah, {username}, siempre un placer verte curiosear por mis dominios. No te contengas.",
        ],
        EmotionTone.MYSTERIOUS: [
            "Hay secretos esperándote en las sombras, {username}. ¿Te atreves a buscarlos?",
            "Cada paso que das revela un nuevo hilo en el tapiz del destino, {username}. Tira de él.",
        ],
        EmotionTone.INTIMATE: [
            "Mi querid@ {username}, tu presencia aquí es un susurro de deseo en el silencio. ¿Qué anhelas?",
            "Acércate, {username}. Hay confidencias que solo comparto con mis favoritos... y tú eres uno de ellos.",
        ],
        EmotionTone.CONGRATULATORY: [
            "Felicidades, {username}. Has desvelado un secreto que te distingue del resto. Esto te da acceso a un nuevo nivel de placer.",
            "Lo has logrado, {username}. Tu audacia ha sido recompensada. Bienvenido al círculo interno.",
        ]
    }

    def generate_message(self, user: User, tone: EmotionTone, context: str) -> str:
        """
        Generates a personalized message based on tone and context.
        """
        # For now, we select a random template from the chosen tone.
        # The 'context' variable could be used for more advanced generation in the future.
        
        if tone in self._templates:
            template = random.choice(self._templates[tone])
            return template.format(username=user.username)
        
        return f"Hola, {user.username}. {context}"
