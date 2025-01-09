import pytest
from app.database import SessionManager, add_chore, add_person, Session
from app.domain.models import Person, Chore, Frequency

@pytest.fixture
def session():
    # Setup a session for testing (use a test database)
    return Session()

def test_add_person_and_chore(session):
    # Add a new person
    session.query(Person).delete()  # Clears existing data in the test database
    session.commit()
    session.query(Chore).delete()  # Clears existing data in the test database
    session.commit()

    new_person = Person(telegram_id=1234, name="Kleverochek")
    session.add(new_person)  # Corrected this line
    session.commit()
    # Add a new chore
    new_chore = Chore(name="Poop", frequency=Frequency.DAILY, complexity=5)
    session.add(new_chore)  # Corrected this line
    session.commit()

    # Assert that the person and chore were added
    persons = session.query(Person).all()
    chores = session.query(Chore).all()

    assert len(persons) == 1
    assert persons[0].name == "Kleverochek"
    assert len(chores) == 1
    assert chores[0].name == "Poop"
