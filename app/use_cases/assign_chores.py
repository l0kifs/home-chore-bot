from typing import Dict, List
from domain.models import Chore, Person
from sqlalchemy.orm import Session
import datetime

class AssignChoresUseCase:
    def __init__(self, session):
        self.session = session

    def get_due_chores(self, reference_date):
        chores = self.session.query(Chore).all()
        # Logic to filter chores based on frequency, assuming 'daily' chores are due today
        due_chores = [chore for chore in chores if chore.frequency == 'daily']  # Example filter
        return due_chores

    def execute(self, due_chores, persons, reference_date):
        assignment_map = {}
        for i, person in enumerate(persons):
            # Round-robin assignment (or other logic)
            assigned_chores = [due_chores[i % len(due_chores)]]  # Assign chores in a round-robin manner
            assignment_map[person] = assigned_chores
        return assignment_map


# class AssignChoresUseCase:
#     def __init__(self, session: Session):
#         """
#         Initializes the use case with a database session.
#         """
#         self.session = session

#     def get_due_chores(self, reference_date: datetime.date) -> List[Chore]:
#         """
#         Retrieves chores that are due on the given reference date based on their frequency.
#         """
#         all_chores = self.session.query(Chore).all()
#         due_chores = []

#         for chore in all_chores:
#             if self.is_chore_due(chore, reference_date):
#                 due_chores.append(chore)

#         return due_chores

#     def is_chore_due(self, chore: Chore, reference_date: datetime.date) -> bool:
#         """
#         Determines if a chore is due based on its frequency and the reference date.
#         """
#         if chore.frequency == "daily":
#             return True
#         elif chore.frequency == "weekly":
#             return reference_date.weekday() == 0  # Example: Monday
#         elif chore.frequency == "monthly":
#             return reference_date.day == 1  # Example: First day of the month
#         return False

#     def execute(self, chores: List[Chore], persons: List[Person], reference_date: datetime.date) -> Dict[Person, List[Chore]]:
#         """
#         Assigns chores to persons in a round-robin fashion.
#         """
#         assignment_map = {person: [] for person in persons}

#         if not persons:
#             raise ValueError("No persons available for chore assignment.")

#         person_index = 0

#         for chore in chores:
#             assigned_person = persons[person_index]
#             assignment_map[assigned_person].append(chore)

#             # Move to the next person in a round-robin manner
#             person_index = (person_index + 1) % len(persons)

#         return assignment_map

# import datetime
# from typing import Dict, List
# from domain.models import Chore, Person
# from domain.services import ChoreDistributionService


# class AssignChoresUseCase:
#     """
#     A use case that orchestrates:
#     - figuring out today's chores
#     - distributing them among persons
#     """

#     def __init__(self, distribution_service: ChoreDistributionService) -> None:
#         self.distribution_service = distribution_service

#     def execute(
#         self, 
#         chores: List[Chore], 
#         persons: List[Person], 
#         reference_date: datetime.date
#     ) -> Dict[Person, List[Chore]]:
#         chores_due_today = self.distribution_service.get_chores_due_today(chores, reference_date)
#         assignment_map = self.distribution_service.distribute_chores(chores_due_today, persons)
#         return assignment_map
