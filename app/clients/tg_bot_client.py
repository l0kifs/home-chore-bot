from datetime import timedelta, timezone, time

from loguru import logger
from telegram.ext import Application, CommandHandler, ContextTypes, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
from telegram import BotCommand, Update, InlineKeyboardButton, InlineKeyboardMarkup

from clients.db_client import  Chore, Person, DBClient
from enums.complexity import Complexity
from enums.frequency import Frequency
from logic.assing_by_date import ChoreDistributionService


class TgBotClient:
    def __init__(self, token: str, db_url: str):
        logger.info("Initializing bot client")
        self.db_client = DBClient(db_url)
        self.chore_service = ChoreDistributionService()

        self._bot: Application = (
            Application.builder()
            .token(token)
            .build()
        )

        self._bot.add_handler(CommandHandler("add_person", self.add_person_command))

    async def add_person_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.info("Received add_person command")
        if not update.effective_chat or not update.message or not update.message.from_user:
            return
        if update.effective_chat.type in ['group', 'supergroup']:
            chat_id = update.effective_chat.id
            user_id = update.message.from_user.id

            existing_person = self.db_client.get_person_by_user_and_group(
                tg_group_id=chat_id,
                tg_user_id=user_id
            )
            if existing_person:
                await update.message.reply_text(
                    text="Вы уже зарегистрированы в группе!"
                )
            else:
                new_person = Person(
                    tg_group_id=chat_id,
                    tg_user_id=user_id
                )
                self.db_client.add_person(new_person)
                await update.message.reply_text(
                    text="Вы успешно зарегистрированы в группе!"
                )

                await context.bot.send_message(
                    chat_id=update.message.from_user.id,
                    text="Привет! Я бот Антисрач. Расскажу, что делать, чтобы не зарасти говной."
                )

    def run(self):
        logger.info("Starting bot")
        self._bot.run_polling()
