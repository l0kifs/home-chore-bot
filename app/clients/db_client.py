# import logging
from datetime import UTC, datetime
from typing import List

from loguru import logger
import sqlalchemy
from sqlalchemy import Column, DateTime, Integer, String, create_engine, ForeignKey, Table, engine
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

from enums.complexity import Complexity
from enums.frequency import Frequency

Base = declarative_base()
# Base.metadata.create_all(engine, checkfirst=True)


person_group_table = Table(
    'person_group',
    Base.metadata,
    Column('person_id', Integer, ForeignKey('persons.id')),
    Column('group_id', Integer, ForeignKey('groups.id'))
)

class Person(Base):
    __tablename__ = "persons"
    
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)
    tg_user_id = Column(Integer, unique=True, nullable=False)

    person_groups = relationship("Group", secondary=person_group_table, back_populates="members")

class Group(Base):
    __tablename__ = "groups"  # Остается, но атрибут изменяем
    
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)
    name = Column(String, unique=True, nullable=False)
    invite_code = Column(String, unique=True)

    members = relationship("Person", secondary=person_group_table, back_populates="person_groups")


class Chore(Base):
    __tablename__ = 'chores'
    # service fields
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)
    # entry fields
    name = Column(String, nullable=False)
    complexity = Column(sqlalchemy.Enum(Complexity), nullable=False)
    frequency = Column(sqlalchemy.Enum(Frequency), nullable=False)


class DBClient:
    def __init__(
        self,
        db_url: str,
    ) -> None:
        logger.info("Initializing db client")
        self._engine = create_engine(url=db_url, echo=False)
        Base.metadata.create_all(self._engine)
        self._sessionmaker = sessionmaker(bind=self._engine)
    
    
    def add_person(self, person: Person):
        logger.info("Adding person")
        session = self._sessionmaker()
        try:
            session.add(person)
            session.commit()
        except sqlalchemy.exc.IntegrityError:
            logger.warning(f"User {person.tg_user_id} is already in the database.")
            session.rollback()
        finally:
            session.close()      
    
    def add_chore(
        self,
        chore: Chore
    ) -> None:
        logger.info("Adding chore")
        session = self._sessionmaker()
        try:
            session.add(chore)
            session.commit()
        except sqlalchemy.exc.IntegrityError:
            logger.warning(f"Chore {chore.name} is already in the database.")
            session.rollback()
        finally:
            session.close()
            
    def get_chore(
        self, 
        name: str
    ):
        logger.info("Getting chore")
        session = self._sessionmaker()
        try:
            chore = session.query(Chore).filter_by(name=name).first()
            return chore
        finally:
            session.close()
        
            
