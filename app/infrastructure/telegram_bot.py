import datetime
import logging

from telegram import Update
from telegram.ext import Updater, ContextTypes, Application, CommandHandler, MessageHandler, ConversationHandler, CallbackContext
from config.env_vars import EnvVars
from telegram.ext import filters
from domain.models import Chore, Person
from domain.services import ChoreDistributionService
from use_cases.assign_chores import AssignChoresUseCase
from app.database import SessionManager


def get_person_by_telegram_id(session, telegram_id: int) -> Person:
    return session.query(Person).filter_by(telegram_id=telegram_id).first()


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
    reference_date = datetime.date.today()

    with SessionManager() as session:
        persons = session.query(Person).all()
        chores = session.query(Chore).all()

    assignment_map = assign_chores_use_case.execute(chores, persons, reference_date)

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
            
NAME, FREQUENCY, COMPLEXITY = range(3)

def start_chores(update: Update, context: CallbackContext) -> int:
    """
    Initiates the chore creation process by asking for the name of the chore.
    """
    update.message.reply_text("Please enter the name of the chore:")
    return NAME

def get_name(update: Update, context: CallbackContext) -> int:
    """
    Captures the name of the chore and stores it in context for later use.
    """
    context.user_data['chore_name'] = update.message.text
    update.message.reply_text("Please enter the frequency of the chore (e.g., daily, weekly):")
    return FREQUENCY

def get_frequency(update: Update, context: CallbackContext) -> int:
    """
    Captures the frequency and stores it in context for later use.
    Validates the input against predefined frequency values.
    """
    frequency = update.message.text.lower()
    valid_frequencies = ['daily', 'weekly', 'monthly']  # Adjust this list as needed

    if frequency not in valid_frequencies:
        update.message.reply_text("Invalid frequency. Please enter 'daily', 'weekly', or 'monthly':")
        return FREQUENCY

    context.user_data['chore_frequency'] = frequency
    update.message.reply_text("Please enter the complexity of the chore (e.g., easy, medium, hard):")
    return COMPLEXITY

def get_complexity(update: Update, context: CallbackContext) -> int:
    """
    Captures the complexity and completes the chore creation process by storing the chore in the database.
    """
    complexity = update.message.text.lower()
    valid_complexities = ['easy', 'medium', 'hard']  # Adjust this list as needed

    if complexity not in valid_complexities:
        update.message.reply_text("Invalid complexity. Please enter 'easy', 'medium', or 'hard':")
        return COMPLEXITY

    context.user_data['chore_complexity'] = complexity

    # Store the chore in the database
    with SessionManager() as session:
        new_chore = Chore(
            name=context.user_data['chore_name'],
            frequency=context.user_data['chore_frequency'],
            complexity=context.user_data['chore_complexity']
        )
        session.add(new_chore)
        session.commit()

    update.message.reply_text(f"Chore '{new_chore.name}' has been added successfully!")
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Chore addition cancelled.")
    return ConversationHandler.END

# Add handlers to the dispatcher
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('chores', start_chores)],
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        FREQUENCY: [MessageHandler(filters.Text & ~filters.COMMAND, get_frequency)],
        COMPLEXITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_complexity)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)

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

# Initialize bot and dispatcher
updater = Updater("7762089399:AAHPKdkefJFYo5lJcSiEY0F2KQU4FCRFwtk")
dispatcher = updater.dispatcher

# Define your conversation handler here
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('chores', start_chores)],
    states={
        NAME: [MessageHandler(Filters.text & ~Filters.command, get_name)],
        FREQUENCY: [MessageHandler(Filters.text & ~Filters.command, get_frequency)],
        COMPLEXITY: [MessageHandler(Filters.text & ~Filters.command, get_complexity)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)

# Add the conversation handler to the dispatcher
dispatcher.add_handler(conv_handler)

# Start the bot
updater.start_polling()
updater.idle()
