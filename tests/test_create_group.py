import pytest
import random
import string
from unittest.mock import AsyncMock, MagicMock
from urllib.parse import quote
from clients.tg_bot_client import  TgBotClient  
from clients.db_client import Group, Person 

@pytest.fixture
def mock_update():
    """Создает mock-объект update"""
    update = AsyncMock()
    update.message.reply_text = AsyncMock()
    update.message.from_user.id = 12345
    update.message.from_user.username = "test_user"
    return update

@pytest.fixture
def mock_context():
    """Создает mock-объект context"""
    context = MagicMock()
    context.args = ["TestGroup"]
    return context

@pytest.fixture
def mock_session():
    """Создает мок сессии базы данных"""
    session = MagicMock()
    session.commit = MagicMock()
    session.close = MagicMock()
    session.query.return_value.filter_by.return_value.first.return_value = None
    return session

@pytest.fixture
def bot(mock_session):
    """Создает экземпляр бота с мок-сессией"""
    bot = TgBotClient(token="test_token", db_url="sqlite:///:memory:")  # Фиктивные параметры
    bot.db_client._sessionmaker = MagicMock(return_value=mock_session)
    return bot

@pytest.mark.asyncio
async def test_create_group_command(bot, mock_update, mock_context, mock_session):
    """Тест создания группы"""
    invite_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(random, "choices", lambda *args, **kwargs: list(invite_code))

        await bot.create_group_command(mock_update, mock_context)

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called()
        mock_update.message.reply_text.assert_called_with(
            f"✅ Группа '{mock_context.args[0]}' создана!\n🔗 Ссылка приглашения: https://t.me/YOUR_BOT_USERNAME?start={quote(f'join_{invite_code}')}"
        )

@pytest.mark.asyncio
async def test_create_group_already_exists(bot, mock_update, mock_context, mock_session):
    """Тест попытки создать существующую группу"""
    mock_session.query.return_value.filter_by.return_value.first.return_value = Group(name="TestGroup")

    await bot.create_group_command(mock_update, mock_context)

    mock_update.message.reply_text.assert_called_with("Группа с таким названием уже существует!")
    mock_session.add.assert_not_called()

@pytest.mark.asyncio
async def test_start_command_invalid_invite(bot, mock_update, mock_context, mock_session):
    """Тест входа с неверным кодом"""
    mock_context.args = ["join_wrongcode"]
    mock_session.query.return_value.filter_by.return_value.first.return_value = None

    await bot.start_command(mock_update, mock_context)

    mock_update.message.reply_text.assert_called_with("❌ Неверный код приглашения!")
    
@pytest.mark.asyncio
async def test_start_command_valid_invite(bot, mock_update, mock_context, mock_session):
    """Тест команды /start с валидным кодом приглашения"""

    invite_code = "ABC123"
    fake_group = "TestGroup"
    tg_user_id = 12345
    username = "TestUser"

    # Создаем мок-объекты группы и пользователя
    fake_group = Group(id=1, name="Test Group", invite_code="ABC123")

    # Мокаем запросы к базе данных
    mock_query = MagicMock()
    mock_query.filter_by.return_value.first.side_effect = [fake_group, None]  # Группа найдена, пользователя в группе нет

    mock_session.query.return_value = mock_query  # Устанавливаем мок-сессию

    # Подготовка mock_update и mock_context
    mock_update.message.from_user.id = tg_user_id
    mock_update.message.from_user.username = username
    mock_update.message.reply_text = AsyncMock()
    mock_context.args = [f"join_{invite_code}"]

    # Вызываем команду /start
    await bot.start_command(mock_update, mock_context)

    # Проверяем, что бот отправил ожидаемое сообщение
    mock_update.message.reply_text.assert_called_with(f"🎉 Добро пожаловать в '{fake_group.name}'!")

