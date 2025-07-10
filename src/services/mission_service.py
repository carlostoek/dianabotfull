# -*- coding: utf-8 -*-
"""
Módulo para gestionar las misiones del bot.

Este módulo define el MissionService, que se encarga de cargar, validar
y proporcionar acceso a las misiones desde un archivo JSON.
"""

import json
import random
from pathlib import Path
from typing import Dict, List, Optional

class MissionService:
    """
    Servicio para gestionar las misiones del juego.

    Carga las misiones desde un archivo JSON, las valida y ofrece métodos
    para acceder a ellas.

    Attributes:
        missions_path (Path): Ruta al archivo JSON de misiones.
    """
    _REQUIRED_KEYS = {"id", "title", "description", "reward", "time_limit", "category"}

    def __init__(self, missions_file_path: str = "data/missions.json"):
        """
        Inicializa el servicio de misiones.

        Args:
            missions_file_path (str): Ruta relativa al archivo de misiones JSON.
        """
        self.missions_path = Path(missions_file_path)
        self._missions: List[Dict] = self._load_missions()

    def _load_missions(self) -> List[Dict]:
        """
        Carga y valida las misiones desde el archivo JSON.

        Maneja errores de archivo no encontrado o formato JSON inválido.

        Returns:
            List[Dict]: Una lista de misiones validadas o una lista vacía si
                        ocurre un error.
        """
        if not self.missions_path.exists():
            print(f"Error: El archivo de misiones no se encontró en '{self.missions_path}'")
            return []

        try:
            with self.missions_path.open('r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                raise TypeError("El JSON de misiones debe ser una lista de objetos.")

            self._validate_missions(data)
            return data
        except FileNotFoundError:
            print(f"Error: El archivo de misiones no se encontró en '{self.missions_path}'")
        except json.JSONDecodeError:
            print(f"Error: El archivo '{self.missions_path}' no contiene un JSON válido.")
        except (KeyError, TypeError) as e:
            print(f"Error en la validación de misiones: {e}")
        
        return []

    def _validate_missions(self, missions_data: List[Dict]):
        """
        Valida que cada misión en la lista contenga las claves requeridas.

        Args:
            missions_data (List[Dict]): La lista de misiones a validar.

        Raises:
            KeyError: Si a una misión le falta una clave requerida.
        """
        for i, mission in enumerate(missions_data):
            if not self._REQUIRED_KEYS.issubset(mission.keys()):
                missing_keys = self._REQUIRED_KEYS - mission.keys()
                raise KeyError(
                    f"La misión en el índice {i} no tiene las claves requeridas: {missing_keys}"
                )

    def get_all_missions(self) -> List[Dict]:
        """
        Retorna todas las misiones cargadas.

        Returns:
            List[Dict]: Una lista de todas las misiones.
        """
        return self._missions

    def get_mission_by_id(self, mission_id: str) -> Optional[Dict]:
        """
        Busca y retorna una misión por su ID.

        Args:
            mission_id (str): El ID de la misión a buscar.

        Returns:
            Optional[Dict]: El diccionario de la misión si se encuentra, de lo contrario None.
        """
        for mission in self._missions:
            if mission.get("id") == mission_id:
                return mission
        return None

    def get_random_mission(self, category: Optional[str] = None) -> Optional[Dict]:
        """
        Retorna una misión aleatoria, opcionalmente filtrada por categoría.

        Args:
            category (Optional[str]): La categoría por la cual filtrar. Si es None,
                                      se elige de entre todas las misiones.

        Returns:
            Optional[Dict]: Un diccionario de misión aleatoria o None si no hay
                            misiones disponibles para los criterios dados.
        """
        if not self._missions:
            return None

        if category:
            filtered_missions = [
                m for m in self._missions if m.get("category") == category
            ]
            if not filtered_missions:
                return None
            return random.choice(filtered_missions)
        
        return random.choice(self._missions)


