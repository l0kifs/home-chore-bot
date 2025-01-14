import logging
from typing import List

import sqlalchemy
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from enums.complexity import Complexity
from enums.frequency import Frequency
from models.chore import Chore as chore_model
from models.person import Person as person_model


Base = declarative_base()


class Person(Base):
    __tablename__ = 'persons'
    id = Column(Integer, primary_key=True)
    tg_user_id = Column(String, unique=True, nullable=False)
    tg_group_id = Column(String, unique=False, nullable=False)

    def to_model(self) -> person_model:
        return person_model(
            tg_user_id=str(self.tg_user_id),
            tg_group_id=str(self.tg_group_id)
        )


class Chore(Base):
    __tablename__ = 'chores'
    id = Column(Integer, primary_key=True)
    tg_group_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    complexity = Column(sqlalchemy.Enum(Complexity), nullable=False)
    frequency = Column(sqlalchemy.Enum(Frequency), nullable=False)

    def to_model(self) -> chore_model:
        return chore_model(
            tg_group_id=str(self.tg_group_id),
            name=str(self.name),
            complexity=Complexity(self.complexity).value,
            frequency=Frequency(self.frequency).value
        )


class DBClient:
    def __init__(
        self,
        db_url: str,
    ) -> None:
        self._log = logging.getLogger(self.__class__.__name__)
        self._engine = create_engine(url=db_url, echo=False)
        Base.metadata.create_all(self._engine)
        self._sessionmaker = sessionmaker(bind=self._engine)
    
    def add_person(
        self,
        person: Person
    ) -> None:
        with self._sessionmaker() as session:
            session.add(person)
            session.commit()

    def get_person_by_tg_user_id(
        self,
        tg_user_id: str
    ) -> Person:
        with self._sessionmaker() as session:
            return session.query(Person).filter_by(tg_user_id=tg_user_id).first()
    
    def get_persons_by_tg_group_id(
        self,
        tg_group_id: str
    ) -> List[Person]:
        with self._sessionmaker() as session:
            return session.query(Person).filter_by(tg_group_id=tg_group_id).all()
        
    def delete_person_by_tg_user_id(
        self,
        tg_user_id: str
    ) -> None:
        with self._sessionmaker() as session:
            session.query(Person).filter_by(tg_user_id=tg_user_id).delete()
            session.commit()
    
    def add_chore(
        self,
        chore: Chore
    ) -> None:
        with self._sessionmaker() as session:
            session.add(chore)
            session.commit()
    
    def get_chores_by_tg_group_id(
        self,
        tg_group_id: str
    ) -> List[Chore]:
        with self._sessionmaker() as session:
            return session.query(Chore).filter_by(tg_group_id=tg_group_id).all()
        
    def update_chore_by_id(
        self,
        chore_id: int,
        name: str | None = None,
        complexity: Complexity | None = None,
        frequency: Frequency | None = None
    ) -> None:
        with self._sessionmaker() as session:
            chore = session.query(Chore).filter_by(id=chore_id).first()
            if name:
                chore.name = name  # type: ignore
            if complexity:
                chore.complexity = complexity  # type: ignore
            if frequency:
                chore.frequency = frequency  # type: ignore
            session.commit()
    
    def delete_chore_by_id(
        self,
        chore_id: int
    ) -> None:
        with self._sessionmaker() as session:
            session.query(Chore).filter_by(id=chore_id).delete()
            session.commit()


# Usage test:
# import os
# data_dir_path = os.path.join(os.path.dirname(__file__), '..', 'data')
# db_client = DBClient(f'sqlite:///{data_dir_path}/home_chore_bot.db')
# db_client.add_person(Person(tg_user_id='111', tg_group_id='g1'))
# db_client.add_person(Person(tg_user_id='222', tg_group_id='g1'))

# db_client.add_chore(Chore(tg_group_id='g1', name='Wash Dishes', complexity=Complexity.EASY, frequency=Frequency.DAILY))
# db_client.add_chore(Chore(tg_group_id='g1', name='Clean Bathroom', complexity=Complexity.HARD, frequency=Frequency.WEEKLY))

# person = Person(tg_user_id='111', tg_group_id='g1')
# print(person.to_model())
# chore = Chore(tg_group_id='g1', name='Wash Dishes', complexity=Complexity.EASY, frequency=Frequency.DAILY)
# print(chore.to_model())