import datetime
from app.domain.models import Chore, Person, Frequency
from app.domain.services import ChoreDistributionService


def test_get_chores_due_today():
    service = ChoreDistributionService()
    chores = [
        Chore(name="Wash Dishes", frequency=Frequency.DAILY, complexity=1),
        Chore(name="Do Laundry", frequency=Frequency.WEEKLY, complexity=3),
    ]
    reference_date = datetime.date(2023, 1, 7)  # Day 7 of the year
    due_chores = service.get_chores_due_today(chores, reference_date)
    assert len(due_chores) == 2
    assert any(chore.name == "Wash Dishes" for chore in due_chores)
    assert any(chore.name == "Do Laundry" for chore in due_chores)


def test_distribute_chores():
    service = ChoreDistributionService()
    persons = [
        Person(telegram_id=123, name="Alice"),
        Person(telegram_id=456, name="Bob"),
    ]
    chores = [
        Chore(name="Wash Dishes", frequency=Frequency.DAILY, complexity=1),
        Chore(name="Do Laundry", frequency=Frequency.WEEKLY, complexity=3),
    ]
    assignments = service.distribute_chores(chores, persons)

    # Ensure all chores are assigned
    assigned_chores = sum(len(chores) for chores in assignments.values())
    assert assigned_chores == len(chores)

    # Ensure assignment alternates if possible
    assert len(assignments[persons[0]]) > 0
    assert len(assignments[persons[1]]) > 0
