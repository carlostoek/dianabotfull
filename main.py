
import asyncio
import logging
from datetime import datetime

from src.core.config import settings, setup_logging
from src.core.event_bus import EventBus
from src.database.connection import DatabaseManager
from src.models.user import User, UserRole

# Import gamification services
from src.services.points_service import PointsService
from src.services.level_service import LevelService
from src.services.mission_service import MissionService
from src.services.achievements_service import AchievementsService
from src.services.channel_service import ChannelService
from src.services.subscription_service import SubscriptionService
from src.services.content_service import ContentService

# Initialize logger
setup_logging()
logger = logging.getLogger(__name__)

# --- Event Handlers ---
async def on_user_created(user: User):
    """Event handler for when a new user is created."""
    logger.info(f"EVENT [user_created]: A new user has been registered: {user.username} (ID: {user.id})")

async def on_vip_user_created(user: User):
    """Event handler specifically for new VIP users."""
    if user.role == UserRole.VIP:
        logger.info(f"EVENT [vip_user_created]: A new VIP user '{user.username}' just joined! Give them a welcome bonus.")

# --- Main Application Logic ---
class Application:
    """Main application class to orchestrate components."""
    def __init__(self):
        # Dependency Injection: Create instances of services
        self.settings = settings
        self.event_bus = EventBus()
        self.db_manager = DatabaseManager(self.settings.DATABASE_URL)

        # Gamification Services
        self.points_service = PointsService(self.event_bus)
        self.level_service = LevelService(self.event_bus, self.settings)
        self.mission_service = MissionService(self.event_bus)
        self.achievements_service = AchievementsService(self.event_bus)

    def setup_event_listeners(self):
        """Subscribe event handlers to the event bus."""
        self.event_bus.subscribe("user_created", on_user_created)
        self.event_bus.subscribe("user_created", on_vip_user_created)
        
        # Gamification Event Listeners
        self.event_bus.subscribe("points_earned", self.on_points_earned)
        self.event_bus.subscribe("level_up", self.on_level_up)
        self.event_bus.subscribe("mission_completed", self.on_mission_completed)
        self.event_bus.subscribe("achievement_unlocked", self.on_achievement_unlocked)
        
        logger.info("Event listeners have been set up.")

    async def on_points_earned(self, user_id: int, amount: int, new_balance: int):
        logger.info(f"EVENT [points_earned]: User {user_id} earned {amount} points. New balance: {new_balance}")
        # Check for level up after points are earned
        # Note: This requires fetching the user's old points, which is not directly available here.
        # For a real system, you'd fetch the user from DB or pass the user object directly.
        # For this demo, we'll assume the user object is updated and passed around.
        # For now, we'll just call check_level_up with dummy old_points for demonstration.
        # In a real scenario, the user object would be passed to add_points and deduct_points.
        # And the level service would be called with the user's old and new points.
        # For simplicity, let's assume we have access to the user object here.
        # This is a simplification for the demo.
        user = User(id=user_id, username="demo", points=new_balance) # Dummy user for demo
        await self.level_service.check_level_up(user.id, user.points - amount, user.points)

    async def on_level_up(self, user_id: int, new_level: str, old_level: str):
        logger.info(f"EVENT [level_up]: User {user_id} leveled up from {old_level} to {new_level}!")
        # Unlock achievement for reaching Maestro level
        if new_level == "Maestro":
            await self.achievements_service.unlock_achievement(user_id, "level_maestro")

    async def on_mission_completed(self, user_id: int, mission_id: int, reward_points: int):
        logger.info(f"EVENT [mission_completed]: User {user_id} completed mission {mission_id} and earned {reward_points} points.")
        # In a real app, you'd fetch the user and add points.
        # For demo, we'll just log.

    async def on_achievement_unlocked(self, user_id: int, achievement_id: int, achievement_name: str):
        logger.info(f"EVENT [achievement_unlocked]: User {user_id} unlocked achievement: {achievement_name} (ID: {achievement_id})")

    async def on_reaction_added(self, post_id: int, user_id: int, reaction: str):
        logger.info(f"EVENT [reaction_added]: User {user_id} added reaction '{reaction}' to post {post_id}.")

    async def on_vip_access_granted(self, user_id: int, expiration_date: datetime):
        logger.info(f"EVENT [vip_access_granted]: User {user_id} granted VIP access until {expiration_date}.")

    async def run(self):
        """Main execution flow."""
        logger.info("Application starting up...")
        self.db_connected = False
        try:
            await self.db_manager.connect()
            await self.db_manager.init_db()
            self.db_connected = True
            logger.info("Database connection successful.")
        except Exception as e:
            logger.warning(f"Could not connect to the database. Running without database features. Error: {e}")
            # Optionally, you might want to disable certain features or services here
            self.db_connected = False
        
        self.setup_event_listeners()

        # --- DEMO: Create and retrieve a user and test gamification services ---
        if self.db_connected:
            try:
                async with self.db_manager.get_connection() as conn:
                    # Clean up previous demo user if exists
                    await conn.execute("DELETE FROM users WHERE username IN ('demo_user', 'vip_user', 'gami_user')")

                    # 1. Create a new standard user
                    logger.info("--- Creating a new standard user ---")
                    std_user_row = await conn.fetchrow(
                        "INSERT INTO users (username, role, points) VALUES ($1, $2, $3) RETURNING id, username, role, points",
                        'demo_user', UserRole.FREE.value, 50
                    )
                    std_user = User.model_validate(dict(std_user_row))
                    await self.event_bus.publish("user_created", user=std_user)

                    # 2. Create a new VIP user
                    logger.info("--- Creating a new VIP user ---")
                    vip_user_row = await conn.fetchrow(
                        "INSERT INTO users (username, role, points) VALUES ($1, $2, $3) RETURNING id, username, role, points",
                        'vip_user', UserRole.VIP.value, 1000
                    )
                    vip_user = User.model_validate(dict(vip_user_row))
                    await self.event_bus.publish("user_created", user=vip_user)

                    # 3. Create a user for gamification demo
                    logger.info("--- Creating a user for gamification demo ---")
                    gami_user_row = await conn.fetchrow(
                        "INSERT INTO users (username, role, points) VALUES ($1, $2, $3) RETURNING id, username, role, points",
                        'gami_user', UserRole.FREE.value, 0
                    )
                    gami_user = User.model_validate(dict(gami_user_row))
                    await self.event_bus.publish("user_created", user=gami_user)
                    await self.achievements_service.unlock_achievement(gami_user.id, "first_login")

                    # 4. Test PointsService and LevelService
                    logger.info("--- Testing PointsService and LevelService ---")
                    current_level = self.level_service.get_level(gami_user.points)
                    logger.info(f"Gami user initial points: {gami_user.points}, Level: {current_level}")

                    await self.points_service.add_points(gami_user, 150) # Should reach Aprendiz
                    await self.points_service.add_points(gami_user, 200) # Should reach Explorador
                    await self.points_service.add_points(gami_user, 400) # Should reach Maestro
                    await self.points_service.deduct_points(gami_user, 50) # Deduct some points

                    # 5. Test MissionService
                    logger.info("--- Testing MissionService ---")
                    missions = self.mission_service.get_daily_missions(gami_user.id)
                    logger.info(f"Available missions for gami user: {[m.name for m in missions]}")
                    await self.mission_service.complete_mission(gami_user.id, "daily_login")
                    await self.mission_service.complete_mission(gami_user.id, "send_message")
                    await self.mission_service.complete_mission(gami_user.id, "daily_login") # Try completing again

                    # 6. Test AchievementsService
                    logger.info("--- Testing AchievementsService ---")
                    unlocked_achievements = self.achievements_service.get_unlocked_for_user(gami_user.id)
                    logger.info(f"Unlocked achievements for gami user: {[a.name for a in unlocked_achievements]}")
                    
                    # 7. Retrieve a user
                    logger.info("--- Retrieving a user from DB ---")
                    retrieved_row = await conn.fetchrow("SELECT * FROM users WHERE username = $1", 'demo_user')
                    if retrieved_row:
                        retrieved_user = User.model_validate(dict(retrieved_row))
                        logger.info(f"Successfully retrieved user: {retrieved_user.model_dump_json(indent=2)}")

                    # 8. Test ChannelService
                    logger.info("--- Testing ChannelService ---")
                    await self.channel_service.add_channel(chat_id=12345, is_vip=False)
                    await self.channel_service.set_reactions(chat_id=12345, reactions=["👍", "👎", "❤️"])
                    await self.channel_service.add_channel(chat_id=67890, is_vip=True)

                    # 9. Test SubscriptionService
                    logger.info("--- Testing SubscriptionService ---")
                    # Use an existing user for VIP demo, e.g., std_user
                    await self.subscription_service.grant_vip(std_user, 7) # Grant VIP for 7 days
                    is_std_user_vip = self.subscription_service.is_vip(std_user.id)
                    logger.info(f"Is standard user VIP? {is_std_user_vip}")
                    await self.subscription_service.revoke_vip(std_user)
                    is_std_user_vip = self.subscription_service.is_vip(std_user.id)
                    logger.info(f"Is standard user VIP after revoke? {is_std_user_vip}")

                    # 10. Test ContentService
                    logger.info("--- Testing ContentService ---")
                    from datetime import datetime, timedelta
                    future_time = datetime.now() + timedelta(minutes=5)
                    await self.content_service.schedule_post(
                        content="Hello everyone! This is a scheduled post.",
                        schedule_time=future_time,
                        channel_id=12345
                    )
                    # Simulate a reaction to a post
                    await self.content_service.track_engagement(post_id=1, user_id=gami_user.id, engagement_type="reaction_added", value="👍")

            except Exception as e:
                logger.error(f"An error occurred during the demo execution: {e}", exc_info=True)
            finally:
                logger.info("Application shutting down...")
                await self.db_manager.disconnect()
        else:
            logger.warning("Skipping database-dependent demo due to connection failure.")


async def main():
    """Asynchronous entry point."""
    app = Application()
    await app.run()

if __name__ == "__main__":
    asyncio.run(main())
