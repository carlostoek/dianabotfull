
import logging
from pydantic_settings import BaseSettings, SettingsConfigDict

def setup_logging():
    """Configures structured logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

from pydantic import BaseModel
from typing import Dict

class Settings(BaseSettings):
    """
    Manages application settings using Pydantic.
    Reads from environment variables or a .env file.
    """
    DATABASE_URL: str = "sqlite+aiosqlite:///file::memory:?cache=shared"
    TELEGRAM_TOKEN: str | None = None
    ADMIN_IDS: str | None = None
    FREE_CHANNEL_ID: str | None = None
    VIP_CHANNEL_ID: str | None = None
    
    # Configuration for LevelService
    LEVEL_THRESHOLDS: Dict[int, str] = {
        0: "Novato",
        100: "Aprendiz",
        300: "Explorador",
        700: "Maestro",
        1500: "Leyenda"
    }

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')


# Create a single instance to be used across the application
settings = Settings()
