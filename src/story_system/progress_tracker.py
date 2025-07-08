class ProgressTracker:
    def __init__(self, db_manager, event_bus=None):
        self.db_manager = db_manager
        self.event_bus = event_bus

    async def save_progress(self, user_id, current_scene_id, unlocked_fragments=None):
        async with self.db_manager.get_connection() as conn:
            # Example: Save current scene ID
            await conn.execute(
                "INSERT INTO user_progress (user_id, current_scene_id) VALUES ($1, $2) ON CONFLICT (user_id) DO UPDATE SET current_scene_id = $2",
                user_id, current_scene_id
            )
            # Example: Save unlocked fragments (simplified, might need a separate table)
            if unlocked_fragments:
                for fragment_id in unlocked_fragments:
                    await conn.execute(
                        "INSERT INTO user_unlocked_fragments (user_id, fragment_id) VALUES ($1, $2) ON CONFLICT DO NOTHING",
                        user_id, fragment_id
                    )
        print(f"Saving progress for user {user_id}: current_scene={current_scene_id}, unlocked_fragments={unlocked_fragments}")

    async def load_progress(self, user_id):
        async with self.db_manager.get_connection() as conn:
            row = await conn.fetchrow("SELECT current_scene_id FROM user_progress WHERE user_id = $1", user_id)
            fragments = await conn.fetch("SELECT fragment_id FROM user_unlocked_fragments WHERE user_id = $1", user_id)
            unlocked_fragments = [f['fragment_id'] for f in fragments]
            if row:
                return {'current_scene_id': row['current_scene_id'], 'unlocked_fragments': unlocked_fragments}
            return {'current_scene_id': 'start_scene', 'unlocked_fragments': []} # Placeholder if no progress found

    async def unlock_fragment(self, user_id, fragment_id):
        async with self.db_manager.get_connection() as conn:
            await conn.execute(
                "INSERT INTO user_unlocked_fragments (user_id, fragment_id) VALUES ($1, $2) ON CONFLICT DO NOTHING",
                user_id, fragment_id
            )
        if self.event_bus:
            await self.event_bus.publish('fragment_unlocked', user_id, fragment_id)
        print(f"Unlocking fragment {fragment_id} for user {user_id}")
