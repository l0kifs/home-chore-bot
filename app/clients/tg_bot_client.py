import logging
from datetime import timedelta, timezone, time

from telegram import BotCommand, Update
from telegram.ext import Application, CommandHandler, ContextTypes


class TgBotClient:
    def __init__(self, token: str):
        self._log = logging.getLogger(self.__class__.__name__)

        self._bot: Application = Application.builder().token(token).build()
        self._set_commands(self._bot)
        self._set_job_queue(self._bot)
        self._chat_id = None

    def _set_commands(self, application: Application) -> None:
        commands = [
            {"command": "start", "description": "Стартовое сообщение бота", "callback": self._start_command},
            {"command": "message", "description": "Отправить сообщение пользователю", "callback": self._message_command},
        ]
        for cmd in commands:
            application.add_handler(handler=CommandHandler(command=cmd["command"], callback=cmd["callback"]))
        application.bot.set_my_commands([BotCommand(cmd["command"], cmd["description"]) for cmd in commands])

    def _set_job_queue(self, application: Application) -> None:
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
        if not update.effective_chat or not update.message:
            return
        if update.effective_chat.type in ['group', 'supergroup']:
            self._chat_id = update.effective_chat.id
            await update.message.reply_text(
                text="Привет! Я бот Антисрач. Расскажу, что делать, чтобы не зарасти говной."
            )

    async def _message_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.effective_chat or not update.message or not update.effective_user:
            return
        if update.effective_chat.type in ['group', 'supergroup']:
            user = update.effective_user
            await update.message.reply_text(f'{user.username} использовал команду /message')

    async def _notify_chores_daily(self, context: ContextTypes.DEFAULT_TYPE):
        if not self._chat_id:
            self._log.error("Job context not found.")
            return
        await context.bot.send_message(
            chat_id=self._chat_id,
            text="Доброе утро! Напоминаю, что сегодня нужно сделать следующие дела: ..."
        )

    def run(self):
        self._bot.run_polling()
