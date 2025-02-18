import logging
from datetime import timedelta, timezone, time
from logic.chore_distribution import  split_list_to_groups
from telegram import BotCommand, Update, InlineKeyboardButton, InlineKeyboardMarkup
from clients.db_client import  Chore, Person, DBClient
from enums.complexity import Complexity
from enums.frequency import Frequency
from telegram.ext import Application, CommandHandler, ContextTypes, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
from logic.assing_by_date import ChoreDistributionService


ASK_NAME, ASK_COMPLEXITY, ASK_FREQUENCY, ASK_START_DATE = range(4)

class TgBotClient:
    def __init__(self, token: str, db_url: str):
        self.db_client = DBClient(db_url)  # Initialize the database client

        self._log = logging.getLogger(self.__class__.__name__)
        
        self.chore_service = ChoreDistributionService()  # Добавляем этот атрибут
        self._bot: Application = Application.builder().token(token).build()
        self._set_commands(self._bot)
        self._set_job_queue(self._bot)
        self._chat_id = None  # Initialize _chat_id here

    
    def set_chat_id(self, chat_id: int) -> None:
        self._chat_id = chat_id
        self._log.info(f"Chat ID set to {self._chat_id}")

    def _set_commands(self, application: Application) -> None:
        # Add standalone command handlers

        self._log.info("Setting standalone commands...")
        commands = [
            {"command": "start", "description": "Стартовое сообщение бота", "callback": self._start_command},
            {"command": "message", "description": "Отправить сообщение пользователю", "callback": self._message_command},
            {"command": "assign_tasks", "description": "Распределить задачи между людьми", "callback": self.assign_tasks_command},
            # {"command": "add_person", "description": "Добавить или зассал", "callback": self.add_person_command},
        ]

        for cmd in commands:
            application.add_handler(handler=CommandHandler(command=cmd["command"], callback=cmd["callback"]))

        # Set bot commands
        application.bot.set_my_commands([BotCommand(cmd["command"], cmd["description"]) for cmd in commands])


        # Add conversation handler for 'add_chore' command
        self._log.info("Setting conversation handler for 'add_chore'...")
        conversation_handler = ConversationHandler(
            entry_points=[CommandHandler("add_chore", self.start_add_chore)],
            states={
                ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.ask_complexity)],
                ASK_COMPLEXITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.ask_frequency)],
                ASK_FREQUENCY: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.save_chore)],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
        )
        application.add_handler(conversation_handler)
        application.add_handler(MessageHandler(filters.ALL, self.add_person_on_interaction))


        self._log.info("All commands and handlers have been set.")

    def _set_job_queue(self, application: Application) -> None:
        self._log.info("Setting job queue...")
        if not application.job_queue:
            self._log.error("Job queue not found in bot. Exiting.")
            return

        jobs = [
            # {"name": "notify_chores_daily", "callback": self._notify_chores_daily, "interval": timedelta(days=1), "first": timedelta(seconds=5)}
            {"name": "notify_chores_daily", "callback": self._notify_chores_daily, "interval": timedelta(days=1), "first": time(hour=12, minute=15, tzinfo=timezone.utc)},
        ]
        for job in jobs:
            application.job_queue.run_repeating(
            callback=job["callback"], 
            interval=job["interval"],
            first=job["first"],
            name=job["name"]
        )

    async def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        
        self._log.info("Start command received.")
        
        if not update.effective_chat or not update.message:
            return
        if update.effective_chat.type in ['group', 'supergroup']:
            self.set_chat_id(update.effective_chat.id)  # Set chat_id here
            await update.message.reply_text(
                text="Привет! Я бот Антисрач. Расскажу, что делать, чтобы не зарасти говной."
            )
                
    async def start_add_chore(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("What's the name of the chore?")
        return ASK_NAME 
    
    async def ask_complexity(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data['chore_name'] = update.message.text
        keyboard = [
            ["Easiest", "Easy", "Medium", "Hard", "Hardest"]
        ]
        reply_markup = {"keyboard": keyboard, "one_time_keyboard": True, "resize_keyboard": True}
        await update.message.reply_text("Select the complexity:", reply_markup=reply_markup)
        return ASK_COMPLEXITY
    
    async def ask_frequency(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            complexity = Complexity[update.message.text.upper()]
            context.user_data['chore_complexity'] = complexity
            keyboard = [
                ["Daily", "Every 3 Days", "Weekly", "Monthly", "Every 2 Months"]
            ]
            reply_markup = {"keyboard": keyboard, "one_time_keyboard": True, "resize_keyboard": True}
            await update.message.reply_text("Select the frequency:", reply_markup=reply_markup)
            return ASK_FREQUENCY
        except KeyError:
            await update.message.reply_text("Invalid complexity. Please select from the provided options.")
            return ASK_COMPLEXITY

    async def save_chore(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            frequency = Frequency[update.message.text.upper().replace(" ", "_")]
            context.user_data['chore_frequency'] = frequency
            
            # Retrieve data from user_data
            name = context.user_data['chore_name']
            complexity = context.user_data['chore_complexity']
            tg_group_id = str(update.message.chat_id)

            # Save to the database
            chore = Chore(tg_group_id=tg_group_id, name=name, complexity=complexity, frequency=frequency)
            self.db_client.add_chore(chore)

            await update.message.reply_text(f"Chore '{name}' added successfully!")
            return ConversationHandler.END
        except KeyError:
            await update.message.reply_text("Invalid frequency. Please select from the provided options.")
            return ASK_FREQUENCY
        
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Chore addition cancelled.")
        return ConversationHandler.END

    def setup_conversation_handler(application: Application, db_client: DBClient):
        """Setup the conversation handler for adding a chore."""
        tg_bot_client = TgBotClient(token="YOUR_TOKEN", db_url="YOUR_DB_URL")
        tg_bot_client.db_client = db_client  # Inject database client
        
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("add_chore", tg_bot_client.start_add_chore)],
            states={
                ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, tg_bot_client.ask_complexity)],
                ASK_COMPLEXITY: [CallbackQueryHandler(tg_bot_client.ask_frequency)],
                ASK_FREQUENCY: [CallbackQueryHandler(tg_bot_client.save_chore)],
            },
            fallbacks=[CommandHandler("cancel", tg_bot_client.cancel)],
        )
        application.add_handler(conv_handler)
            
    async def add_person_on_interaction(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Log initial trigger
        self._log.info("Triggered add_person_on_interaction.")

        # Ensure the user and chat exist
        if not update.effective_user or not update.effective_chat:
            self._log.warning("No effective_user or effective_chat in update.")
            return

        # Extract user and group details
        tg_user_id = str(update.effective_user.id)  # User ID
        tg_group_id = str(update.effective_chat.id)  # Group ID
        self._log.info(f"User ID: {tg_user_id}, Group ID: {tg_group_id}")

        # Ensure it's a group or supergroup
        if update.effective_chat.type not in ["group", "supergroup"]:
            self._log.info(f"Skipping non-group chat: {update.effective_chat.type}")
            return

        # Check if the person is already in the database
        existing_person = self.db_client.get_person_by_user_and_group(tg_user_id, tg_group_id)
        if existing_person:
            self._log.info(f"User {tg_user_id} already exists in group {tg_group_id}. Skipping addition.")
            return

        # Add the person to the database
        person = Person(tg_user_id=tg_user_id, tg_group_id=tg_group_id)
        try:
            self.db_client.add_person(person)
            self._log.info(f"Successfully added user {tg_user_id} to group {tg_group_id}.")
        except Exception as e:
            self._log.error(f"Error adding user {tg_user_id} to group {tg_group_id}: {e}")


    async def _message_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        self._log.info("Message command received.")
        if not update.effective_chat or not update.message or not update.effective_user:
            return
        if update.effective_chat.type in ['group', 'supergroup']:
            user = update.effective_user
            await update.message.reply_text(f'{user.username} использовал команду /message')
    
    async def _notify_chores_daily(self, context: ContextTypes.DEFAULT_TYPE):
        self._log.info("Notify chores daily job started.")

        if not self._chat_id:
            self._log.error("Job context not found.")
            return

        tg_group_id = str(self._chat_id)
        persons = self.db_client.get_persons_by_tg_group_id(tg_group_id)
        all_chores = self.db_client.get_chores_by_tg_group_id(tg_group_id)

        if not persons or not all_chores:
            await context.bot.send_message(
                chat_id=self._chat_id,
                text="Сегодня нет назначенных дел. Добавьте задачи или участников!"
            )
            return

        # Фильтруем задачи на сегодня и распределяем их
        chores_due_today = self.chore_service.get_chores_due_today(all_chores)
        assignment = self.chore_service.assign_tasks(chores_due_today, persons)

        # Создаем сообщение
        message = "Доброе утро! Вот сегодняшние задачи:\n"
        for group in assignment:
            person = group['person']
            tasks = ", ".join([task['name'] for task in group['tasks']]) or "нет задач"
            message += f"👤 {person.tg_user_id}: {tasks}\n"

        # Отправляем уведомление
        await context.bot.send_message(chat_id=self._chat_id, text=message)
    
    # async def _notify_chores_daily(self, context: ContextTypes.DEFAULT_TYPE):
        
    #     self._log.debug(f"_chat_id: {self._chat_id}")
    #     self._log.debug(f"_ch at_id: {self._chat_id}")
    #     self._log.info("Notify chores daily job started.")
        

    #     if not self._chat_id:
    #         self._log.error("Job context not found.")
    #         return

    #     tg_group_id = str(self._chat_id)  # Assuming _chat_id is the Telegram group ID
    #     persons = self.db_client.get_persons_by_tg_group_id(tg_group_id)
    #     chores = self.db_client.get_chores_by_tg_group_id(tg_group_id)

    #     if not persons or not chores:
    #         await context.bot.send_message(
    #             chat_id=self._chat_id,
    #             text="Сегодня нет назначенных дел. Добавьте задачи или участников, чтобы начать!"
    #         )
    #         return

    #     # Assign tasks (reuse your existing logic or fetch assignments if stored)
    #     assignment = split_list_to_groups(chores, persons)

    #     # Create the notification message
    #     message = "Доброе утро! Вот сегодняшние задачи:\n"
    #     for group in assignment:
    #         person = group['person']
    #         tasks = ", ".join([task['name'] for task in group['tasks']])
    #         message += f"👤 {person.tg_user_id}: {tasks if tasks else 'нет задач'}\n"

    #     # Send the message
    #     await context.bot.send_message(chat_id=self._chat_id, text=message)

        
    async def assign_tasks_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        tg_group_id = str(update.message.chat_id)
        
        # Fetch persons and chores for the group
        persons = self.db_client.get_persons_by_tg_group_id(tg_group_id)
        chores = self.db_client.get_chores_by_tg_group_id(tg_group_id)

        if not persons:
            await update.message.reply_text("No persons available in this group. Add persons first!")
            return
        if not chores:
            await update.message.reply_text("No chores available in this group. Add chores first!")
            return

        # Prepare data for the assignment logic
        persons_data = [{"tg_user_id": person.tg_user_id, "id": person.id} for person in persons]
        chores_data = [
            {"name": chore.name, "complexity": chore.complexity.value, "id": chore.id}
            for chore in chores
        ]

        # Call the assignment logic
        assignment = split_list_to_groups(chores_data, persons_data)

        # Prepare and send the response message
        message = "Task Assignments:\n"
        for group in assignment:
            person = group["person"]
            tasks = ", ".join([task["name"] for task in group["tasks"]])
            message += f"👤 {person['tg_user_id']}: {tasks if tasks else 'No tasks assigned'}\n"
        
        await update.message.reply_text(message)
        
    def run(self):
        self._log.info("Starting bot polling...")
        self._bot.run_polling()
