from app.domain.models import Chore, Person, Frequency



def test_chore_creation():
    chore = Chore(name="Wash Dishes", frequency=Frequency.DAILY, complexity=2)
    assert chore.name == "Wash Dishes"
    assert chore.frequency == Frequency.DAILY
    assert chore.complexity == 2


def test_person_creation():
    person = Person(telegram_id=123456, name="Alice")
    assert person.telegram_id == 123456
    assert person.name == "Alice"
