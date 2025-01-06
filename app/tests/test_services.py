import datetime
import logging
from app.domain.models import Chore, Person, Frequency
from app.domain.services import ChoreDistributionService

logger = logging.getLogger(__name__)


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


def test_fairness_of_task_distribution():
    service = ChoreDistributionService()
    persons = [
        Person(telegram_id=123, name="Alice"),
        Person(telegram_id=456, name="Bob"),
    ]
    chores = [
        Chore(name="Wash Dishes", frequency=Frequency.DAILY, complexity=1),
        Chore(name="Do Laundry", frequency=Frequency.WEEKLY, complexity=3),
        Chore(name="Mop Floor", frequency=Frequency.EVERY_5_DAYS, complexity=2),
        Chore(name="Cook Dinner", frequency=Frequency.DAILY, complexity=4),
    ]
    reference_date = datetime.date(2023, 1, 7)  # Day 7 of the year

    # Simulate today's due chores
    due_chores = service.get_chores_due_today(chores, reference_date)

    # Distribute chores
    assignments = service.distribute_chores(due_chores, persons)

    # Calculate total complexity per person
    complexity_map = {
        person: sum(chore.complexity for chore in assigned_chores)
        for person, assigned_chores in assignments.items()
    }

    # Ensure all tasks are assigned
    assert sum(len(assigned) for assigned in assignments.values()) == len(due_chores)

    # Ensure complexity difference is minimal (fairness check)
    complexity_values = list(complexity_map.values())
    assert abs(complexity_values[0] - complexity_values[1]) <= 1, (
        f"Unfair distribution: {complexity_map}"
    )

    # Ensure task alternation (if possible)
    # If a task has been assigned to Alice today, it should ideally be assigned to Bob next time
    # (Mock past assignment if needed for additional checks)

    logger.info(f"Task assignment: {assignments}")
    logger.info(f"Complexity map: {complexity_map}")
