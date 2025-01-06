import datetime
import logging

from telegram import Update
from telegram.ext import ContextTypes, Application, CommandHandler
from config.env_vars import EnvVars
from domain.models import Chore, Frequency, Person
from domain.services import ChoreDistributionService
from use_cases.assign_chores import AssignChoresUseCase


PERSON_1 = Person(telegram_id=EnvVars().TELEGRAM_CHAT_IDS.split(',')[0], name="Serj")
PERSON_2 = Person(telegram_id=EnvVars().TELEGRAM_CHAT_IDS.split(',')[1], name="Vika")


ALL_CHORES = [
    Chore(name="Вынести мусор", frequency=Frequency.EVERY_3_DAYS, complexity=3),
    Chore(name="Почистить зубы кошкам", frequency=Frequency.DAILY, complexity=2),
    Chore(name="Убрать лотки", frequency=Frequency.DAILY, complexity=3),
    Chore(name="Сменить постельное белье", frequency=Frequency.WEEKLY, complexity=4),
    Chore(name="Помыть полы", frequency=Frequency.WEEKLY, complexity=5),
    Chore(name="Помыть стекла", frequency=Frequency.EVERY_2_MONTHS, complexity=5),
    Chore(name="Помыть холодильник", frequency=Frequency.MONTHLY, complexity=5),
    Chore(name="Полить растения", frequency=Frequency.WEEKLY, complexity=2),
    Chore(name="Помыть ванну", frequency=Frequency.WEEKLY, complexity=3),
    Chore(name="Помыть унитаз", frequency=Frequency.WEEKLY, complexity=2),
    Chore(name="Протереть поверхности на кухне", frequency=Frequency.EVERY_3_DAYS, complexity=3),
    Chore(name="Постирать вещи", frequency=Frequency.EVERY_3_DAYS, complexity=3),
    Chore(name="Собрать мусор", frequency=Frequency.DAILY, complexity=2),
    Chore(name="Помыть посуду", frequency=Frequency.DAILY, complexity=2),
]


distribution_service = ChoreDistributionService()
assign_chores_use_case = AssignChoresUseCase(distribution_service)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler for the /start command. 
    Just a greeting message.
    """
    user_id = update.effective_user.id
    username = update.effective_user.username

    await update.message.reply_text(
        text="Привет! Я бот Антисрач. Расскажу, что тебе делать, чтобы не зарасти говной."
    )

    print(f"User ID: {user_id}, Username: {username}")


async def notify_chores(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    This job runs daily (or whenever you schedule it) 
    to notify each person of their assigned chores for today.
    """
    reference_date = datetime.date.today()
    persons = [PERSON_1, PERSON_2]

    assignment_map = assign_chores_use_case.execute(
        ALL_CHORES, 
        persons, 
        reference_date
    )

    # Send Telegram messages to each user
    for person, chores_list in assignment_map.items():
        if chores_list:
            chores_text = "\n".join([f"- {chore.name}" for chore in chores_list])
            message_text = (
                f"Доброе утро, {person.name}!\n"
                f"Вот твой список дел на {reference_date}:\n{chores_text}"
            )
        else:
            message_text = (
                f"Доброе утро, {person.name}!\n"
                f"Сегодня у тебя нет дел {reference_date}.\nРасслабляйся!"
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
    3. Schedule daily job to notify chores
    4. Start polling
    """
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )

    application = Application.builder().token(
        EnvVars().TELEGRAM_BOT_TOKEN
    ).build()

    start_handler = CommandHandler("start", start_command)

    application.add_handler(start_handler)

    job_queue = application.job_queue
    job_queue.run_daily(
        notify_chores,
        time=datetime.time(hour=2, minute=0, second=0, tzinfo=datetime.timezone.utc),
        name="daily_chore_notification"
    )

    application.run_polling()
