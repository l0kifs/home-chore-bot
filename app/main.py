from config.env_vars import get_env_vars
from clients.tg_bot_client import TgBotClient


if __name__ == "__main__":
    bot = TgBotClient(get_env_vars().TELEGRAM_BOT_TOKEN)
    bot.run()
