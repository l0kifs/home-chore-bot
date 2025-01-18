from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvVars(BaseSettings):
    TELEGRAM_BOT_TOKEN: str


    model_config = SettingsConfigDict(env_file='.env')


def get_env_vars() -> EnvVars:
    return EnvVars()  # type: ignore
