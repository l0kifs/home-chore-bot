from telegram import Update
import logging
from telegram.ext import CommandHandler, MessageHandler, ConversationHandler, ContextTypes, filters
from database import SessionManager
from domain.models import Chore

# Constants for conversation states
NAME, FREQUENCY, COMPLEXITY = range(3)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    await update.message.reply_text("Привет! Я бот Антисрач. Готов помогать с делами!")
    logging.info(f"User started bot - ID: {user_id}, Username: {username}")

async def start_chores(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Enter the name of the chore:")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['chore_name'] = update.message.text
    await update.message.reply_text("Enter the frequency (daily, weekly, monthly):")
    return FREQUENCY

async def get_frequency(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    frequency = update.message.text.lower()
    valid_frequencies = ["daily", "weekly", "monthly"]

    if frequency not in valid_frequencies:
        await update.message.reply_text("Invalid frequency. Choose: daily, weekly, or monthly.")
        return FREQUENCY

    context.user_data['chore_frequency'] = frequency
    await update.message.reply_text("Enter complexity (easy, medium, hard):")
    return COMPLEXITY

async def get_complexity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    complexity = update.message.text.lower()
    valid_complexities = ["easy", "medium", "hard"]

    if complexity not in valid_complexities:
        await update.message.reply_text("Invalid complexity. Choose: easy, medium, or hard.")
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

        # Retrieve the saved chore
        added_chore = session.query(Chore).filter_by(name=new_chore.name).first()

    if added_chore:
        await update.message.reply_text(
            f"Chore added successfully! 🎉\n\n"
            f"**Name:** {added_chore.name}\n"
            f"**Frequency:** {added_chore.frequency}\n"
            f"**Complexity:** {added_chore.complexity}"
        )
    else:
        await update.message.reply_text("Error: Could not retrieve the chore from the database.")



    # Save chore in database and retrieve the details
    # with SessionManager() as session:
    #     new_chore = Chore(
    #         name=context.user_data['chore_name'],
    #         frequency=context.user_data['chore_frequency'],
    #         complexity=context.user_data['chore_complexity']
    #     )
    #     session.add(new_chore)
    #     session.commit()

    #     # Fetch the chore from the database to display its details
    #     added_chore = session.query(Chore).filter_by(id=new_chore.id).first()

    # # Send task details to the user
    # await update.message.reply_text(
    #     f"Chore added successfully! 🎉\n\n"
    #     f"**Name:** {added_chore.name}\n"
    #     f"**Frequency:** {added_chore.frequency}\n"
    #     f"**Complexity:** {added_chore.complexity}"
    # )
    # return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Chore addition cancelled.")
    return ConversationHandler.END

async def daily_chore_notification(context: ContextTypes.DEFAULT_TYPE):
    chat_ids = context.bot_data.get("TELEGRAM_CHAT_IDS", [])
    message = "Reminder: Time to do your daily chores!"
    for chat_id in chat_ids:
        await context.bot.send_message(chat_id=chat_id, text=message)

def setup_bot(application):
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))

    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("chores", start_chores)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            FREQUENCY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_frequency)],
            COMPLEXITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_complexity)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(conv_handler)


# import datetime
# import logging

# from telegram import Update
# from telegram.ext import Updater, ContextTypes, Application, CommandHandler, MessageHandler, ConversationHandler, CallbackContext
# from config.env_vars import EnvVars
# from telegram.ext import filters
# from domain.models import Chore, Person
# from database import SessionManager


# def get_person_by_telegram_id(session, telegram_id: int) -> Person:
#     return session.query(Person).filter_by(telegram_id=telegram_id).first()

# async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """
#     Handler for the /start command. 
#     Just a greeting message.
#     """
#     user_id = update.effective_user.id
#     username = update.effective_user.username

#     await update.message.reply_text(
#         text="Привет! Я бот Антисрач. Расскажу, что тебе делать, чтобы не зарасти говной."
#     )

#     print(f"User ID: {user_id}, Username: {username}")

# NAME, FREQUENCY, COMPLEXITY = range(3)

# def start_chores(update: Update, context: CallbackContext) -> int:
#     """
#     Initiates the chore creation process by asking for the name of the chore.
#     """
#     update.message.reply_text("Please enter the name of the chore:")
#     return NAME

