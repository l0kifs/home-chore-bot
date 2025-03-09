from datetime import timedelta, timezone, time

from loguru import logger
from telegram.ext import Application, CommandHandler, ContextTypes, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
from telegram import BotCommand, Update, InlineKeyboardButton, InlineKeyboardMarkup

from clients.db_client import  Chore, Person, DBClient
from enums.complexity import Complexity
from enums.frequency import Frequency
from logic.assing_by_date import ChoreDistributionService
import random
import string


def add_default_chores(db_client: DBClient):
    chores = [
        Chore(name="Вынести мусор", frequency=Frequency.EVERY_3_DAYS, complexity=Complexity.MEDIUM),
        Chore(name="Почистить зубы кошкам", frequency=Frequency.DAILY, complexity=Complexity.EASY),
        Chore(name="Убрать лотки", frequency=Frequency.DAILY, complexity=Complexity.MEDIUM),
        Chore(name="Сменить постельное белье", frequency=Frequency.WEEKLY, complexity=Complexity.HARD),
        Chore(name="Помыть робососа", frequency=Frequency.WEEKLY, complexity=Complexity.HARDEST),
        Chore(name="Помыть стекла", frequency=Frequency.EVERY_2_MONTHS, complexity=Complexity.HARDEST),
        Chore(name="Помыть холодильник", frequency=Frequency.WEEKLY, complexity=Complexity.HARDEST),
        Chore(name="Помыть душ", frequency=Frequency.WEEKLY, complexity=Complexity.HARD),
        Chore(name="Помыть унитаз", frequency=Frequency.WEEKLY, complexity=Complexity.EASY),
        Chore(name="Протереть поверхности на кухне", frequency=Frequency.EVERY_3_DAYS, complexity=Complexity.MEDIUM),
        Chore(name="Постирать вещи", frequency=Frequency.EVERY_3_DAYS, complexity=Complexity.MEDIUM),
        Chore(name="Собрать мусор", frequency=Frequency.DAILY, complexity=Complexity.EASY),
        Chore(name="Помыть посуду", frequency=Frequency.DAILY, complexity=Complexity.EASY), 
    ]   
    for chore in chores:
            if not db_client.get_chore(chore.name):  # Check if chore exists
                db_client.add_chore(chore)

