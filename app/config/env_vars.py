from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

# Creates a custom version of BaseSettings that manages environment variables
class EnvVars(BaseSettings):
    TELEGRAM_BOT_TOKEN: Optional[str] = None  # Makes the variable optional
    TELEGRAM_CHAT_IDS: Optional[str] = None  # Makes the variable optional
    
    model_config = SettingsConfigDict(env_file='.env')
