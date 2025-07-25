"""
Data models for the Bitcoin historical data application.

This module contains the data classes for representing candlestick data and market data.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List
from decimal import Decimal


@dataclass
class Candlestick:
    """Represents a single OHLC candlestick with volume data."""
    
    timestamp: datetime
    open_price: Decimal
    high_price: Decimal
    low_price: Decimal
    close_price: Decimal
    volume: Decimal
    symbol: str = "BTCUSDT"
    
    @property
    def is_bullish(self) -> bool:
        """Check if this candlestick is bullish (close > open)."""
        return self.close_price > self.open_price
    
    @property
    def is_bearish(self) -> bool:
        """Check if this candlestick is bearish (close < open)."""
        return self.close_price < self.open_price
    
    @property
    def body_size(self) -> Decimal:
        """Calculate the size of the candlestick body."""
        return abs(self.close_price - self.open_price)


@dataclass
class MarketData:
    """Represents market data for a specific symbol and timeframe."""
    
    symbol: str
    timeframe: str
    candles: List[Candlestick]
    last_updated: datetime
    
    def __post_init__(self):
        """Sort candles by timestamp after initialization."""
        self.candles.sort(key=lambda c: c.timestamp)
