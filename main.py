
import asyncio
import logging
import threading
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
from src.services.user_service import UserService
from src.services.story_service import StoryService

# Import Scheduling System
from src.core.scheduler_system import SchedulerSystem
from src.services.vip_checker import VIPChecker
from src.services.daily_reset import DailyReset

# Import Admin Services
from src.admin.dashboard_service import DashboardService
from src.admin.mission_designer import MissionDesigner
from src.admin.content_planner import ContentPlanner

# Import Integration Core
from src.core.integration_hub import IntegrationHub, EventLogger

# --- Import Security Layer ---
from src.security.anti_abuse_system import anti_abuse_system
from src.security.auth_middleware import auth_middleware
from src.security.content_guard import content_guard


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
from src.story_system.reward_gateway import setup_reward_gateway
from src.story_system.access_manager import setup_access_manager
from src.story_system.content_linker import setup_content_linker


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

        # Scheduling System
        self.scheduler = SchedulerSystem()
        self.vip_checker = VIPChecker()
        self.daily_reset = DailyReset()

    def setup_integration_hub(self):
        """Configure the IntegrationHub and register all event handlers for the new flows."""
        logger.info("--- Setting up IntegrationHub ---")
        self.event_logger = EventLogger()
        self.hub = IntegrationHub(self.event_logger)

        # Instantiate services required for the hub, passing the hub instance
        self.user_service_hub = UserService(hub=self.hub)
        self.points_service_hub = PointsService(hub=self.hub)
        self.achievements_service_hub = AchievementsService(hub=self.hub)
        self.story_service_hub = StoryService(hub=self.hub)
        self.content_service_hub = ContentService(hub=self.hub)

        # Flow 1: Reacción -> Puntos -> Logro -> Fragmento
        self.hub.register_handler("CHANNEL_REACTION", self.points_service_hub.add_points_for_reaction)
        self.hub.register_handler("POINTS_AWARDED", self.achievements_service_hub.check_for_achievement)
        self.hub.register_handler("ACHIEVEMENT_UNLOCKED", self.story_service_hub.grant_story_fragment)

        # Flow 2: Decisión -> VIP -> Contenido Exclusivo
        self.hub.register_handler("STORY_CHOICE_MADE", self.user_service_hub.grant_temporary_vip)
        self.hub.register_handler("VIP_STATUS_GRANTED", self.content_service_hub.deliver_exclusive_content)
        
        # Initialize Admin Services
        self.dashboard_service = DashboardService(
            user_service=self.user_service_hub,
            points_service=self.points_service_hub,
            achievements_service=self.achievements_service_hub
        )
        self.mission_designer = MissionDesigner(mission_service=self.mission_service, hub=self.hub)
        self.content_planner = ContentPlanner(hub=self.hub)

        logger.info("IntegrationHub and Admin Services have been registered.")

    def setup_event_listeners(self):
        """Subscribe event handlers to the event bus."""
        self.event_bus.subscribe("user_created", on_user_created)
        self.event_bus.subscribe("user_created", on_vip_user_created)
        
        # Gamification Event Listeners
        self.event_bus.subscribe("points_earned", self.on_points_earned)
        self.event_bus.subscribe("level_up", self.on_level_up)
        self.event_bus.subscribe("mission_completed", self.on_mission_completed)
        self.event_bus.subscribe("achievement_unlocked", self.on_achievement_unlocked)

        # Narrative System Listeners
        setup_reward_gateway(self.event_bus)
        setup_access_manager(self.event_bus)
        setup_content_linker(self.event_bus)
        
        logger.info("Event listeners have been set up.")

    async def on_points_earned(self, user_id: int, amount: int, new_balance: int):
        logger.info(f"EVENT [points_earned]: User {user_id} earned {amount} points. New balance: {new_balance}")
        user = User(id=user_id, username="demo", points=new_balance) # Dummy user for demo
        await self.level_service.check_level_up(user.id, user.points - amount, user.points)

    async def on_level_up(self, user_id: int, new_level: str, old_level: str):
        logger.info(f"EVENT [level_up]: User {user_id} leveled up from {old_level} to {new_level}!")
        if new_level == "Maestro":
            await self.achievements_service.unlock_achievement(user_id, "level_maestro")

    async def on_mission_completed(self, user_id: int, mission_id: int, reward_points: int):
        logger.info(f"EVENT [mission_completed]: User {user_id} completed mission {mission_id} and earned {reward_points} points.")

    async def on_achievement_unlocked(self, user_id: int, achievement_id: int, achievement_name: str):
        logger.info(f"EVENT [achievement_unlocked]: User {user_id} unlocked achievement: {achievement_name} (ID: {achievement_id})")

    async def on_reaction_added(self, post_id: int, user_id: int, reaction: str):
        logger.info(f"EVENT [reaction_added]: User {user_id} added reaction '{reaction}' to post {post_id}.")

    async def on_vip_access_granted(self, user_id: int, expiration_date: datetime):
        logger.info(f"EVENT [vip_access_granted]: User {user_id} granted VIP access until {expiration_date}.")

    def test_scheduler_job(self):
        logger.info("Scheduler test job executed!")

    async def run(self):
        """Main execution flow."""
        logger.info("Application starting up...")
        
        self.setup_event_listeners()
        self.setup_integration_hub()

        # Schedule jobs
        self.scheduler.add_job("daily", self.daily_reset.reset_daily_missions)
        self.scheduler.add_job("hourly", self.vip_checker.revoke_expired_vip)
        self.scheduler.add_job("every_minute", self.test_scheduler_job)

        # Start the scheduler in a separate thread
        scheduler_thread = threading.Thread(target=self.scheduler.run_pending_jobs)
        scheduler_thread.daemon = True  # Allow the main program to exit even if the thread is still running
        scheduler_thread.start()

        # Keep the main asyncio loop running indefinitely
        while True:
            await asyncio.sleep(1) # Keep the asyncio loop running

    async def run_security_demo(self):
        """Runs a demonstration of the new security layer components."""
        logger.info("\n" + "="*50 + "\n--- STARTING SECURITY LAYER DEMO ---\n" + "="*50)

        # --- Mock Users for Demo ---
        free_user = User(id=100, username="free_user", role=UserRole.FREE)
        vip_user = User(id=200, username="vip_user", role=UserRole.VIP)
        admin_user = User(id=300, username="admin_user", role=UserRole.ADMIN)
        abusive_user = User(id=400, username="abusive_user", role=UserRole.FREE)

        # --- 1. AuthMiddleware Demo ---
        logger.info("\n--- 1. AuthMiddleware: Access Control Demo ---")

        @auth_middleware.check_access(required_role="VIP")
        async def get_vip_content(user: User):
            logger.info(f"SUCCESS: VIP content delivered to user {user.id}.")
            return "Este es el contenido exclusivo para VIPs."

        @auth_middleware.check_access(required_role="ADMIN")
        async def get_admin_panel(user: User):
            logger.info(f"SUCCESS: Admin panel accessed by user {user.id}.")
            return "Bienvenido al panel de administración."

        # Test cases
        await get_vip_content(free_user)  # Should fail
        await get_vip_content(vip_user)   # Should succeed
        await get_admin_panel(vip_user)   # Should fail
        await get_admin_panel(admin_user) # Should succeed

        # --- 2. ContentGuard Demo ---
        logger.info("\n--- 2. ContentGuard: Watermarking and Protection ---")
        
        vip_content = await get_vip_content(vip_user)
        if vip_content:
            watermarked_content = content_guard.apply_watermark(vip_content, vip_user.id)
            protection_settings = content_guard.disable_forwarding_settings()
            logger.info("Original content: " + vip_content)
            logger.info("Watermarked content: " + watermarked_content)
            logger.info(f"Protection settings to apply on send: {protection_settings}")

        # --- 3. AntiAbuseSystem Demo ---
        logger.info("\n--- 3. AntiAbuseSystem: Rate Limiting and Cooldown ---")
        
        logger.info(f"Simulating high activity for user {abusive_user.id}...")
        for i in range(25):
            # Simulate an interaction
            if anti_abuse_system.is_in_cooldown(abusive_user.id):
                logger.warning(f"Interaction {i+1} BLOCKED: User {abusive_user.id} is in cooldown.")
            else:
                logger.info(f"Interaction {i+1} allowed for user {abusive_user.id}.")
                if anti_abuse_system.detect_patterns(abusive_user.id):
                    logger.error(f"ABUSE DETECTED: User {abusive_user.id} has been put on cooldown.")
            await asyncio.sleep(0.05) # Rapid interactions

        logger.info(f"Simulating an interaction for a normal user {free_user.id}...")
        if not anti_abuse_system.is_in_cooldown(free_user.id):
            anti_abuse_system.detect_patterns(free_user.id)
            logger.info(f"Normal interaction allowed for user {free_user.id}.")

        logger.info("\n" + "="*50 + "\n--- SECURITY LAYER DEMO FINISHED ---\n" + "="*50)


async def main():
    """Asynchronous entry point."""
    import sys
    app = Application()

    # Allow running security demo directly
    if len(sys.argv) > 1 and sys.argv[1] == 'security':
        await app.run_security_demo()
    else:
        await app.run()


if __name__ == "__main__":
    asyncio.run(main())
