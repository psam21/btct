"""
Data models for the Bitcoin futures trading signal application.

This module contains all the data classes and enums used throughout the application
for representing candlestick data, trading signals, patterns, and related entities.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, List
from decimal import Decimal


class SignalType(Enum):
    """Types of trading signals that can be generated."""
    GO_LONG = "GO_LONG"
    GO_SHORT = "GO_SHORT"
    HOLD = "HOLD"


class PatternType(Enum):
    """Types of candlestick patterns that can be detected."""
    BULLISH_ENGULFING = "BULLISH_ENGULFING"
    BEARISH_ENGULFING = "BEARISH_ENGULFING"
    NO_PATTERN = "NO_PATTERN"


class ConfidenceLevel(Enum):
    """Confidence levels for pattern detection and signal generation."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


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
        """Check if the candlestick is bullish (green)."""
        return self.close_price > self.open_price
    
    @property
    def is_bearish(self) -> bool:
        """Check if the candlestick is bearish (red)."""
        return self.close_price < self.open_price
    
    @property
    def body_size(self) -> Decimal:
        """Calculate the size of the candlestick body."""
        return abs(self.close_price - self.open_price)
    
    @property
    def upper_shadow(self) -> Decimal:
        """Calculate the upper shadow (wick) size."""
        return self.high_price - max(self.open_price, self.close_price)
    
    @property
    def lower_shadow(self) -> Decimal:
        """Calculate the lower shadow (wick) size."""
        return min(self.open_price, self.close_price) - self.low_price
    
    @property
    def total_range(self) -> Decimal:
        """Calculate the total range (high - low)."""
        return self.high_price - self.low_price
    
    def __str__(self) -> str:
        """String representation of the candlestick."""
        direction = "🟢" if self.is_bullish else "🔴" if self.is_bearish else "⚪"
        return f"{direction} {self.timestamp.strftime('%Y-%m-%d')} O:{self.open_price} H:{self.high_price} L:{self.low_price} C:{self.close_price}"


@dataclass
class Pattern:
    """Represents a detected candlestick pattern."""
    
    pattern_type: PatternType
    confidence: float  # 0.0 to 1.0
    confidence_level: ConfidenceLevel
    timestamp: datetime
    candles: List[Candlestick]
    description: str
    
    def __post_init__(self):
        """Validate pattern data after initialization."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        
        if len(self.candles) < 2:
            raise ValueError("Pattern must have at least 2 candles")


@dataclass
class Signal:
    """Represents a trading signal generated from pattern analysis."""
    
    id: str
    timestamp: datetime
    signal_type: SignalType
    pattern_type: PatternType
    entry_price: Decimal
    confidence: float  # 0.0 to 1.0
    confidence_level: ConfidenceLevel
    commentary: str
    pattern: Optional[Pattern] = None
    candle: Optional[Candlestick] = None
    
    def __post_init__(self):
        """Validate signal data after initialization."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        
        if self.entry_price <= 0:
            raise ValueError("Entry price must be positive")


@dataclass
class MarketData:
    """Container for market data and analysis results."""
    
    symbol: str
    timeframe: str
    candles: List[Candlestick]
    patterns: List[Pattern]
    signals: List[Signal]
    last_updated: datetime
    
    @property
    def latest_candle(self) -> Optional[Candlestick]:
        """Get the most recent candlestick."""
        return self.candles[-1] if self.candles else None
    
    @property
    def latest_signal(self) -> Optional[Signal]:
        """Get the most recent signal."""
        return self.signals[-1] if self.signals else None
    
    def get_candles_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Candlestick]:
        """Filter candles by date range."""
        return [
            candle for candle in self.candles
            if start_date <= candle.timestamp <= end_date
        ]


@dataclass
class AnalysisResult:
    """Results from pattern analysis and signal generation."""
    
    timestamp: datetime
    symbol: str
    total_candles_analyzed: int
    patterns_detected: int
    signals_generated: int
    analysis_duration_ms: float
    success: bool
    error_message: Optional[str] = None
    
    @property
    def pattern_detection_rate(self) -> float:
        """Calculate pattern detection rate."""
        if self.total_candles_analyzed == 0:
            return 0.0
        return self.patterns_detected / self.total_candles_analyzed
    
    @property
    def signal_generation_rate(self) -> float:
        """Calculate signal generation rate."""
        if self.patterns_detected == 0:
            return 0.0
        return self.signals_generated / self.patterns_detected


def get_confidence_level(confidence: float) -> ConfidenceLevel:
    """Convert numerical confidence to confidence level enum."""
    if confidence >= 0.9:
        return ConfidenceLevel.VERY_HIGH
    elif confidence >= 0.75:
        return ConfidenceLevel.HIGH
    elif confidence >= 0.5:
        return ConfidenceLevel.MEDIUM
    else:
        return ConfidenceLevel.LOW


def create_sample_candlestick(
    timestamp: datetime,
    open_price: float,
    high_price: float,
    low_price: float,
    close_price: float,
    volume: float = 1000.0
) -> Candlestick:
    """Helper function to create sample candlestick data for testing."""
    return Candlestick(
        timestamp=timestamp,
        open_price=Decimal(str(open_price)),
        high_price=Decimal(str(high_price)),
        low_price=Decimal(str(low_price)),
        close_price=Decimal(str(close_price)),
        volume=Decimal(str(volume))
    )
