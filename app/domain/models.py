# Importing necessary tools for database magic and Enum handling
from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum as PyEnum


# This is our special "base" class for all database tables. 
Base = declarative_base()

# This is an Enum (like a choice list) to define how often chores need to be done. 
class Frequency(PyEnum):
    DAILY = 1
    EVERY_3_DAYS = 3
    WEEKLY = 7
    MONTHLY = 30
    EVERY_2_MONTHS = 60

# Here comes the "Chore" table! This is where every chore lives.
# We define this table with columns to store all the details about chores.
class Chore(Base):
    # The table is called 'chores'. In the database, it'll store the chore data.
    __tablename__ = "chores"
    
    # 'id' is the unique identifier for each chore. It's an auto-incrementing integer.
    id = Column(Integer, primary_key=True, autoincrement=True)   
    name = Column(String, nullable=False)
    
    # 'frequency' is linked to our 'Frequency' Enum to define how often this chore repeats.
    frequency = Column(Enum(Frequency), nullable=False)
    complexity = Column(Integer, nullable=False)

# Now we have a "Person" table. This stores details about the people who will be assigned chores.
class Person(Base):
    __tablename__ = "persons"
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 'telegram_id' is a unique ID for each person (since our bot needs to know who is who).
    telegram_id = Column(Integer, unique=True, nullable=False)
    name = Column(String, nullable=False)