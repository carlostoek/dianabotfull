import logging
from src.core.integration_hub import IntegrationHub

logger = logging.getLogger(__name__)

class StoryService:
    """
    Servicio simplificado para gestionar interacciones con el sistema de historias.
    """
    def __init__(self, hub: IntegrationHub):
        self.hub = hub
        # Simulación de fragmentos de historia desbloqueados por usuario
        self._unlocked_fragments = {}

    def grant_story_fragment(self, data: dict):
        """
        Handler para 'ACHIEVEMENT_UNLOCKED'. Otorga un fragmento de historia como recompensa.
        """
        user_id = data.get("user_id")
        achievement_name = data.get("achievement_name")
        
        logger.info(f"[HUB] StoryService: Otorgando fragmento de historia a user '{user_id}' por el logro '{achievement_name}'.")
        
        # Lógica de ejemplo para asignar un fragmento
        fragment_id = f"fragment_for_{achievement_name}"
        
        if user_id not in self._unlocked_fragments:
            self._unlocked_fragments[user_id] = []
        
        if fragment_id not in self._unlocked_fragments[user_id]:
            self._unlocked_fragments[user_id].append(fragment_id)
            logger.info(f"[HUB] StoryService: Fragmento '{fragment_id}' añadido a user '{user_id}'.")
            
            # Este es el final del primer flujo, por lo que no se enruta ningún evento nuevo.
        else:
            logger.info(f"[HUB] StoryService: User '{user_id}' ya posee el fragmento '{fragment_id}'.")

