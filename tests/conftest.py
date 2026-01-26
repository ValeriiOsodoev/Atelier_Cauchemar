import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def mock_bot():
    """Mock bot instance."""
    bot = MagicMock(spec=Bot)
    bot.send_message = AsyncMock()
    bot.send_photo = AsyncMock()
    bot.send_document = AsyncMock()
    return bot


@pytest.fixture
async def mock_dispatcher():
    """Mock dispatcher with memory storage."""
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    return dp


@pytest.fixture
async def mock_message():
    """Mock message object."""
    message = MagicMock()
    message.from_user.id = 123
    message.from_user.username = "testuser"
    message.text = "test message"
    message.answer = AsyncMock()
    message.reply = AsyncMock()
    return message


@pytest.fixture
async def mock_callback_query():
    """Mock callback query."""
    query = MagicMock()
    query.from_user.id = 123
    query.data = "test_data"
    query.message.edit_text = AsyncMock()
    query.message.edit_reply_markup = AsyncMock()
    query.answer = AsyncMock()
    return query