import json

class StoryEngine:
    def __init__(self, story_data_path, event_bus=None):
        self.story_data = self._load_story_data(story_data_path)
        self.current_scene = None
        self.event_bus = event_bus

    def _load_story_data(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    async def get_scene(self, scene_id):
        return self.story_data.get(scene_id)

    async def start_story(self, initial_scene_id, user_id):
        self.current_scene = await self.get_scene(initial_scene_id)
        if self.event_bus:
            await self.event_bus.publish('story_started', user_id, initial_scene_id)
        return self.current_scene

    def make_choice(self, choice_id):
        # This will be handled by ChoiceManager, but a placeholder for now
        pass
