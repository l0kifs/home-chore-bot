import pytest
from unittest.mock import MagicMock
from app.use_cases.assign_chores import AssignChoresUseCase
from app.domain.models import Chore, Person
import datetime
from app.database import SessionManager  # Assuming this is your database session manager


@pytest.fixture(scope="function")
def clear_database():
    """Fixture to clear the database before each test."""
    with SessionManager() as session:
        # Delete all records in the relevant tables
        session.query(Chore).delete()
        session.query(Person).delete()
        session.commit()  # Commit the transaction to persist the changes

    yield  # This will allow the test to run after clearing the DB

    # Optionally, you can also clean up again after the test if needed
    with SessionManager() as session:
        session.query(Chore).delete()
        session.query(Person).delete()
        session.commit()  # Commit any changes if needed
        
@pytest.fixture
def mock_session():
    # Create a mock session object
    session = MagicMock()
    # Define mock behavior for the session
    session.query().all.return_value = [
        Person(name="Alice", telegram_id="123"),
        Person(name="Bob", telegram_id="456"),
    ]
    session.query(Chore).all.return_value = [
        Chore(name="Dishes", frequency="daily"),
        Chore(name="Vacuum", frequency="weekly"),
    ]
    return session

def test_get_due_chores(mock_session):
    # Set up mock chores with explicit 'name' and 'frequency'
    mock_chores = [
        MagicMock(),
        MagicMock()
    ]
    
    # Assign mock values for name and frequency attributes
    mock_chores[0].name = "Dishes"
    mock_chores[0].frequency = "daily"
    
    mock_chores[1].name = "Vacuum"
    mock_chores[1].frequency = "daily"
    
    # Mock the query to return these chores
    mock_session.query.return_value.all.return_value = mock_chores

    # Given a reference date of today
    reference_date = datetime.date.today()

    # Initialize AssignChoresUseCase with mock session
    assign_chores = AssignChoresUseCase(mock_session)

    # Get the due chores
    due_chores = assign_chores.get_due_chores(reference_date)

    # Add some logging for debugging
    print(f"Due chores: {[chore.name for chore in due_chores]}")  # Debugging line

    # Test if the correct chores are returned (now expecting 2 daily chores)
    assert len(due_chores) == 2  # Adjust this according to your logic

    # Now test if the chores are correctly named
    assert any(chore.name == "Dishes" for chore in due_chores)
    assert any(chore.name == "Vacuum" for chore in due_chores)
    
def test_assign_chores(mock_session):
    # Given a reference date of today
    reference_date = datetime.date.today()

    # Initialize AssignChoresUseCase with mock session
    assign_chores = AssignChoresUseCase(mock_session)

    # Get the due chores
    due_chores = assign_chores.get_due_chores(reference_date)

    # Get the persons to assign chores to
    persons = mock_session.query(Person).all()

    # Assign the chores
    assignment_map = assign_chores.execute(due_chores, persons, reference_date)

    # Debugging print to check assignment_map
    print(f"Assignment map: {assignment_map}")

    # Test if each person has been assigned chores
    assert len(assignment_map) == 2  # Alice and Bob
    for person, chores in assignment_map.items():
        print(f"{person.name} assigned chores: {[chore.name for chore in chores]}")  # Debugging line
        assert len(chores) > 0  # Make sure there are chores assigned
        assert all(isinstance(chore, Chore) for chore in chores)
