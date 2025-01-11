# Brings tools from pydantic_settins package, BaseSettings - manages configuration settings, SettingsConfigDict - specify additional conf
from pydantic_settings import BaseSettings, SettingsConfigDict

# Creates a custom version of BaseSettings that manages environment variables
class EnvVars(BaseSettings):
    # Defines the class atributes of type str
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHAT_IDS: str
    
    # This config tells pydantic to load settings from the file named .env
    model_config = SettingsConfigDict(env_file='.env')
