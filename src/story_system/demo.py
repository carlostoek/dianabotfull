import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import asyncio
import os
from dotenv import load_dotenv

from src.core.event_bus import EventBus
from src.database.connection import DatabaseManager
from src.story_system.story_engine import StoryEngine
from src.story_system.choice_manager import ChoiceManager
from src.story_system.progress_tracker import ProgressTracker

# Load environment variables from .env file
load_dotenv()

async def main():
    user_id = 1 # Example user ID

    # Initialize EventBus
    event_bus = EventBus()

    # Initialize DatabaseManager
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL environment variable not set. Please configure your database connection.")
        return
    db_manager = DatabaseManager(db_url)
    await db_manager.connect()
    await db_manager.init_db() # Ensure tables are created

    # Ensure a dummy user exists for the demo
    async with db_manager.get_connection() as conn:
        await conn.execute(
            "INSERT INTO users (id, username, role, points) VALUES ($1, $2, $3, $4) ON CONFLICT (id) DO NOTHING",
            user_id, f"user_{user_id}", "player", 0
        )

    # Initialize StoryEngine, ChoiceManager, ProgressTracker
    story_engine = StoryEngine('src/story_system/story.json', event_bus=event_bus)
    progress_tracker = ProgressTracker(db_manager, event_bus=event_bus)
    choice_manager = ChoiceManager(event_bus, progress_tracker)

    # --- Simulate Story Flow ---

    print("\n--- Starting Story ---")
    # Load or start new story
    user_progress = await progress_tracker.load_progress(user_id)
    current_scene_id = user_progress['current_scene_id']

    if current_scene_id == 'start_scene':
        current_scene = await story_engine.start_story('start_scene', user_id)
    else:
        current_scene = await story_engine.get_scene(current_scene_id)
        print(f"Resuming story at scene: {current_scene_id}")

    # Simulate user input
    simulated_choices = ["go_forest", "investigate_whisper", "help_creature", "continue_journey", "final_destination"]
    choice_iterator = iter(simulated_choices)

    while True: # Loop indefinitely until explicitly broken
        if current_scene_id == 'start_scene':
            current_scene = await story_engine.start_story('start_scene', user_id)
        else:
            current_scene = await story_engine.get_scene(current_scene_id)

        if not current_scene:
            print("No current scene found. Exiting story.")
            break

        print(f"\nScene: {current_scene['text']}")
        if current_scene.get('image'):
            print(f"Image: {current_scene['image']}")

        choices = current_scene.get('choices', [])
        if not choices:
            print("End of story path.")
            break

        print("Choices:")
        for i, choice in enumerate(choices):
            print(f"{i+1}. {choice['text']} (ID: {choice['id']})")

        try:
            selected_choice_id = next(choice_iterator)
            print(f"Simulating choice: {selected_choice_id}")
        except StopIteration:
            print("No more simulated choices. Exiting demo.")
            break

        # Find the selected choice object
        selected_choice = next((c for c in choices if c['id'] == selected_choice_id), None)
        
        if not selected_choice:
            print(f"Simulated choice '{selected_choice_id}' not found in current scene. Exiting.")
            break

        next_scene_id, message = await choice_manager.process_choice(user_id, current_scene_id, current_scene, selected_choice_id)
        print(f"Choice result: {message}")

        if next_scene_id:
            current_scene_id = next_scene_id # Update current_scene_id for next iteration
            await progress_tracker.save_progress(user_id, next_scene_id, user_progress['unlocked_fragments'])

            # Simulate unlocking a fragment if applicable (from story.json example)
            if 'unlocks_fragment' in selected_choice:
                fragment_to_unlock = selected_choice['unlocks_fragment']
                await progress_tracker.unlock_fragment(user_id, fragment_to_unlock)
                user_progress['unlocked_fragments'].append(fragment_to_unlock)
        else:
            print("Could not determine next scene. Exiting story.")
            break

    print("\n--- Story Ended ---")
    print(f"Final progress for user {user_id}: {await progress_tracker.load_progress(user_id)}")

    # Disconnect from database
    await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(main())