class ChoiceManager:
    def __init__(self, event_bus, progress_tracker):
        self.event_bus = event_bus
        self.progress_tracker = progress_tracker

    async def process_choice(self, user_id, scene_id, scene, choice_id):
        # Find the chosen choice in the current scene
        chosen_choice = next((c for c in scene.get('choices', []) if c.get('id') == choice_id), None)

        if not chosen_choice:
            return None, "Invalid choice."

        # TODO: Implement cost validation and unlock logic
        # For now, just return the next scene ID
        next_scene_id = chosen_choice.get('next_scene')

        # TODO: Emit choice_made event
        if self.event_bus:
            await self.event_bus.publish('choice_made', user_id, scene_id, choice_id, next_scene_id)

        return next_scene_id, "Choice processed successfully."