class TgBotClient:
    def __init__(self, token: str, db_url: str):
        logger.info("Initializing bot client")
        self.db_client = DBClient(db_url)
        add_default_chores(self.db_client)
        self.chore_service = ChoreDistributionService()

        self._bot: Application = (
            Application.builder()
            .token(token)
            .post_init(self.post_init)
            .build()
        )
        self._set_commands(self._bot)  
        self._set_job_queue(self._bot)

        
    def _set_commands(self, application: Application) -> None:

        logger.info("Setting standalone commands...")
        
        application.add_handler(CommandHandler("add_chore", self.create_chore_command))
        application.add_handler(CommandHandler("invite", self.invite_command))
        application.add_handler(CommandHandler("start", self.start_command))
        
    async def post_init(self, application: Application) -> None:
        await application.bot.set_my_commands([
            BotCommand("add_chore", "Добавление задачи"),
            BotCommand("invite", "добвление челика"),
            BotCommand("start", "начало работы с ботом")
        ])
        
        chat_id = "624165496"

        try:
            await application.bot.send_message(chat_id=chat_id, text="Бот запущен и готов к работе!")
            logger.info("Startup message sent successfully.")
        except Exception as e:
            logger.error(f"Failed to send startup message: {e}")
       
    async def create_chore_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Method create chore"""
        logger.info('Start creating chore')

        if not context.args or len(context.args) < 3:
            await update.message.reply_text(
                "Используй формат: /add_chore <название> <сложность> <частота>\n"
                "Например: /add_chore Мыть_посуду 2 7"
            )
            return

        try:
            name = context.args[0]
            complexity = Complexity(int(context.args[1]))
            frequency = Frequency(int(context.args[2]))

            chore = Chore(name=name, complexity=complexity, frequency=frequency)
            self.db_client.add_chore(chore)

            await update.message.reply_text(f"Задача '{name}' добавлена!")
            logger.info(f"Chore '{name}' added successfully.")

        except ValueError:
            await update.message.reply_text("Ошибка! Сложность и частота должны быть числами из списка доступных значений.")
        except Exception as e:
            logger.error(f"Error adding chore: {e}")
            await update.message.reply_text("Произошла ошибка при добавлении задачи.")

    async def invite_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.message.from_user
        invite_code = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        
        invite_link = f"https://t.me/{context.bot.username}?start=addme_{invite_code}"

        await update.message.reply_text(
            f"🚀 Отправь эту ссылку другу: {invite_link}\n"
            "Когда он нажмёт, бот его зарегистрирует!"
        )

        logger.info(f"Generated invite link for {user.id}: {invite_link}")

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.message.from_user

        if context.args and context.args[0].startswith("addme_"):
            invite_code = context.args[0][6:]  
            logger.info(f"User {user.id} joined with invite code: {invite_code}")

        session = self.db_client._sessionmaker()
        existing_person = session.query(Person).filter_by(tg_user_id=user.id).first()
        session.close()

        if existing_person:
            await update.message.reply_text(f"Ты уже в системе, @{user.username}! 😉")
        else:
            person = Person(tg_user_id=user.id)
            self.db_client.add_person(person)
            await update.message.reply_text(f"✅ Ты успешно зарегистрирован в системе, @{user.username}!")

            logger.info(f"User {user.id} added to database.")
            
    def _set_job_queue(self, application: Application) -> None:
        """Настраивает автоматические задачи для бота."""
        logger.info("Setting job queue...")
        if not application.job_queue:
            logger.error("Job queue not found in bot. Exiting.")
            return

        application.job_queue.run_repeating(
            callback=self._notify_chores_daily, 
            interval=timedelta(days=1),
            first=time(hour=17, minute=54, tzinfo=timezone.utc),
            name="notify_chores_daily"
        )

    async def _notify_chores_daily(self, context: ContextTypes.DEFAULT_TYPE):
        """Распределяет и отправляет пользователям их задачи каждый день."""
        logger.info("Началась автоматическая рассылка задач.")

        session = self.db_client._sessionmaker()
        persons = session.query(Person).all()
        all_chores = session.query(Chore).all()
        session.close()

        if not persons or not all_chores:
            logger.warning("Нет пользователей или задач для распределения.")
            return

        chore_service = ChoreDistributionService()
        today_chores = chore_service.get_chores_due_today(all_chores)

        if not today_chores:
            logger.info("Сегодня нет задач для выполнения.")
            return

        tasks_by_person = chore_service.assign_tasks(today_chores, persons)

        for entry in tasks_by_person:
            person = entry["person"]
            tasks = entry["tasks"]

            try:
                chat = await context.bot.get_chat(person.tg_user_id)
                user_display_name = f"@{chat.username}" if chat.username else chat.first_name
            except Exception as e:
                logger.error(f"Не удалось получить имя пользователя {person.tg_user_id}: {e}")
                user_display_name = f"ID {person.tg_user_id}" 

            if tasks:
                task_list = "\n".join([f"- {task['name']} (Сложность: {task['complexity']})" for task in tasks])
                message = f"👋 {user_display_name}, вот твои задачи на сегодня:\n{task_list}"
            else:
                message = f"🎉 {user_display_name}, у тебя сегодня нет задач!"

            try:
                await context.bot.send_message(chat_id=person.tg_user_id, text=message)
                logger.info(f"Задачи отправлены {user_display_name}")
            except Exception as e:
                logger.error(f"Не удалось отправить сообщение {person.tg_user_id}: {e}")

    def run(self):
        logger.info("Starting bot")
        self._bot.run_polling()

# # В личных сообщениях с ботом можно добавлять задачи и редактировать, в общем чате будет приходить оповещение об изменениях в списке задач
