import logging
from datetime import timedelta, timezone, time
from logic.chore_distribution import  split_list_to_groups
from telegram import BotCommand, Update
from clients.db_client import  Chore, Person, DBClient
from enums.complexity import Complexity
from enums.frequency import Frequency
from telegram.ext import Application, CommandHandler, ContextTypes


class TgBotClient:
    def __init__(self, token: str, db_url: str):
        self.db_client = DBClient(db_url)  # Initialize the database client

        self._log = logging.getLogger(self.__class__.__name__)

        self._bot: Application = Application.builder().token(token).build()
        self._set_commands(self._bot)
        self._set_job_queue(self._bot)

    def _set_commands(self, application: Application) -> None:
        self._log.info("Setting commands...")
        commands = [
            {"command": "start", "description": "Стартовое сообщение бота", "callback": self._start_command},
            {"command": "message", "description": "Отправить сообщение пользователю", "callback": self._message_command},
            {"command": "assign_tasks", "description": "Распределить задачи между людьми", "callback": self.assign_tasks_command},
            {"command": "add_person", "description": "Добавить или зассал", "callback": self.add_person_command},
            {"command": "add_chore", "description": "Какой срач убирать", "callback": self.add_chore_command},


        ]
        for cmd in commands:
            application.add_handler(handler=CommandHandler(command=cmd["command"], callback=cmd["callback"]))
        application.bot.set_my_commands([BotCommand(cmd["command"], cmd["description"]) for cmd in commands])

    def _set_job_queue(self, application: Application) -> None:
        self._log.info("Setting job queue...")
        if not application.job_queue:
            self._log.error("Job queue not found in bot. Exiting.")
            return

        jobs = [
            {"name": "notify_chores_daily", "callback": self._notify_chores_daily, "interval": timedelta(days=1), "first": time(hour=18, minute=6,tzinfo=timezone.utc)},
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
            self._chat_id = update.effective_chat.id
            await update.message.reply_text(
                text="Привет! Я бот Антисрач. Расскажу, что делать, чтобы не зарасти говной."
            )
                
    async def add_chore_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message or len(context.args) < 3:
            await update.message.reply_text("Usage: /add_chore <name> <complexity> <frequency>")
            return
        try:
            name = context.args[0]
            complexity = Complexity[context.args[1].upper()]
            frequency = Frequency[context.args[2].upper()]
            tg_group_id = str(update.message.chat_id)
            chore = Chore(tg_group_id=tg_group_id, name=name, complexity=complexity, frequency=frequency)
            self.db_client.add_chore(chore)
            await update.message.reply_text(f"Chore '{name}' added to group {tg_group_id}.")
        except KeyError:
            await update.message.reply_text("Invalid complexity or frequency. Use /add_chore <name> <complexity> <frequency>")

        
    async def add_person_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message or len(context.args) < 1:
            await update.message.reply_text("Usage: /add_person <tg_user_id>")
            return
        tg_user_id = context.args[0]
        tg_group_id = str(update.message.chat_id)  # Get group ID from chat
        person = Person(tg_user_id=tg_user_id, tg_group_id=tg_group_id)
        self.db_client.add_person(person)
        await update.message.reply_text(f"Person with TG user ID {tg_user_id} added to group {tg_group_id}.")

        
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
        await context.bot.send_message(
            chat_id=self._chat_id,
            text="Доброе утро! Напоминаю, что сегодня нужно сделать следующие дела: ..."
        )
        
    async def assign_tasks_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        tg_group_id = str(update.message.chat_id)
        persons = self.db_client.get_persons_by_tg_group_id(tg_group_id)
        chores = self.db_client.get_chores_by_tg_group_id(tg_group_id)

        if not persons or not chores:
            await update.message.reply_text("No persons or chores available. Add them first!")
            return

        # Call your existing logic to assign chores to persons
        assignment = split_list_to_groups(chores, persons)

        message = "Task Assignments:\n"
        for group in assignment:
            person = group['person']
            tasks = ", ".join([task['name'] for task in group['tasks']])
            message += f"👤 {person.tg_user_id}: {tasks}\n"
        
        await update.message.reply_text(message)

        

    def run(self):
        self._log.info("Starting bot polling...")
        self._bot.run_polling()
