from enum import Enum


class Frequency(Enum):
    DAILY = 1
    WEEKLY = 7
    EVERY_5_DAYS = 5
    # You can add more frequencies as needed, e.g. MONTHLY = 30, etc.

class Chore:
    """
    Represents a household chore.
    """
    def __init__(
        self, 
        name: str, 
        frequency: Frequency, 
        complexity: int
    ) -> None:
        """
        :param name: Name of the chore (e.g. 'Wash Dishes')
        :param frequency: How often the chore repeats
        :param complexity: A numeric indicator of chore's difficulty (e.g. 1=easy, 3=hard)
        """
        self.name = name
        self.frequency = frequency
        self.complexity = complexity

    def __repr__(self) -> str:
        return f"Chore(name={self.name}, frequency={self.frequency}, complexity={self.complexity})"


class Person:
    """
    Represents a person who has to do chores.
    """
    def __init__(self, telegram_id: int, name: str) -> None:
        self.telegram_id = telegram_id
        self.name = name

    def __repr__(self) -> str:
        return f"Person(name={self.name}, telegram_id={self.telegram_id})"