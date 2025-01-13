from enum import Enum
import logging
from typing import List

from sqlalchemy import Column, Integer, String, create_engine
import sqlalchemy
from sqlalchemy.orm import sessionmaker, declarative_base


Base = declarative_base()


class Frequency(Enum):
    DAILY = 1
    EVERY_3_DAYS = 3
    WEEKLY = 7
    MONTHLY = 30
    EVERY_2_MONTHS = 60


class Complexity(Enum):
    EASIEST = 1
    EASY = 2
    MEDIUM = 3
    HARD = 4
    HARDEST = 5


class Person(Base):
    __tablename__ = 'persons'
    id = Column(Integer, primary_key=True)
    tg_user_id = Column(String, unique=True, nullable=False)
    tg_group_id = Column(String, unique=False, nullable=False)


class Chore(Base):
    __tablename__ = 'chores'
    id = Column(Integer, primary_key=True)
    tg_group_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    complexity = Column(sqlalchemy.Enum(Complexity), nullable=False)
    frequency = Column(sqlalchemy.Enum(Frequency), nullable=False)


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
