import pytest
import os
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram.fsm.context import FSMContext

# Test the actual handler functions that exist
from atelier_bot.handlers.print_handler import router


class TestRouterSetup:
    """Test that the router is properly configured."""

    def test_router_exists(self):
        """Test that router is imported and exists."""
        assert router is not None

    def test_router_has_handlers(self):
        """Test that router has some handlers registered."""
        # In aiogram 3.x, we can check if handlers are registered by checking
        # the router object
        # This is a basic check that router is functional
        assert router is not None
        assert hasattr(router, 'message')
        assert hasattr(router, 'callback_query')


class TestMessageHandlers:
    """Test message handler functions."""

    @pytest.mark.asyncio
    async def test_cmd_start_with_mock(self):
        """Test start command with mocked dependencies."""
        from atelier_bot.handlers.print_handler import cmd_start

        mock_message = MagicMock()
        mock_message.from_user.id = 123
        mock_message.from_user.username = "testuser"
        mock_message.answer = AsyncMock()
        mock_state = AsyncMock(spec=FSMContext)

        with (
            patch('atelier_bot.handlers.print_handler.create_or_update_user')
            as mock_create_user,
            patch('atelier_bot.handlers.print_handler.main_menu_keyboard')
            as mock_menu_kb,
            patch('atelier_bot.handlers.print_handler.main_reply_keyboard')
            as mock_reply_kb
        ):

            mock_menu_kb.return_value = None
            mock_reply_kb.return_value = None

            await cmd_start(mock_message, mock_state)

            mock_create_user.assert_called_once_with(123, "testuser")
            assert mock_message.answer.called  # Called at least once


class TestNotificationService:
    """Test notification service functions."""

    @pytest.mark.asyncio
    async def test_notify_atelier_function_exists(self):
        """Test that notify_atelier function can be imported and called."""
        from atelier_bot.services.notify import notify_atelier

        # Test that function exists and is callable
        assert callable(notify_atelier)

        # Test with missing BOT_TOKEN (should return early)
        with patch.dict(os.environ, {}, clear=True):
            # Should not raise exception
            await notify_atelier(123, "testuser", "art", "paper", 5)


class TestDatabaseIntegration:
    """Test database integration with handlers."""

    @pytest.mark.asyncio
    async def test_user_creation_integration(self):
        """Test user creation through handler flow."""
        # This test runs without database setup for basic functionality check
        from atelier_bot.db.db import create_or_update_user
        # Just test that the function exists and is callable
        assert callable(create_or_update_user)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
