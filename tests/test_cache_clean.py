"""
Comprehensive unit tests for the cache system.

Tests the caching abstraction layer (FR005, FR016).
"""

import pytest
from unittest.mock import patch, Mock
from datetime import datetime, timedelta
import streamlit as st

from utils.cache import (
    CacheManager, 
    cache_data, 
    get_cached_data, 
    clear_cache,
    get_cache_info
)


class TestCacheManager:
    """Test suite for CacheManager class."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        # Clear any existing cache
        clear_cache()
    
    def test_cache_manager_initialization(self):
        """Test CacheManager initialization."""
        cache_manager = CacheManager()
        
        assert cache_manager.cache_dir == ".cache"
        assert cache_manager.default_ttl == 3600
    
    def test_cache_manager_custom_initialization(self):
        """Test CacheManager with custom parameters."""
        cache_manager = CacheManager(cache_dir="/tmp/cache", default_ttl=7200)
        
        assert cache_manager.cache_dir == "/tmp/cache"
        assert cache_manager.default_ttl == 7200
    
    def test_cache_set_and_get(self):
        """Test basic cache set and get operations."""
        cache_manager = CacheManager()
        
        # Set data
        test_data = {"symbol": "BTCUSDT", "price": 45000}
        cache_manager.set("market_data", test_data)
        
        # Get data
        retrieved_data = cache_manager.get("market_data")
        
        assert retrieved_data == test_data
    
    def test_cache_get_nonexistent_key(self):
        """Test getting data with non-existent key."""
        cache_manager = CacheManager()
        
        result = cache_manager.get("nonexistent_key")
        
        assert result is None
    
    def test_cache_clear(self):
        """Test cache clearing functionality."""
        cache_manager = CacheManager()
        
        # Set multiple items
        cache_manager.set("key1", "value1")
        cache_manager.set("key2", "value2")
        
        # Verify they exist
        assert cache_manager.get("key1") == "value1"
        assert cache_manager.get("key2") == "value2"
        
        # Clear cache
        cache_manager.clear()
        
        # Verify they're gone
        assert cache_manager.get("key1") is None
        assert cache_manager.get("key2") is None
    
    def test_cache_stats(self):
        """Test cache statistics generation."""
        cache_manager = CacheManager(default_ttl=3600)
        
        # Empty cache stats
        stats = cache_manager.get_cache_stats()
        assert stats["total_items"] == 0
        assert stats["cache_ttl"] == 3600
        
        # Add some items
        cache_manager.set("key1", "value1")
        cache_manager.set("key2", "value2")
        
        stats = cache_manager.get_cache_stats()
        assert stats["total_items"] == 2


class TestCacheUtilityFunctions:
    """Test suite for cache utility functions."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        clear_cache()
    
    def test_cache_data_function(self):
        """Test cache_data utility function."""
        test_data = {"test": "data"}
        
        cache_data("test_key", test_data)
        retrieved_data = get_cached_data("test_key")
        
        assert retrieved_data == test_data
    
    def test_get_cached_data_function(self):
        """Test get_cached_data utility function."""
        # Test with non-existent key
        result = get_cached_data("nonexistent")
        assert result is None
        
        # Test with existing key
        cache_data("existing_key", "existing_value")
        result = get_cached_data("existing_key")
        assert result == "existing_value"
    
    def test_clear_cache_function(self):
        """Test clear_cache utility function."""
        # Add some data
        cache_data("key1", "value1")
        cache_data("key2", "value2")
        
        # Verify data exists
        assert get_cached_data("key1") == "value1"
        assert get_cached_data("key2") == "value2"
        
        # Clear cache
        clear_cache()
        
        # Verify data is gone
        assert get_cached_data("key1") is None
        assert get_cached_data("key2") is None
    
    def test_get_cache_info_function(self):
        """Test get_cache_info utility function."""
        # Empty cache
        info = get_cache_info()
        assert info["total_items"] == 0
        
        # Add some data
        cache_data("key1", "value1")
        cache_data("key2", "value2")
        
        info = get_cache_info()
        assert info["total_items"] == 2


class TestCacheIntegration:
    """Integration tests for cache system."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        clear_cache()
    
    def test_cache_integration_workflow(self):
        """Test complete cache workflow."""
        # Simulate market data caching workflow
        market_data = {
            "symbol": "BTCUSDT",
            "timeframe": "1w",
            "candles": [
                {"open": 45000, "close": 45500},
                {"open": 45500, "close": 46000}
            ]
        }
        
        # Cache market data
        cache_key = "market_data_BTCUSDT_1w"
        cache_data(cache_key, market_data)
        
        # Cache signal results
        signals = [{"signal": "GO_LONG", "confidence": 0.8}]
        signal_cache_key = "signals_test_hash"
        cache_data(signal_cache_key, signals)
        
        # Retrieve cached data
        cached_market_data = get_cached_data(cache_key)
        cached_signals = get_cached_data(signal_cache_key)
        
        # Verify data integrity
        assert cached_market_data == market_data
        assert cached_signals == signals
        
        # Check cache statistics
        cache_info = get_cache_info()
        assert cache_info["total_items"] == 2
    
    def test_cache_performance_simulation(self):
        """Test cache performance with multiple operations."""
        import time
        
        # Simulate multiple cache operations
        start_time = time.time()
        
        for i in range(50):  # Reduced for faster testing
            cache_data(f"key_{i}", f"value_{i}")
        
        for i in range(50):
            result = get_cached_data(f"key_{i}")
            assert result == f"value_{i}"
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete quickly (less than 0.5 second for 100 operations)
        assert execution_time < 0.5
        
        # Verify cache statistics
        cache_info = get_cache_info()
        assert cache_info["total_items"] == 50


class TestCacheErrorHandling:
    """Test suite for cache error handling."""
    
    def test_cache_with_none_values(self):
        """Test caching None values."""
        cache_data("none_key", None)
        result = get_cached_data("none_key")
        
        # Should be able to cache None
        assert result is None
    
    def test_cache_with_complex_objects(self):
        """Test caching complex objects."""
        complex_data = {
            "nested": {
                "data": [1, 2, 3],
                "info": {"key": "value"}
            },
            "timestamp": datetime.now().isoformat()
        }
        
        cache_data("complex_key", complex_data)
        result = get_cached_data("complex_key")
        
        assert result == complex_data
    
    def test_cache_key_types(self):
        """Test different cache key types."""
        # String keys
        cache_data("string_key", "string_value")
        assert get_cached_data("string_key") == "string_value"
        
        # Keys with special characters
        cache_data("key_with_special-chars.123", "special_value")
        assert get_cached_data("key_with_special-chars.123") == "special_value"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
