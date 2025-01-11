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