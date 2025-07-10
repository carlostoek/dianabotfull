import json
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class StoryService:
    """
    Service for loading and managing story nodes from a JSON file.
    
    This service provides access to interactive story content and manages
    story progression through various nodes and choices.
    """
    
    def __init__(self, story_file_path: str = "data/story.json"):
        """
        Initialize the StoryService with a story file.
        
        Args:
            story_file_path: Path to the story JSON file
            
        Raises:
            FileNotFoundError: If the story file doesn't exist
            json.JSONDecodeError: If the story file is not valid JSON
        """
        self.story_file_path = Path(story_file_path)
        self.story_data = self._load_story_data()
        
    def _load_story_data(self) -> Dict:
        """
        Load story data from the JSON file.
        
        Returns:
            Dictionary containing all story nodes
            
        Raises:
            FileNotFoundError: If the story file doesn't exist
            json.JSONDecodeError: If the story file is not valid JSON
        """
        try:
            if not self.story_file_path.exists():
                raise FileNotFoundError(f"Story file not found: {self.story_file_path}")
            
            with open(self.story_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self._validate_story_data(data)
            logger.info(f"Story data loaded successfully from {self.story_file_path}")
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in story file {self.story_file_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading story file {self.story_file_path}: {e}")
            raise
    
    def _validate_story_data(self, data: Dict) -> None:
        """
        Validate that story data has the required structure.
        
        Args:
            data: Story data dictionary to validate
            
        Raises:
            ValueError: If story data is invalid
        """
        if not isinstance(data, dict):
            raise ValueError("Story data must be a dictionary")
            
        for node_id, node_data in data.items():
            if not isinstance(node_data, dict):
                raise ValueError(f"Node {node_id} must be a dictionary")
                
            if 'text' not in node_data:
                raise ValueError(f"Node {node_id} missing required 'text' field")
                
            # Validate choices if present
            if 'choices' in node_data:
                if not isinstance(node_data['choices'], list):
                    raise ValueError(f"Node {node_id} 'choices' must be a list")
    
    def get_node(self, node_id: str) -> Optional[Dict]:
        """
        Get a specific story node by its ID.
        
        Args:
            node_id: Unique identifier for the story node
            
        Returns:
            Dictionary containing node data if found, None otherwise
        """
        node = self.story_data.get(node_id)
        if node:
            logger.info(f"Retrieved story node: {node_id}")
        else:
            logger.warning(f"Story node not found: {node_id}")
        return node
    
    def get_initial_node(self) -> str:
        """
        Get the ID of the initial story node.
        
        Returns:
            String ID of the initial node
            
        Raises:
            ValueError: If no initial node can be determined
        """
        # Look for a node marked as initial or use a conventional naming
        for node_id, node_data in self.story_data.items():
            if node_data.get('meta', {}).get('is_initial', False):
                logger.info(f"Found initial node: {node_id}")
                return node_id
        
        # Fallback to conventional naming patterns
        conventional_names = ['start', 'intro', 'level_1_intro', 'beginning']
        for name in conventional_names:
            if name in self.story_data:
                logger.info(f"Using conventional initial node: {name}")
                return name
                
        # Use the first node as last resort
        if self.story_data:
            first_node = next(iter(self.story_data.keys()))
            logger.info(f"Using first node as initial: {first_node}")
            return first_node
            
        raise ValueError("No story nodes found in story data")