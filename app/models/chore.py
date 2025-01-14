from dataclasses import dataclass


@dataclass
class Chore:
    tg_group_id: str
    name: str
    complexity: int
    frequency: int
