import pytest
import asyncio
import os
import tempfile
from unittest.mock import AsyncMock, MagicMock
import base64
from io import BytesIO
from PIL import Image

# Test database functions
from atelier_bot.db.db import (
    create_artwork_icon,
    init_db,
    create_or_update_user,
    search_users,
    get_artworks_for_user,
    get_papers_for_user,
    add_paper_for_user,
    create_artwork,
    create_order,
    get_all_users
)


@pytest.fixture
def sample_image_data():
    """Create a small test image."""
    img = Image.new('RGB', (200, 200), color='red')
    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    buffer.seek(0)
    return buffer.getvalue()


class TestArtworkIcon:
    def test_create_artwork_icon_success(self, sample_image_data):
        """Test successful icon creation."""
        result = create_artwork_icon(sample_image_data, (50, 50))

        assert result is not None
        assert result.startswith("data:image/jpeg;base64,")

        # Decode and verify it's a valid image
        base64_data = result.split(",")[1]
        decoded = base64.b64decode(base64_data)
        img = Image.open(BytesIO(decoded))

        # Should be resized to thumbnail
        assert img.size[0] <= 50
        assert img.size[1] <= 50

    def test_create_artwork_icon_invalid_data(self):
        """Test icon creation with invalid data."""
        result = create_artwork_icon(b"invalid image data")
        assert result is None


class TestDatabaseOperations:
    """Test database operations with temporary databases."""

    @pytest.mark.asyncio
    async def test_database_functions_exist(self):
        """Test that key database functions exist and are callable."""
        # Just test that functions exist and are callable
        assert callable(create_or_update_user)
        assert callable(search_users)
        assert callable(add_paper_for_user)
        assert callable(create_artwork)
        assert callable(create_order)
        assert callable(get_all_users)
        assert callable(get_papers_for_user)
        assert callable(get_artworks_for_user)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])