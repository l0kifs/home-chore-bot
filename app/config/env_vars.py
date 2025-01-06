from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvVars(BaseSettings):
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHAT_IDS: str

    model_config = SettingsConfigDict(env_file='.env')
