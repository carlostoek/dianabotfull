# src/admin/content_planner.py
import logging
from typing import Dict, Any
from src.core.integration_hub import IntegrationHub

logger = logging.getLogger(__name__)

class ContentPlanner:
    """
    Permite programar la entrega de contenido basada en eventos (disparadores).
    """
    def __init__(self, hub: IntegrationHub):
        self._hub = hub
        self._scheduled_content: list[dict] = []

    def schedule_post(self, content: str, trigger_condition: str):
        """
        Programa la publicación de contenido cuando se cumple una condición.

        Args:
            content (str): El contenido a publicar.
            trigger_condition (str): La condición en formato "EVENTO:VALOR_ESPERADO".
                                     Ej: "ACHIEVEMENT_UNLOCKED:level_maestro"
        """
        try:
            event_name, expected_value = trigger_condition.split(":", 1)
        except ValueError:
            logger.error(f"La condición de disparo '{trigger_condition}' es inválida. Debe tener el formato 'EVENTO:VALOR'.")
            return

        schedule_config = {
            "content": content,
            "trigger_event": event_name,
            "expected_value": expected_value
        }
        self._scheduled_content.append(schedule_config)

        # Registra un manejador dinámico para el evento
        def handle_content_delivery(data: dict):
            # Busca la clave que podría contener el valor a comparar.
            # Por ejemplo, en ACHIEVEMENT_UNLOCKED, podría ser 'achievement_name'.
            # Esto es una simplificación; un sistema real necesitaría una forma más robusta de mapear.
            value_to_check = data.get("achievement_name") or data.get("mission_id") or data.get("status")

            if value_to_check == expected_value:
                logger.info(f"[CONTENT_DELIVERY] Condición '{trigger_condition}' cumplida. Entregando contenido.")
                # En un sistema real, esto se enviaría a un canal o usuario.
                # Aquí, simplemente lo mostraremos en la consola.
                print("\n--- CONTENIDO PROGRAMADO ENTREGADO ---")
                print(f"Disparador: {trigger_condition}")
                print(f"Contenido: {content}")
                print("-------------------------------------\n")

        self._hub.register_handler(event_name, handle_content_delivery)
        logger.info(f"Contenido programado. Se entregará cuando ocurra '{trigger_condition}'.")
        return True
