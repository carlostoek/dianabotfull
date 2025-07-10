import json
from pathlib import Path
from typing import List, Dict, Optional
import random

class MissionCatalogService:
    """
    Servicio para cargar y gestionar misiones desde un archivo JSON.
    """

    def __init__(self, missions_file: str = "data/missions.json"):
        """
        Inicializa el MissionService cargando las misiones desde el archivo especificado.

        Args:
            missions_file (str): La ruta al archivo JSON de misiones.
        """
        self._missions_file = Path(missions_file)
        self._missions = self._load_missions()

    def _load_missions(self) -> List[Dict]:
        """
        Carga las misiones desde el archivo JSON y realiza validaciones básicas.

        Returns:
            List[Dict]: Una lista de diccionarios, cada uno representando una misión.

        Raises:
            FileNotFoundError: Si el archivo de misiones no se encuentra.
            json.JSONDecodeError: Si el archivo JSON está malformado.
            ValueError: Si alguna misión no cumple con la estructura requerida.
        """
        if not self._missions_file.exists():
            raise FileNotFoundError(f"El archivo de misiones no se encontró en: {self._missions_file}")

        try:
            with open(self._missions_file, 'r', encoding='utf-8') as f:
                missions_data = json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"El archivo de misiones está malformado: {e}", e.doc, e.pos)

        # Validar la estructura de cada misión
        required_keys = ["id", "title", "description", "reward", "time_limit", "category"]
        for mission in missions_data:
            if not all(key in mission for key in required_keys):
                raise ValueError(f"Misión con estructura inválida. Faltan claves requeridas en: {mission}")
        return missions_data

    def get_all_missions(self) -> List[Dict]:
        """
        Retorna todas las misiones cargadas.

        Returns:
            List[Dict]: Una lista de todas las misiones.
        """
        return self._missions

    def get_mission_by_id(self, mission_id: str) -> Optional[Dict]:
        """
        Retorna una misión específica por su ID.

        Args:
            mission_id (str): El ID de la misión a buscar.

        Returns:
            Optional[Dict]: La misión si se encuentra, de lo contrario None.
        """
        for mission in self._missions:
            if mission["id"] == mission_id:
                return mission
        return None

    def get_random_mission(self, category: Optional[str] = None) -> Optional[Dict]:
        """
        Devuelve una misión aleatoria, opcionalmente filtrada por categoría.

        Args:
            category (Optional[str]): La categoría de la misión a buscar. Si es None,
                                      se selecciona una misión de cualquier categoría.

        Returns:
            Optional[Dict]: Una misión aleatoria que coincide con la categoría,
                            o None si no hay misiones disponibles para la categoría.
        """
        if category:
            filtered_missions = [m for m in self._missions if m["category"] == category]
            if filtered_missions:
                return random.choice(filtered_missions)
            return None
        elif self._missions:
            return random.choice(self._missions)
        return None

if __name__ == "__main__":
    # Ejemplo de uso (asumiendo que data/missions.json existe y es válido)
    # Para probar esto, necesitarías un archivo data/missions.json
    # con el formato esperado.
    try:
        # Crear un archivo missions.json de ejemplo para la prueba
        example_missions_content = """
[
    {
        "id": "m1",
        "title": "Misión de Prueba 1",
        "description": "Esta es la primera misión de prueba.",
        "reward": 100,
        "time_limit": 3600,
        "category": "interacción"
    },
    {
        "id": "m2",
        "title": "Misión de Prueba 2",
        "description": "Esta es la segunda misión de prueba.",
        "reward": 150,
        "time_limit": 7200,
        "category": "exploración"
    },
    {
        "id": "m3",
        "title": "Misión de Prueba 3",
        "description": "Esta es la tercera misión de prueba.",
        "reward": 200,
        "time_limit": 1800,
        "category": "interacción"
    }
]
        """
        Path("data").mkdir(exist_ok=True)
        with open("data/missions.json", "w", encoding="utf-8") as f:
            f.write(example_missions_content)

        service = MissionService()

        print("Todas las misiones:")
        for mission in service.get_all_missions():
            print(f"- {mission['title']} ({mission['category']})")

        print("\nMisión por ID 'm1':")
        mission_by_id = service.get_mission_by_id("m1")
        if mission_by_id:
            print(f"- {mission_by_id['title']}")
        else:
            print("Misión 'm1' no encontrada.")

        print("\nMisión aleatoria (cualquier categoría):")
        random_mission = service.get_random_mission()
        if random_mission:
            print(f"- {random_mission['title']} ({random_mission['category']})")
        else:
            print("No hay misiones disponibles.")

        print("\nMisión aleatoria de categoría 'interacción':")
        random_interaction_mission = service.get_random_mission("interacción")
        if random_interaction_mission:
            print(f"- {random_interaction_mission['title']} ({random_interaction_mission['category']})")
        else:
            print("No hay misiones de categoría 'interacción'.")

        print("\nMisión aleatoria de categoría 'inexistente':")
        random_nonexistent_mission = service.get_random_mission("inexistente")
        if random_nonexistent_mission:
            print(f"- {random_nonexistent_mission['title']} ({random_nonexistent_mission['category']})")
        else:
            print("No hay misiones de categoría 'inexistente'.")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except json.JSONDecodeError as e:
        print(f"Error de formato JSON: {e}")
    except ValueError as e:
        print(f"Error de validación de misión: {e}")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
    finally:
        # Limpiar el archivo de ejemplo
        if Path("data/missions.json").exists():
            Path("data/missions.json").unlink()
        if Path("data").exists() and not list(Path("data").iterdir()):
            Path("data").rmdir()
