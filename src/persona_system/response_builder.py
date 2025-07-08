from typing import Dict, List
from src.persona_system.emotion_engine import EmotionTone

class ResponseBuilder:
    """
    Formats raw messages, adding emojis and other UI elements.
    """
    _emoji_map: Dict[EmotionTone, List[str]] = {
        EmotionTone.PLAYFUL: ["😉", "😏", "✨"],
        EmotionTone.MYSTERIOUS: ["🤫", "🔮", "🌙"],
        EmotionTone.INTIMATE: ["🌹", "🔥", "🖤"],
        EmotionTone.CONGRATULATORY: ["🥂", "🎉", "👑"],
    }

    def build(self, raw_message: str, tone: EmotionTone) -> str:
        """
        Enhances the raw message with formatting and contextual elements.
        """
        message = raw_message

        # Add a contextual emoji if one is defined for the tone
        if tone in self._emoji_map:
            import random
            emoji = random.choice(self._emoji_map[tone])
            message = f"{message} {emoji}"

        # Here you could add logic for buttons, e.g.,
        # buttons = self._get_buttons_for_tone(tone)
        # return {"text": message, "buttons": buttons}
        
        return message
