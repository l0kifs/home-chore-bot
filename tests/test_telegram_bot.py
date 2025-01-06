import datetime
from unittest.mock import AsyncMock
from domain.models import Chore, Person, Frequency
from domain.services import ChoreDistributionService
from use_cases.assign_chores import AssignChoresUseCase
from infrastructure.telegram_bot import notify_chores


async def test_notify_chores(mocker):
    mock_bot = AsyncMock()
    mock_context = AsyncMock()
    mock_context.bot = mock_bot

    # Setup test data
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

    # Mock use case response
    mock_assignments = {
        persons[0]: [chores[0]],
        persons[1]: [chores[1]],
    }
    mocker.patch(
        "use_cases.assign_chores.AssignChoresUseCase.execute",
        return_value=mock_assignments,
    )

    # Call notify_chores
    await notify_chores(mock_context)

    # Check messages sent
    mock_bot.send_message.assert_any_call(
        chat_id=123,
        text="Good morning, Alice!\nHere are your chores for 2023-01-07:\n- Wash Dishes",
    )
    mock_bot.send_message.assert_any_call(
        chat_id=456,
        text="Good morning, Bob!\nHere are your chores for 2023-01-07:\n- Do Laundry",
    )
