import logging
from typing import List

import sqlalchemy
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from enums.complexity import Complexity
from enums.frequency import Frequency

Base = declarative_base()


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
    
    # def add_person(
    #     self,
    #     person: Person
    # ) -> None:
    #     self._log.info("Adding person")
    #     with self._sessionmaker() as session:
    #         session.add(person)
    #         session.commit()
    
    def add_person(self, person: Person):
        session = self._sessionmaker()
        try:
            session.add(person)
            session.commit()
        except sqlalchemy.exc.IntegrityError:
            self._log.warning(f"User {person.tg_user_id} is already in the database.")
            session.rollback()
        finally:
            session.close()
            
    def get_person_by_tg_user_id(
        self,
        tg_user_id: str
    ) -> Person:
        self._log.info("Getting person by tg_user_id")
        with self._sessionmaker() as session:
            return session.query(Person).filter_by(tg_user_id=tg_user_id).first()
    
    def get_persons_by_tg_group_id(
        self,
        tg_group_id: str
    ) -> List[Person]:
        self._log.info("Getting persons by tg_group_id")
        with self._sessionmaker() as session:
            return session.query(Person).filter_by(tg_group_id=tg_group_id).all()
    
    # def get_person_by_user_and_group(self, tg_user_id: str, tg_group_id: str) -> Person:
    #     session = self.Session()
    #     try:
    #         return session.query(Person).filter_by(tg_user_id=tg_user_id, tg_group_id=tg_group_id).first()
    #     finally:
    #         session.close()
            
            
    def get_person_by_user_and_group(self, tg_user_id: str, tg_group_id: str):
        try:
            with self._sessionmaker() as session:
                return session.query(Person).filter_by(tg_user_id=tg_user_id, tg_group_id=tg_group_id).first()
        except Exception as e:
            print(f"Error in get_person_by_user_and_group: {e}")
            raise
        
    def delete_person_by_tg_user_id(
        self,
        tg_user_id: str
    ) -> None:
        self._log.info("Deleting person by tg_user_id")
        with self._sessionmaker() as session:
            session.query(Person).filter_by(tg_user_id=tg_user_id).delete()
            session.commit()
    
    def add_chore(
        self,
        chore: Chore
    ) -> None:
        self._log.info("Adding chore")
        with self._sessionmaker() as session:
            session.add(chore)
            session.commit()
    
    def get_chores_by_tg_group_id(
        self,
        tg_group_id: str
    ) -> List[Chore]:
        self._log.info("Getting chores by tg_group_id")
        with self._sessionmaker() as session:
            return session.query(Chore).filter_by(tg_group_id=tg_group_id).all()
        
    def update_chore_by_id(
        self,
        chore_id: int,
        name: str | None = None,
        complexity: Complexity | None = None,
        frequency: Frequency | None = None
    ) -> None:
        self._log.info("Updating chore by id")
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
        self._log.info("Deleting chore by id")
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