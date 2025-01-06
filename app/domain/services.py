import datetime
from typing import Dict, List

from domain.models import Chore, Person


class ChoreDistributionService:
    """
    Responsible for distributing chores between persons based on:
    - Which chores are due today
    - Complexity/time consumption
    - Prior history so that the same person does not do the same task every time
    """

    def __init__(self) -> None:
        # For demonstration, we keep a simple in-memory assignment history
        # Key: chore name, Value: last Person assigned
        self.last_assigned: Dict[str, Person] = {}

    def get_chores_due_today(self, chores: List[Chore], reference_date: datetime.date) -> List[Chore]:
        """
        Given a list of chores and today's date, return which chores are due.
        This is a basic demonstration that checks 'day of year' mod frequency value.
        """
        chores_due = []
        day_of_year = reference_date.timetuple().tm_yday

        for chore in chores:
            # If day_of_year % chore.frequency.value == 0 => chore is due
            if (day_of_year % chore.frequency.value) == 0:
                chores_due.append(chore)

        return chores_due

    def distribute_chores(
        self, 
        chores_due: List[Chore], 
        persons: List[Person]
    ) -> Dict[Person, List[Chore]]:
        """
        Distribute chores due among the persons in a balanced way.

        Strategy:
        1. Sort chores by complexity descending (assign tough chores first).
        2. Try to alternate who does a chore if it was assigned recently to someone else.
        3. Keep track of total complexity assigned to each person to keep it balanced.
        """
        # Initialize result structure
        assignment_map: Dict[Person, List[Chore]] = {p: [] for p in persons}
        complexity_map: Dict[Person, int] = {p: 0 for p in persons}

        # Sort chores by complexity so we assign the hardest chores first
        chores_due_sorted = sorted(chores_due, key=lambda c: c.complexity, reverse=True)

        for chore in chores_due_sorted:
            # If the chore was done by Person X last time, try to assign to the other
            last_person = self.last_assigned.get(chore.name, None)

            # Among persons, pick the one with the least total complexity so far,
            # but also prefer to alternate from the last assignment.
            # This is a naive approach; you can refine if needed.
            best_person = min(persons, key=lambda p: complexity_map[p])

            # If we have a last assignment, try to pick a different person
            if last_person is not None:
                # among persons, pick the "other" one if feasible
                alt_persons = [p for p in persons if p != last_person]
                if alt_persons:
                    # pick the alt person with the least complexity
                    alt_person = min(alt_persons, key=lambda p: complexity_map[p])
                    # if alt_person is indeed more balanced, reassign best_person
                    if complexity_map[alt_person] < complexity_map[best_person]:
                        best_person = alt_person

            # Assign chore
            assignment_map[best_person].append(chore)
            complexity_map[best_person] += chore.complexity
            self.last_assigned[chore.name] = best_person

        return assignment_map