import pytest
import asyncio
import tempfile
import os
from unittest.mock import AsyncMock, MagicMock, patch

from atelier_bot.services.notify import notify_atelier


class TestNotificationService:
    """Test notification service functions."""

    @pytest.mark.asyncio
    async def test_notify_atelier_success(self):
        """Test successful atelier notification."""
        mock_bot = AsyncMock()

        with patch('atelier_bot.services.notify.Bot') as mock_bot_class, \
             patch('atelier_bot.services.notify.get_artwork_by_name_and_user') as mock_get_artwork, \
             patch.dict(os.environ, {'BOT_TOKEN': 'test_token'}):

            mock_bot_instance = AsyncMock()
            mock_bot_class.return_value = mock_bot_instance

            mock_get_artwork.return_value = None  # No artwork icon

            await notify_atelier(123, "testuser", "Test Art", "A4", 5)

            mock_bot_class.assert_called_once_with(token='test_token')
            mock_bot_instance.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_notify_atelier_no_token(self):
        """Test notification with no BOT_TOKEN."""
        with patch.dict(os.environ, {}, clear=True):
            # Should not raise exception and should return early
            await notify_atelier(123, "testuser", "Test Art", "A4", 5)

    @pytest.mark.asyncio
    async def test_notify_atelier_with_image(self):
        """Test notification with artwork image."""
        mock_bot = AsyncMock()

        with patch('atelier_bot.services.notify.Bot') as mock_bot_class, \
             patch('atelier_bot.services.notify.get_artwork_by_name_and_user') as mock_get_artwork, \
             patch.dict(os.environ, {'BOT_TOKEN': 'test_token'}):

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
            mock_get_artwork.return_value = {'image_icon': f'data:image/jpeg;base64,{img_b64}'}

            await notify_atelier(123, "testuser", "Test Art", "A4", 5)

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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])