# src/core/integration_hub.py
import logging
from collections import defaultdict
from typing import Callable, Any, Dict

# Configuración básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EventLogger:
    """Registra eventos para auditoría y depuración."""
    def log_event(self, event: str, metadata: Dict[str, Any]):
        """
        Registra un evento con sus metadatos asociados.
        
        Args:
            event: El nombre del evento.
            metadata: Un diccionario con datos sobre el evento.
        """
        logger.info(f"[AUDIT] Evento: '{event}', Metadata: {metadata}")

class IntegrationHub:
    """
    Orquestador central que conecta módulos a través de un sistema de eventos.
    Enruta eventos a los manejadores (handlers) registrados.
    """
    def __init__(self, event_logger: EventLogger):
        self._handlers: Dict[str, list[Callable]] = defaultdict(list)
        self._event_logger = event_logger

    def register_handler(self, event: str, callback: Callable):
        """
        Registra una función (callback) para un evento específico.

        Args:
            event: El nombre del evento al que se suscribe.
            callback: La función que se ejecutará cuando ocurra el evento.
        """
        self._handlers[event].append(callback)
        logger.info(f"Handler '{callback.__name__}' registrado para el evento '{event}'.")

    def route_event(self, event: str, data: Dict[str, Any]):
        """
        Enruta un evento a todos los handlers registrados y lo registra.

        Args:
            event: El nombre del evento a enrutar.
            data: El diccionario de datos que se pasará a los handlers.
        """
        self._event_logger.log_event(event, data)
        if event in self._handlers:
            for handler in self._handlers[event]:
                try:
                    handler(data)
                except Exception as e:
                    logger.error(f"Error al ejecutar el handler '{handler.__name__}' para el evento '{event}': {e}", exc_info=True)
        else:
            logger.warning(f"No hay handlers registrados para el evento '{event}'.")
