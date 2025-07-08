# src/admin/mission_designer.py
import logging
from typing import Dict, Any
from src.core.integration_hub import IntegrationHub
from src.services.mission_service import MissionService

logger = logging.getLogger(__name__)

class MissionDesigner:
    """
    Permite a los administradores crear y configurar nuevas misiones dinámicamente.
    """
    def __init__(self, mission_service: MissionService, hub: IntegrationHub):
        self._mission_service = mission_service
        self._hub = hub
        self._custom_missions: Dict[str, Dict[str, Any]] = {}
        self._mission_progress: Dict[str, Dict[int, int]] = {} # {mission_name: {user_id: progress}}

    def create_mission(self, config: Dict[str, Any]):
        """
        Crea una nueva misión basada en una configuración.
        
        Args:
            config (dict): Un diccionario con 'name', 'description', 'reward_points', 
                           y un 'trigger' con 'event' y 'goal'.
        """
        mission_name = config["name"]
        trigger_event = config["trigger"]["event"]
        
        if mission_name in self._custom_missions:
            logger.warning(f"La misión '{mission_name}' ya existe. No se puede crear de nuevo.")
            return

        # Añade la misión a la lista de misiones personalizadas
        self._custom_missions[mission_name] = config
        self._mission_progress[mission_name] = {}
        
        # Registra un manejador dinámico para el evento disparador
        def handle_trigger(data: dict):
            user_id = data.get("user_id")
            if not user_id:
                return

            progress = self._mission_progress[mission_name].get(user_id, 0)
            progress += 1
            self._mission_progress[mission_name][user_id] = progress
            
            logger.info(f"[MISSION_PROGRESS] Misión: '{mission_name}', Usuario: {user_id}, Progreso: {progress}/{config['trigger']['goal']}")

            if progress >= config["trigger"]["goal"]:
                logger.info(f"¡Usuario {user_id} ha completado la misión personalizada '{mission_name}'!")
                # Aquí se podría llamar a mission_service.complete_mission o directamente al hub
                self._hub.route_event("MISSION_COMPLETED", {
                    "user_id": user_id,
                    "mission_id": mission_name, # Usamos el nombre como ID para misiones personalizadas
                    "reward_points": config["reward_points"]
                })
                # Reiniciar el progreso
                self._mission_progress[mission_name][user_id] = 0

        self._hub.register_handler(trigger_event, handle_trigger)
        logger.info(f"Misión personalizada '{mission_name}' creada y manejador registrado para el evento '{trigger_event}'.")
        return True
