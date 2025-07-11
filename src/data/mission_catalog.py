import json
import random
from pathlib import Path
from typing import Dict, List, Optional

class MissionCatalog:
    """A catalog to load and manage missions from a JSON file.

    Handles loading, validation, and retrieval of missions, providing methods
    to access all missions, a specific mission by ID, or a random mission
    optionally filtered by category.
    """

    def __init__(self, missions_file: Path = Path("data/missions.json")):
        """Initializes the MissionCatalog by loading and validating missions.

        Args:
            missions_file (Path): The path to the missions JSON file.
        
        Raises:
            FileNotFoundError: If the missions file cannot be found.
            ValueError: If the JSON is malformed or a mission is invalid.
        """
        self._missions: List[Dict] = []
        self._missions_by_id: Dict[str, Dict] = {}
        self._load_missions(missions_file)

    def _load_missions(self, missions_file: Path):
        """Loads and validates missions from the specified JSON file."""
        required_keys = {"id", "title", "description", "reward", "time_limit", "category"}
        try:
            with open(missions_file, 'r', encoding='utf-8') as f:
                missions_data = json.load(f)
            
            if not isinstance(missions_data, list):
                raise ValueError("Missions JSON must be a list of mission objects.")

            for mission in missions_data:
                if not required_keys.issubset(mission.keys()):
                    raise ValueError(f"Invalid mission data. Missing keys in: {mission}")
                self._missions.append(mission)
                self._missions_by_id[mission["id"]] = mission
        except FileNotFoundError:
            print(f"Error: Missions file not found at '{missions_file}'.")
            raise
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from '{missions_file}'. Check for syntax errors.")
            raise
        except ValueError as e:
            print(f"Error validating missions data: {e}")
            raise

    def get_all_missions(self) -> List[Dict]:
        """Retrieves all available missions.

        Returns:
            List[Dict]: A list of all missions.
        """
        return self._missions

    def get_mission_by_id(self, mission_id: str) -> Optional[Dict]:
        """Retrieves a single mission by its unique ID.

        Args:
            mission_id (str): The ID of the mission to retrieve.

        Returns:
            Optional[Dict]: The mission dictionary if found, otherwise None.
        """
        return self._missions_by_id.get(mission_id)

    def get_random_mission(self, category: Optional[str] = None) -> Optional[Dict]:
        """Returns a random mission, optionally filtered by category.

        Args:
            category (Optional[str]): The category to filter by. If None,
                a random mission from all available missions is returned.

        Returns:
            Optional[Dict]: A randomly selected mission dictionary, or None if
                no missions are available or the category has no missions.
        """
        if not self._missions:
            return None

        if category:
            categorized_missions = [
                m for m in self._missions if m.get("category") == category
            ]
            if not categorized_missions:
                return None
            return random.choice(categorized_missions)
        
        return random.choice(self._missions)
