import datetime
import logging

from telegram import Update
from telegram.ext import ContextTypes, ApplicationBuilder, CommandHandler
from app.domain.models import Chore, Frequency, Person
from app.domain.services import ChoreDistributionService
from app.use_cases.assign_chores import AssignChoresUseCase


TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"

# Hardcode two sample people for demonstration (use actual Telegram IDs).
# Example: Person 1 => telegram_id=123456, Person 2 => telegram_id=234567
PERSON_1 = Person(telegram_id=111111111, name="Alice")
PERSON_2 = Person(telegram_id=222222222, name="Bob")

# Define your chores here (in real scenario, load from DB or config)
ALL_CHORES = [
    Chore(name="Wash Dishes", frequency=Frequency.DAILY, complexity=1),
    Chore(name="Collect Trash", frequency=Frequency.DAILY, complexity=1),
    Chore(name="Mop Floor", frequency=Frequency.EVERY_5_DAYS, complexity=2),
    Chore(name="Do Laundry", frequency=Frequency.WEEKLY, complexity=3),
]

# Instantiate the needed classes
distribution_service = ChoreDistributionService()
assign_chores_use_case = AssignChoresUseCase(distribution_service)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler for the /start command. 
    Just a greeting message.
    """
    await update.message.reply_text(
        text="Hi! I am your Chore Bot. I'll let you know which chores you have to do today."
    )

async def notify_chores(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    This job runs daily (or whenever you schedule it) 
    to notify each person of their assigned chores for today.
    """
    # We use today's date to figure out chores
    reference_date = datetime.date.today()
    persons = [PERSON_1, PERSON_2]

    # Distribute chores
    assignment_map = assign_chores_use_case.execute(ALL_CHORES, persons, reference_date)

    # Send Telegram messages to each user
    for person, chores_list in assignment_map.items():
        if chores_list:
            chores_text = "\n".join([f"- {chore.name}" for chore in chores_list])
            message_text = (
                f"Good morning, {person.name}!\n"
                f"Here are your chores for {reference_date}:\n{chores_text}"
            )
        else:
            message_text = (
                f"Good morning, {person.name}!\n"
                f"You have no chores for {reference_date}.\nEnjoy your free time!"
            )

        try:
            await context.bot.send_message(chat_id=person.telegram_id, text=message_text)
        except Exception as e:
            logging.error(f"Failed to send chores notification to {person.name}: {e}")


def main() -> None:
    """
    Entrypoint: 
    1. Build the telegram application
    2. Register handlers
    3. (Optionally) schedule daily job to notify chores
    4. Start polling
    """
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )

    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Register a /start command handler
    start_handler = CommandHandler("start", start_command)
    application.add_handler(start_handler)

    # Here you could use APScheduler or application.job_queue for daily tasks
    # Example using JobQueue from python-telegram-bot:
    # This schedules notify_chores to run daily at 08:00
    # (Adjust for your timezone or use UTC appropriately)
    job_queue = application.job_queue
    job_queue.run_daily(
        notify_chores,
        time=datetime.time(hour=8, minute=0, second=0),
        name="daily_chore_notification"
    )

    # Start the bot
    application.run_polling()


if __name__ == "__main__":
    main()
