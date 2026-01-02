from backend.services.cache import CacheService
from unittest.mock import MagicMock, patch

def test_cache_service():
    with patch('redis.from_url') as mock_redis:
        mock_instance = MagicMock()
        mock_redis.return_value = mock_instance

        service = CacheService()

        # Test Set
        service.set("test_key", "test_val")
        mock_instance.set.assert_called_with("test_key", "test_val", ex=None)

        # Test Get
        mock_instance.get.return_value = "test_val"
        val = service.get("test_key")
        assert val == "test_val"
