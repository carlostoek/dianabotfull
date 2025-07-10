import json
from typing import Dict, Optional, List
from pathlib import Path

class StoryService:
    def __init__(self, story_file_path: str = "src/data/story.json"):
        self.story_data = self._load_story_json(story_file_path)
        self.current_sessions = {}  # user_id -> current_scene_id
    
    def _load_story_json(self, file_path: str) -> Dict:
        """Carga el archivo story.json"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    async def get_scene(self, scene_id: str) -> Optional[Dict]:
        """Obtiene una escena específica"""
        return self.story_data.get(scene_id)
    
    async def start_story(self, user_id: int, level: int = 1) -> Dict:
        """Inicia la historia para un usuario"""
        start_scene_id = f"level_{level}_intro"
        self.current_sessions[user_id] = start_scene_id
        return await self.get_scene(start_scene_id)
    
    async def process_choice(self, user_id: int, choice_id: str) -> Dict:
        """Procesa la elección del usuario y retorna la siguiente escena"""
        current_scene_id = self.current_sessions.get(user_id)
        if not current_scene_id:
            raise ValueError("No hay sesión activa para este usuario")
        
        current_scene = await self.get_scene(current_scene_id)
        
        # Buscar la elección seleccionada
        for choice in current_scene.get('choices', []):
            if choice['id'] == choice_id:
                next_scene_id = choice['next_scene']
                self.current_sessions[user_id] = next_scene_id
                
                return {
                    'next_scene': await self.get_scene(next_scene_id),
                    'impact': choice.get('impact', {}),
                    'choice_made': choice
                }
        
        raise ValueError(f"Elección {choice_id} no válida para la escena {current_scene_id}")