# def get_name(update: Update, context: CallbackContext) -> int:
#     """
#     Captures the name of the chore and stores it in context for later use.
#     """
#     context.user_data['chore_name'] = update.message.text
#     update.message.reply_text("Please enter the frequency of the chore (e.g., daily, weekly):")
#     return FREQUENCY

# def get_frequency(update: Update, context: CallbackContext) -> int:
#     """
#     Captures the frequency and stores it in context for later use.
#     Validates the input against predefined frequency values.
#     """
#     frequency = update.message.text.lower()
#     valid_frequencies = ['daily', 'weekly', 'monthly']  # Adjust this list as needed

#     if frequency not in valid_frequencies:
#         update.message.reply_text("Invalid frequency. Please enter 'daily', 'weekly', or 'monthly':")
#         return FREQUENCY

#     context.user_data['chore_frequency'] = frequency
#     update.message.reply_text("Please enter the complexity of the chore (e.g., easy, medium, hard):")
#     return COMPLEXITY

# def get_complexity(update: Update, context: CallbackContext) -> int:
#     """
#     Captures the complexity and completes the chore creation process by storing the chore in the database.
#     """
#     complexity = update.message.text.lower()
#     valid_complexities = ['easy', 'medium', 'hard']  # Adjust this list as needed

#     if complexity not in valid_complexities:
#         update.message.reply_text("Invalid complexity. Please enter 'easy', 'medium', or 'hard':")
#         return COMPLEXITY

#     context.user_data['chore_complexity'] = complexity

#     # Store the chore in the database
#     with SessionManager() as session:
#         new_chore = Chore(
#             name=context.user_data['chore_name'],
#             frequency=context.user_data['chore_frequency'],
#             complexity=context.user_data['chore_complexity']
#         )
#         session.add(new_chore)
#         session.commit()

#     update.message.reply_text(f"Chore '{new_chore.name}' has been added successfully!")
#     return ConversationHandler.END

# def cancel(update: Update, context: CallbackContext) -> int:
#     update.message.reply_text("Chore addition cancelled.")
#     return ConversationHandler.END

# # Add handlers to the dispatcher
# conv_handler = ConversationHandler(
#     entry_points=[CommandHandler('chores', start_chores)],
#     states={
#         NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
#         FREQUENCY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_frequency)],
#         COMPLEXITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_complexity)],
#     },
#     fallbacks=[CommandHandler('cancel', cancel)],
# )

# def main() -> None:
#     """
#     Entrypoint: 
#     1. Build the telegram application
#     2. Register handlers
#     3. Schedule daily job to notify chores
#     4. Start polling
#     """
#     logging.basicConfig(
#         format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
#     )

#     application = Application.builder().token(
#         EnvVars().TELEGRAM_BOT_TOKEN
#     ).build()

#     start_handler = CommandHandler("start", start_command) 

#     application.add_handler(start_handler)
    
#     # Define your callback function that will be triggered daily
# async def daily_chore_notification(context: CallbackContext):
#     chat_ids = [int(chat_id) for chat_id in context.bot_data.get("TELEGRAM_CHAT_IDS", "").split(",")]
#     message = "Reminder: Time to do your daily chores!"
    
#     for chat_id in chat_ids:
#         await context.bot.send_message(chat_id=chat_id, text=message)

#     job_queue = application.job_queue
#     job_queue.run_daily(
#         time=datetime.time(hour=2, minute=0, second=0, tzinfo=datetime.timezone.utc),
#         name="daily_chore_notification"
#     )
#     logging.basicConfig(level=logging.DEBUG)


#     application.run_polling()
#     logging.basicConfig(level=logging.DEBUG)


# # Initialize bot and dispatcher
# application = Application.builder().token("8024964245:AAFmu0MNyXAnhf2N7-WHWUvShIJNJwPhVp0").build()
# # Define your conversation handler here
# conv_handler = ConversationHandler(
#     entry_points=[CommandHandler('chores', start_chores)],
#     states={
#         NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
#         FREQUENCY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_frequency)],
#         COMPLEXITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_complexity)],
#     },
#     fallbacks=[CommandHandler('cancel', cancel)],
# )
