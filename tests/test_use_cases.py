import datetime
from app.domain.models import Chore, Person, Frequency
from app.domain.services import ChoreDistributionService
from app.use_cases.assign_chores import AssignChoresUseCase


def test_assign_chores_use_case():
    service = ChoreDistributionService()
    use_case = AssignChoresUseCase(distribution_service=service)

    chores = [
        Chore(name="Wash Dishes", frequency=Frequency.DAILY, complexity=1),
        Chore(name="Do Laundry", frequency=Frequency.WEEKLY, complexity=3),
    ]
    persons = [
        Person(telegram_id=123, name="Alice"),
        Person(telegram_id=456, name="Bob"),
    ]
    reference_date = datetime.date(2023, 1, 7)

    assignments = use_case.execute(chores, persons, reference_date)

    # Ensure the assignment has keys for both persons
    assert set(assignments.keys()) == set(persons)

    # Ensure the total assigned chores match the due chores
    total_assigned = sum(len(chores) for chores in assignments.values())
    due_chores = len(service.get_chores_due_today(chores, reference_date))
    assert total_assigned == due_chores
