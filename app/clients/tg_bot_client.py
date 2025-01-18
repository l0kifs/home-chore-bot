import logging
from telegram import BotCommand, Update
from telegram.ext import Application, CommandHandler, ContextTypes


class TgBotClient:
    def __init__(self, token: str):
        self._log = logging.getLogger(self.__class__.__name__)

        self._bot = Application.builder().token(token).build()
        self._bot.add_handler(CommandHandler("start", self._start_command))
        self._bot.add_handler(CommandHandler("message", self._message_command))
        self._bot.post_init = self._set_cmd_descriptions

    async def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat or not update.message:
            return
        if update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text(
                text="Привет! Я бот Антисрач. Расскажу, что делать, чтобы не зарасти говной."
            )

    async def _message_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.effective_chat or not update.message or not update.effective_user:
            return
        if update.effective_chat.type in ['group', 'supergroup']:
            user = update.effective_user
            await update.message.reply_text(f'{user.username} использовал команду /message')

    async def _set_cmd_descriptions(self, application: Application) -> None:
        commands = [
            BotCommand("start", "Стартовое сообщение бота"),
            BotCommand("message", "Отправить сообщение пользователю"),
        ]
        await application.bot.set_my_commands(commands)

    def run(self):
        self._bot.run_polling()
