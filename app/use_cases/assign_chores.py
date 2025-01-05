import datetime
from typing import Dict, List
from app.domain.models import Chore, Person
from app.domain.services import ChoreDistributionService


class AssignChoresUseCase:
    """
    A use case that orchestrates:
    - figuring out today's chores
    - distributing them among persons
    """

    def __init__(self, distribution_service: ChoreDistributionService) -> None:
        self.distribution_service = distribution_service

    def execute(
        self, 
        chores: List[Chore], 
        persons: List[Person], 
        reference_date: datetime.date
    ) -> Dict[Person, List[Chore]]:
        chores_due_today = self.distribution_service.get_chores_due_today(chores, reference_date)
        assignment_map = self.distribution_service.distribute_chores(chores_due_today, persons)
        return assignment_map
