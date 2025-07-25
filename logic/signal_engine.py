"""
Signal generation engine for Bitcoin futures trading.

This module combines pattern detection with signal generation logic to create
actionable trading signals with confidence scoring and timing information.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from apis.models import (
    Candlestick, Pattern, Signal, SignalType, PatternType, 
    ConfidenceLevel, MarketData
)
try:
    from .patterns import PatternDetector
except ImportError:
    # Handle case when running as standalone module
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from patterns import PatternDetector


class SignalEngine:
    """Generates trading signals based on candlestick patterns."""
    
    def __init__(
        self, 
        min_confidence: float = 0.5,
        signal_timeout_hours: int = 168  # 1 week default
    ):
        """
        Initialize signal engine.
        
        Args:
            min_confidence: Minimum confidence for signal generation
            signal_timeout_hours: Hours after which signals expire
        """
        self.min_confidence = min_confidence
        self.signal_timeout_hours = signal_timeout_hours
        self.pattern_detector = PatternDetector()
        self.logger = logging.getLogger(__name__)
        
        # Track recent signals to avoid duplicates
        self.recent_signals: List[Signal] = []
        
    def generate_signals(self, market_data: MarketData) -> List[Signal]:
        """
        Generate trading signals from market data.
        
        Args:
            market_data: Market data containing candlestick information
            
        Returns:
            List of generated signals
        """
        signals: List[Signal] = []
        
        if not market_data.candles or len(market_data.candles) < 2:
            self.logger.warning("Insufficient candlestick data for signal generation")
            return signals
        
        # Clean up expired signals
        self._cleanup_expired_signals()
        
        # Detect patterns in the market data
        patterns = self.pattern_detector.detect_patterns(market_data.candles)
        
        # Generate signals from patterns
        for pattern in patterns:
            signal = self._pattern_to_signal(pattern, market_data)
            if signal and self._is_valid_signal(signal):
                signals.append(signal)
                self.recent_signals.append(signal)
        
        self.logger.info(f"Generated {len(signals)} signals from {len(patterns)} patterns")
        return signals
    
    def _pattern_to_signal(self, pattern: Pattern, market_data: MarketData) -> Optional[Signal]:
        """
        Convert a detected pattern into a trading signal.
        
        Args:
            pattern: Detected candlestick pattern
            market_data: Market data context
            
        Returns:
            Trading signal or None if not suitable for signal generation
        """
        # Check minimum confidence threshold
        if pattern.confidence < self.min_confidence:
            self.logger.debug(f"Pattern confidence {pattern.confidence:.2f} below threshold {self.min_confidence}")
            return None
        
        # Determine signal type based on pattern
        signal_type = self._pattern_to_signal_type(pattern.pattern_type)
        if not signal_type:
            return None
        
        # Get the most recent candle for current price
        current_candle = market_data.candles[-1]
        
        # Generate commentary
        commentary = self._generate_commentary(pattern, current_candle, signal_type)
        
        # Generate unique signal ID
        signal_id = f"{pattern.pattern_type.value}_{pattern.timestamp.strftime('%Y%m%d_%H%M%S')}"
        
        # Create signal with timing for next candle open
        signal_timestamp = self._calculate_signal_timestamp(pattern.timestamp)
        
        signal = Signal(
            id=signal_id,
            timestamp=signal_timestamp,
            signal_type=signal_type,
            pattern_type=pattern.pattern_type,
            entry_price=current_candle.close_price,
            confidence=pattern.confidence,
            confidence_level=pattern.confidence_level,
            commentary=commentary,
            pattern=pattern,
            candle=current_candle
        )
        
        return signal
    
    def _pattern_to_signal_type(self, pattern_type: PatternType) -> Optional[SignalType]:
        """Map pattern type to signal type."""
        mapping = {
            PatternType.BULLISH_ENGULFING: SignalType.GO_LONG,
            PatternType.BEARISH_ENGULFING: SignalType.GO_SHORT
        }
        return mapping.get(pattern_type)
    
    def _calculate_signal_timestamp(self, pattern_timestamp: datetime) -> datetime:
        """
        Calculate when the signal should be acted upon.
        
        For weekly candles, this would be the start of the next week.
        """
        # For weekly timeframes, signal is for next week's open
        # This is a simplified calculation - in production, you'd want
        # to account for market hours and timezone
        return pattern_timestamp + timedelta(days=7)
    
    def _generate_commentary(
        self, 
        pattern: Pattern, 
        current_candle: Candlestick, 
        signal_type: SignalType
    ) -> str:
        """Generate human-readable commentary for the signal."""
        pattern_name = pattern.pattern_type.value.replace('_', ' ').title()
        confidence_pct = f"{pattern.confidence:.1%}"
        
        direction = "bullish" if signal_type == SignalType.GO_LONG else "bearish"
        action = "buying opportunity" if signal_type == SignalType.GO_LONG else "selling opportunity"
        
        commentary = (
            f"{pattern_name} pattern detected with {confidence_pct} confidence. "
            f"This {direction} pattern suggests a potential {action} at the next candle open. "
        )
        
        # Add specific pattern insights
        if len(pattern.candles) >= 2:
            prev_candle = pattern.candles[0]
            curr_candle = pattern.candles[1]
            
            body_ratio = float(curr_candle.body_size / prev_candle.body_size)
            volume_change = ""
            if curr_candle.volume > prev_candle.volume:
                vol_increase = float((curr_candle.volume / prev_candle.volume - 1) * 100)
                volume_change = f" with {vol_increase:.1f}% volume increase"
            
            commentary += (
                f"The engulfing candle shows {body_ratio:.1f}x body size expansion{volume_change}, "
                f"indicating strong {direction} momentum."
            )
        
        return commentary
    
    def _analyze_volume_trend(self, recent_candles: List[Candlestick]) -> str:
        """Analyze volume trend in recent candles."""
        if len(recent_candles) < 2:
            return "insufficient_data"
        
        volumes = [float(candle.volume) for candle in recent_candles]
        
        # Simple trend analysis
        increasing = sum(1 for i in range(1, len(volumes)) if volumes[i] > volumes[i-1])
        decreasing = sum(1 for i in range(1, len(volumes)) if volumes[i] < volumes[i-1])
        
        if increasing > decreasing:
            return "increasing"
        elif decreasing > increasing:
            return "decreasing"
        else:
            return "sideways"
    
    def _is_valid_signal(self, signal: Signal) -> bool:
        """
        Validate that a signal meets quality criteria and isn't a duplicate.
        
        Args:
            signal: Signal to validate
            
        Returns:
            True if signal is valid and should be included
        """
        # Check for recent duplicate signals
        for recent_signal in self.recent_signals:
            if (recent_signal.signal_type == signal.signal_type and
                abs((recent_signal.timestamp - signal.timestamp).total_seconds()) < 3600):  # Within 1 hour
                self.logger.debug("Skipping duplicate signal")
                return False
        
        # Basic validation - signal must have valid confidence and entry price
        if signal.confidence < 0.0 or signal.confidence > 1.0:
            self.logger.warning("Invalid signal: confidence out of range")
            return False
        
        if signal.entry_price <= 0:
            self.logger.warning("Invalid signal: invalid entry price")
            return False
        
        return True
    
    def _cleanup_expired_signals(self) -> None:
        """Remove expired signals from recent signals tracking."""
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(hours=self.signal_timeout_hours)
        
        original_count = len(self.recent_signals)
        self.recent_signals = [
            signal for signal in self.recent_signals 
            if signal.timestamp > cutoff_time
        ]
        
        removed_count = original_count - len(self.recent_signals)
        if removed_count > 0:
            self.logger.debug(f"Cleaned up {removed_count} expired signals")
    
    def get_signal_summary(self, signals: List[Signal]) -> Dict[str, Any]:
        """
        Generate summary statistics for a list of signals.
        
        Args:
            signals: List of signals to summarize
            
        Returns:
            Dictionary containing summary statistics
        """
        if not signals:
            return {
                'total_signals': 0,
                'buy_signals': 0,
                'sell_signals': 0,
                'avg_confidence': 0.0,
                'confidence_distribution': {}
            }
        
        buy_signals = [s for s in signals if s.signal_type == SignalType.GO_LONG]
        sell_signals = [s for s in signals if s.signal_type == SignalType.GO_SHORT]
        
        avg_confidence = sum(s.confidence for s in signals) / len(signals)
        
        # Confidence level distribution
        confidence_dist: Dict[str, int] = {}
        for signal in signals:
            level = signal.confidence_level.value
            if level in confidence_dist:
                confidence_dist[level] += 1
            else:
                confidence_dist[level] = 1
        
        return {
            'total_signals': len(signals),
            'buy_signals': len(buy_signals),
            'sell_signals': len(sell_signals),
            'avg_confidence': avg_confidence,
            'confidence_distribution': confidence_dist,
            'latest_signal': signals[-1].timestamp if signals else None
        }
