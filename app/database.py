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