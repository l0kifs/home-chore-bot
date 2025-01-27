import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from clients.tg_bot_client import TgBotClient  # Adjust import path
from clients.db_client import DBClient, Chore, Person  # Adjust import path# Adjust import path
from enums.complexity import Complexity
from enums.frequency import Frequency

@pytest.fixture
def bot_client():
    with patch('app.clients.tg_bot_client.Application') as mock_application:
        mock_bot = MagicMock()
        mock_application.return_value = mock_bot
        
        bot = TgBotClient("mock_token", "mock_db_url")  # This now uses the mocked DBClient internally
        bot.set_chat_id(12345)  # Mock chat ID
        yield bot
        
@pytest.mark.asyncio
async def test_notify_chores_daily(bot_client):
    mock_context = AsyncMock()
    
    # Mock database responses
    mock_person = MagicMock(spec=Person, id=1, tg_user_id="user1", tg_group_id="group1")
    mock_chore = MagicMock(spec=Chore, id=1, tg_group_id="group1", name="Chore1", complexity=Complexity.EASY, frequency=Frequency.DAILY)
    
    with patch.object(DBClient, 'get_persons_by_tg_group_id', return_value=[mock_person]):  # Ensure at least one person
        with patch.object(DBClient, 'get_chores_by_tg_group_id', return_value=[mock_chore]):
            with patch('app.logic.chore_distribution.split_list_to_groups', return_value=[{'person': mock_person, 'tasks': [{'name': 'Chore1', 'complexity': Complexity.EASY.value}]}]) as mock_split:
                await bot_client._notify_chores_daily(mock_context, test_date=datetime.now())

                
                # Assert that the bot sent a message
                mock_context.bot.send_message.assert_awaited_once()
                message_sent = mock_context.bot.send_message.call_args[1]['text']
                assert "Chore1" in message_sent
                
                # Test for multiple days to check if it adapts to different days
                for day in range(7):
                    test_date = datetime.now() + timedelta(days=day)
                    await bot_client._notify_chores_daily(mock_context, test_date=test_date)
                
                # Here you might want to assert more about how the message changes day by day, 
                # but we'll keep it simple for now
                assert mock_context.bot.send_message.call_count == 8  # 1 from initial test + 7 days
                assert mock_split.call_count == 8  # split_list_to_groups should have been called for each day

@pytest.mark.asyncio
async def test_no_chores_or_persons(bot_client):
    mock_context = AsyncMock()
    
    with patch.object(DBClient, 'get_persons_by_tg_group_id', return_value=[MagicMock()]):
        with patch.object(DBClient, 'get_chores_by_tg_group_id', return_value=[]):
            await bot_client._notify_chores_daily(mock_context)
                
            mock_context.bot.send_message.assert_awaited_once()
            message_sent = mock_context.bot.send_message.call_args[1]['text']
            assert "Сегодня нет назначенных дел" in message_sent

if __name__ == "__main__":
    pytest.main([__file__])