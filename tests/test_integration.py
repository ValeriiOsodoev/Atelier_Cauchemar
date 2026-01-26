import pytest
import os
from unittest.mock import AsyncMock, patch

from atelier_bot.services.notify import notify_atelier


class TestNotificationService:
    """Test notification service functions."""

    @pytest.mark.asyncio
    async def test_notify_atelier_success(self):
        """Test successful atelier notification."""

        with (
            patch('atelier_bot.services.notify.Bot') as mock_bot_class,
            patch('atelier_bot.services.notify.get_artwork_by_name_and_user')
            as mock_get_artwork,
            patch.dict(os.environ, {'BOT_TOKEN': 'test_token'})
        ):

            mock_bot_instance = AsyncMock()
            mock_bot_class.return_value = mock_bot_instance

            mock_get_artwork.return_value = None  # No artwork icon

            await notify_atelier(123, "testuser", "Test Art", "A4", 5, 1)

            mock_bot_class.assert_called_once_with(token='test_token')
            mock_bot_instance.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_notify_atelier_no_token(self):
        """Test notification with no BOT_TOKEN."""
        with patch.dict(os.environ, {}, clear=True):
            # Should not raise exception and should return early
            await notify_atelier(123, "testuser", "Test Art", "A4", 5, 1)

    @pytest.mark.asyncio
    async def test_notify_atelier_with_image(self):
        """Test notification with artwork image."""

        with (
            patch('atelier_bot.services.notify.Bot') as mock_bot_class,
            patch('atelier_bot.services.notify.get_artwork_by_name_and_user')
            as mock_get_artwork,
            patch.dict(os.environ, {'BOT_TOKEN': 'test_token'})
        ):

            mock_bot_instance = AsyncMock()
            mock_bot_class.return_value = mock_bot_instance

            # Mock artwork with valid base64 image
            import base64
            from PIL import Image
            img = Image.new('RGB', (10, 10), color='red')
            from io import BytesIO
            buffer = BytesIO()
            img.save(buffer, format='JPEG')
            img_b64 = base64.b64encode(buffer.getvalue()).decode()
            mock_get_artwork.return_value = {
                'image_icon': f'data:image/jpeg;base64,{img_b64}'
            }

            await notify_atelier(123, "testuser", "Test Art", "A4", 5, 1)

            mock_bot_instance.send_photo.assert_called_once()


class TestIntegrationFlows:
    """Integration tests for complete user flows."""

    @pytest.mark.asyncio
    async def test_database_functions_exist(self):
        """Test that key database functions exist."""
        from atelier_bot.db.db import (
            create_or_update_user,
            get_all_users,
            add_paper_for_user,
            get_papers_for_user,
            create_artwork,
            get_artworks_for_user,
            create_order
        )

        # Just test that functions exist and are callable
        assert callable(create_or_update_user)
        assert callable(get_all_users)
        assert callable(add_paper_for_user)
        assert callable(get_papers_for_user)
        assert callable(create_artwork)
        assert callable(get_artworks_for_user)
        assert callable(create_order)

    @pytest.mark.asyncio
    async def test_user_auto_creation_workflow(self):
        """Test that atelier workflow can auto-create users by user_id."""
        from atelier_bot.db.db import search_users, create_or_update_user, init_db
        import tempfile
        import os

        # Create a temporary database for testing
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
            test_db_path = tmp.name

        try:
            # Initialize the database
            await init_db(test_db_path)

            # Test user_id that doesn't exist
            test_user_id = 999999

            # Initially, user should not be found
            users = await search_users(str(test_user_id), test_db_path)
            assert len(users) == 0

            # Simulate the logic from atelier_enter_artwork_user
            text = str(test_user_id)
            users = await search_users(text, test_db_path)
            if not users:
                # Should create user automatically
                user_id = int(text)
                await create_or_update_user(user_id, f"user_{user_id}", test_db_path)

            # Now user should exist
            users = await search_users(str(test_user_id), test_db_path)
            assert len(users) == 1
            assert users[0]['user_id'] == test_user_id
            assert users[0]['username'] == f"user_{test_user_id}"

        finally:
            # Clean up
            if os.path.exists(test_db_path):
                os.unlink(test_db_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
