
import asyncio
import logging

from src.core.config import settings, setup_logging
from src.core.event_bus import EventBus
from src.database.connection import DatabaseManager
from src.models.user import User, UserRole

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

    def setup_event_listeners(self):
        """Subscribe event handlers to the event bus."""
        self.event_bus.subscribe("user_created", on_user_created)
        self.event_bus.subscribe("user_created", on_vip_user_created)
        logger.info("Event listeners have been set up.")

    async def run(self):
        """Main execution flow."""
        logger.info("Application starting up...")
        await self.db_manager.connect()
        await self.db_manager.init_db()
        self.setup_event_listeners()

        # --- DEMO: Create and retrieve a user ---
        try:
            async with self.db_manager.get_connection() as conn:
                # Clean up previous demo user if exists
                await conn.execute("DELETE FROM users WHERE username IN ('demo_user', 'vip_user')")

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


                # 3. Retrieve a user
                logger.info("--- Retrieving a user from DB ---")
                retrieved_row = await conn.fetchrow("SELECT * FROM users WHERE username = $1", 'demo_user')
                if retrieved_row:
                    retrieved_user = User.model_validate(dict(retrieved_row))
                    logger.info(f"Successfully retrieved user: {retrieved_user.model_dump_json(indent=2)}")

        except Exception as e:
            logger.error(f"An error occurred during the demo execution: {e}", exc_info=True)
        finally:
            logger.info("Application shutting down...")
            await self.db_manager.disconnect()


async def main():
    """Asynchronous entry point."""
    app = Application()
    await app.run()

if __name__ == "__main__":
    asyncio.run(main())
