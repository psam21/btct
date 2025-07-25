"""
Caching utilities for Bitcoin futures trading signal application.

This module implements FR005 and FR016: Data Persistence & Caching Strategy
Provides caching abstraction layer as per FR004 component responsibilities.
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Any, Optional, Dict
import hashlib
import pickle
import os


class CacheManager:
    """
    Caching abstraction layer for data persistence and performance optimization.
    
    Implements FR005: Data Persistence & Caching Strategy
    Implements FR016: Data Caching Implementation
    """
    
    def __init__(self, cache_dir: str = ".cache", default_ttl: int = 3600):
        """
        Initialize cache manager.
        
        Args:
            cache_dir: Directory for file-based cache (future enhancement)
            default_ttl: Default cache TTL in seconds
        """
        self.cache_dir = cache_dir
        self.default_ttl = default_ttl
        
        # Use Streamlit session state for initial implementation
        if 'cache_data' not in st.session_state:
            st.session_state.cache_data = {}
        if 'cache_timestamps' not in st.session_state:
            st.session_state.cache_timestamps = {}
    
    def _generate_cache_key(self, key: str) -> str:
        """Generate a cache key hash for consistent storage."""
        return hashlib.md5(key.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get cached data by key.
        
        Args:
            key: Cache key
            
        Returns:
            Cached data or None if not found/expired
        """
        cache_key = self._generate_cache_key(key)
        
        # Check if key exists and not expired
        if cache_key in st.session_state.cache_data:
            timestamp = st.session_state.cache_timestamps.get(cache_key)
            if timestamp and datetime.now() - timestamp < timedelta(seconds=self.default_ttl):
                return st.session_state.cache_data[cache_key]
            else:
                # Remove expired data
                self._remove(cache_key)
        
        return None
    
    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> None:
        """
        Store data in cache with optional TTL.
        
        Args:
            key: Cache key
            data: Data to cache
            ttl: Time to live in seconds (uses default if None)
        """
        cache_key = self._generate_cache_key(key)
        
        st.session_state.cache_data[cache_key] = data
        st.session_state.cache_timestamps[cache_key] = datetime.now()
    
    def _remove(self, cache_key: str) -> None:
        """Remove data from cache."""
        if cache_key in st.session_state.cache_data:
            del st.session_state.cache_data[cache_key]
        if cache_key in st.session_state.cache_timestamps:
            del st.session_state.cache_timestamps[cache_key]
    
    def clear(self) -> None:
        """Clear all cached data."""
        st.session_state.cache_data.clear()
        st.session_state.cache_timestamps.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_items = len(st.session_state.cache_data)
        expired_items = 0
        
        current_time = datetime.now()
        for cache_key, timestamp in st.session_state.cache_timestamps.items():
            if current_time - timestamp >= timedelta(seconds=self.default_ttl):
                expired_items += 1
        
        return {
            "total_items": total_items,
            "expired_items": expired_items,
            "active_items": total_items - expired_items,
            "cache_ttl": self.default_ttl
        }


# Global cache manager instance
_cache_manager = None


def get_cache_manager() -> CacheManager:
    """Get the global cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


def cache_data(key: str, data: Any, ttl: Optional[int] = None) -> None:
    """
    Cache data with specified key.
    
    Implements FR016: Cache historical data to reduce API calls
    
    Args:
        key: Cache key
        data: Data to cache
        ttl: Time to live in seconds
    """
    cache_manager = get_cache_manager()
    cache_manager.set(key, data, ttl)


def get_cached_data(key: str) -> Optional[Any]:
    """
    Retrieve cached data by key.
    
    Args:
        key: Cache key
        
    Returns:
        Cached data or None if not found/expired
    """
    cache_manager = get_cache_manager()
    return cache_manager.get(key)


def clear_cache() -> None:
    """Clear all cached data."""
    cache_manager = get_cache_manager()
    cache_manager.clear()


def get_cache_info() -> Dict[str, Any]:
    """
    Get cache information and statistics.
    
    Returns:
        Dictionary with cache statistics
    """
    cache_manager = get_cache_manager()
    return cache_manager.get_cache_stats()


@st.cache_data(ttl=3600)  # Cache for 1 hour
def cache_market_data(symbol: str, timeframe: str, data: Any) -> Any:
    """
    Streamlit-native caching for market data.
    
    Uses Streamlit's built-in caching mechanism for performance optimization.
    
    Args:
        symbol: Trading pair symbol
        timeframe: Timeframe for the data
        data: Market data to cache
        
    Returns:
        The cached data
    """
    return data


@st.cache_data(ttl=1800)  # Cache for 30 minutes
def cache_signal_results(market_data_hash: str, signals: Any) -> Any:
    """
    Cache signal generation results.
    
    Args:
        market_data_hash: Hash of the market data used for signal generation
        signals: Generated signals
        
    Returns:
        The cached signals
    """
    return signals


def generate_data_hash(data: Any) -> str:
    """
    Generate a hash for data to use as cache key.
    
    Args:
        data: Data to hash
        
    Returns:
        Hash string
    """
    try:
        # Convert data to string and hash it
        data_str = str(data)
        return hashlib.md5(data_str.encode()).hexdigest()
    except Exception:
        # Fallback to timestamp-based hash
        return hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()
