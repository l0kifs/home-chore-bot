import logging
from telegram.ext import Application
from config.env_vars import EnvVars
import datetime
from infrastructure.telegram_bot import setup_bot, daily_chore_notification

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def main():
    application = Application.builder().token(EnvVars().TELEGRAM_BOT_TOKEN).build()

    # Set up bot handlers
    setup_bot(application)

    # Schedule daily chore notifications
    job_queue = application.job_queue
    job_queue.run_daily(daily_chore_notification, time=datetime.time(hour=2, minute=0, tzinfo=datetime.timezone.utc))

    # Start polling
    application.run_polling()

if __name__ == "__main__":
    main()


# from infrastructure.telegram_bot import main
# from create_tables import init_db

# # This will create the tables in the database
# init_db()

# if __name__ == "__main__":
#     main()