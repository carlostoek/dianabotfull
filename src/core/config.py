
import logging
from pydantic_settings import BaseSettings, SettingsConfigDict

def setup_logging():
    """Configures structured logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

class Settings(BaseSettings):
    """
    Manages application settings using Pydantic.
    Reads from environment variables or a .env file.
    """
    DATABASE_URL: str = "postgresql://user:password@localhost/db"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

# Create a single instance to be used across the application
settings = Settings()
