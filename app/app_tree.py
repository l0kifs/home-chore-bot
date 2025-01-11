app/
┣ config/
┃ ┣ env_vars.py
    from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvVars(BaseSettings):
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHAT_IDS: str

    model_config = SettingsConfigDict(env_file='.env')
┣ domain/
┃ ┣ models.py
from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum as PyEnum

Base = declarative_base()

class Frequency(PyEnum):
    DAILY = 1
    EVERY_3_DAYS = 3
    WEEKLY = 7
    MONTHLY = 30
    EVERY_2_MONTHS = 60

class Chore(Base):
    __tablename__ = "chores"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    frequency = Column(Enum(Frequency), nullable=False)
    complexity = Column(Integer, nullable=False)

class Person(Base):
    __tablename__ = "persons"
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    name = Column(String, nullable=False)
┃ ┣ services.py
from sqlalchemy.orm import Session
from domain.models import Chore, Person

class ChoreService:
    def add_person(self, db: Session, telegram_id: str, name: str):
        person = Person(telegram_id=telegram_id, name=name)
        db.add(person)
        db.commit()
        db.refresh(person)
        return person

    def add_chore(self, db: Session, name: str, frequency: str, complexity: int):
        chore = Chore(name=name, frequency=frequency, complexity=complexity)
        db.add(chore)
        db.commit()
        db.refresh(chore)
        return chore

    def get_all_persons(self, db: Session):
        return db.query(Person).all()

    def get_all_chores(self, db: Session):
        return db.query(Chore).all()
┣ infrastructure/
┃ ┣ telegram_bot.py
import datetime
import logging

from telegram import Update
from telegram.ext import Updater, ContextTypes, Application, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
from config.env_vars import EnvVars
from domain.models import Chore, Frequency, Person
from domain.services import ChoreDistributionService
from use_cases.assign_chores import AssignChoresUseCase
from app.database import add_chore, Session


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

# Define states for conversation
NAME, FREQUENCY, COMPLEXITY = range(3)

def start_chores(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Please enter the name of the chore:")
    return NAME

def get_name(update: Update, context: CallbackContext) -> int:
    context.user_data['chore_name'] = update.message.text
    update.message.reply_text("Please enter the frequency (daily, weekly, monthly):")
    return FREQUENCY

def get_frequency(update: Update, context: CallbackContext) -> int:
    freq = update.message.text.lower()
    if freq in ['daily', 'weekly', 'monthly']:
        context.user_data['chore_frequency'] = Frequency[freq.upper()]
        update.message.reply_text("Please enter the complexity (1-5):")
        return COMPLEXITY
    else:
        update.message.reply_text("Invalid frequency. Please enter 'daily', 'weekly', or 'monthly':")
        return FREQUENCY

def get_complexity(update: Update, context: CallbackContext) -> int:
    try:
        complexity = int(update.message.text)
        if 1 <= complexity <= 5:
            context.user_data['chore_complexity'] = complexity
            # Save to database
            session = Session()
            new_chore = Chore(
                name=context.user_data['chore_name'],
                frequency=context.user_data['chore_frequency'],
                complexity=context.user_data['chore_complexity']
            )
            add_chore(session, new_chore)
            update.message.reply_text(f"Chore '{new_chore.name}' added successfully!")
            return ConversationHandler.END
        else:
            update.message.reply_text("Complexity must be between 1 and 5. Please enter again:")
            return COMPLEXITY
    except ValueError:
        update.message.reply_text("Invalid input. Please enter a number between 1 and 5:")
        return COMPLEXITY

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Chore addition cancelled.")
    return ConversationHandler.END

# Add handlers to the dispatcher
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('chores', start_chores)],
    states={
        NAME: [MessageHandler(Filters.text & ~Filters.command, get_name)],
        FREQUENCY: [MessageHandler(Filters.text & ~Filters.command, get_frequency)],
        COMPLEXITY: [MessageHandler(Filters.text & ~Filters.command, get_complexity)],
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
┣ use_cases/
┃ ┣ __pycache__/
┃ ┣ assign_chores.py
import datetime
from typing import Dict, List
from domain.models import Chore, Person
from domain.services import ChoreDistributionService


class AssignChoresUseCase:
    """
    A use case that orchestrates:
    - figuring out today's chores
    - distributing them among persons
    """

    def __init__(self, distribution_service: ChoreDistributionService) -> None:
        self.distribution_service = distribution_service

    def execute(
        self, 
        chores: List[Chore], 
        persons: List[Person], 
        reference_date: datetime.date
    ) -> Dict[Person, List[Chore]]:
        chores_due_today = self.distribution_service.get_chores_due_today(chores, reference_date)
        assignment_map = self.distribution_service.distribute_chores(chores_due_today, persons)
        return assignment_map

┣ create_tables.py
from database import SessionManager
from domain.models import Chore, Person, Base

def init_db():
    # Access engine from SessionManager directly
    session_manager = SessionManager()
    Base.metadata.create_all(bind=session_manager.engine)

if __name__ == "__main__":
    init_db()

┣ database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from domain.models import Chore, Person, Base

engine = create_engine("sqlite:///C:/Users/Vika/Documents/home-chore-bot/chores.db")
Session = sessionmaker(bind=engine)

class SessionManager:
    def __init__(self):
        self.database_url = "sqlite:///C:/Users/Vika/Documents/home-chore-bot/chores.db"
        self.engine = create_engine(self.database_url, connect_args={"check_same_thread": False})
        self.session_maker = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def __enter__(self):
        self.session = self.session_maker()
        return self.session

    def __exit__(self, exc_type, exc_value, traceback):
        if self.session:
            self.session.close()

def add_person(session, person: Person):
    session.add(person)
    session.commit()

def add_chore(session, chore: Chore):
    session.add(chore)
    session.commit()
┣ main.py
from infrastructure.telegram_bot import main
from database import init_db

# This will create the tables in the database
init_db()

if __name__ == "__main__":
    main()
┣ requirements.txt
python-telegram-bot
python-telegram-bot[job-queue]
pydantic-settings

