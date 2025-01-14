import datetime
from typing import Dict, List

from models.chore import Chore
from models.person import Person


class ChoreDistributionService:
    def __init__(self) -> None:
        pass

    def get_chores_due_today(
            self, 
            all_chores: List[Chore]
        ) -> List[Chore]:
        chores_due = []
        today_date = datetime.date.today()
        day_of_year = today_date.timetuple().tm_yday
        for chore in all_chores:
            if (day_of_year % chore.frequency) == 0:
                chores_due.append(chore)
        return chores_due
    
    # def distribute_chores(
    #         self, 
    #         chores: List[Chore], 
    #         persons: List[Person]
    #     ) -> Dict[Person, List[Chore]]:

    #     assignment_map: Dict[Person, List[Chore]] = {person: [] for person in persons}

    #     chores_sorted = sorted(chores, key=lambda c: c.complexity, reverse=True)

    #     for chore in chores_sorted:
    #         last_person = self.last_assigned.get(chore.name, None)

    #         # Among persons, pick the one with the least total complexity so far,
    #         # but also prefer to alternate from the last assignment.
    #         # This is a naive approach; you can refine if needed.
    #         best_person = min(persons, key=lambda p: complexity_map[p])

    #         # If we have a last assignment, try to pick a different person
    #         if last_person is not None:
    #             # among persons, pick the "other" one if feasible
    #             alt_persons = [p for p in persons if p != last_person]
    #             if alt_persons:
    #                 # pick the alt person with the least complexity
    #                 alt_person = min(alt_persons, key=lambda p: complexity_map[p])
    #                 # if alt_person is indeed more balanced, reassign best_person
    #                 if complexity_map[alt_person] < complexity_map[best_person]:
    #                     best_person = alt_person

    #         # Assign chore
    #         assignment_map[best_person].append(chore)
    #         complexity_map[best_person] += chore.complexity
    #         self.last_assigned[chore.name] = best_person

    #     return assignment_map