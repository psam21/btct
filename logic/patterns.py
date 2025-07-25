"""
Candlestick pattern detection algorithms.

This module implements the core pattern detection logic for identifying
bullish and bearish engulfing patterns in Bitcoin futures data.
"""

from typing import List, Optional
from datetime import datetime
from decimal import Decimal
import logging

from apis.models import (
    Candlestick, Pattern, PatternType, ConfidenceLevel, 
    get_confidence_level
)


class PatternDetector:
    """Detects candlestick patterns in market data."""
    
    def __init__(self, min_body_ratio: float = 0.6, min_engulfment_ratio: float = 1.1):
        """
        Initialize pattern detector.
        
        Args:
            min_body_ratio: Minimum ratio of body to total range for valid candles
            min_engulfment_ratio: Minimum ratio for engulfment validation
        """
        self.min_body_ratio = min_body_ratio
        self.min_engulfment_ratio = min_engulfment_ratio
        self.logger = logging.getLogger(__name__)
    
    def detect_patterns(self, candles: List[Candlestick]) -> List[Pattern]:
        """
        Detect all patterns in a list of candlesticks.
        
        Args:
            candles: List of candlesticks to analyze
            
        Returns:
            List of detected patterns
        """
        patterns: List[Pattern] = []
        
        if len(candles) < 2:
            self.logger.warning("Need at least 2 candles for pattern detection")
            return patterns
        
        # Analyze each consecutive pair of candles
        for i in range(1, len(candles)):
            prev_candle = candles[i-1]
            current_candle = candles[i]
            
            # Check for bullish engulfing
            bullish_pattern = self.detect_bullish_engulfing(prev_candle, current_candle)
            if bullish_pattern:
                patterns.append(bullish_pattern)
                continue
            
            # Check for bearish engulfing
            bearish_pattern = self.detect_bearish_engulfing(prev_candle, current_candle)
            if bearish_pattern:
                patterns.append(bearish_pattern)
        
        self.logger.info(f"Detected {len(patterns)} patterns from {len(candles)} candles")
        return patterns
    
    def detect_bullish_engulfing(
        self, 
        prev_candle: Candlestick, 
        current_candle: Candlestick
    ) -> Optional[Pattern]:
        """
        Detect bullish engulfing pattern.
        
        Bullish Engulfing Criteria:
        1. Previous candle is bearish (red)
        2. Current candle is bullish (green)
        3. Current candle's body completely engulfs previous candle's body
        4. Current open < Previous close AND Current close > Previous open
        
        Args:
            prev_candle: Previous candlestick
            current_candle: Current candlestick
            
        Returns:
            Pattern object if bullish engulfing detected, None otherwise
        """
        # Basic bullish engulfing criteria
        if not (prev_candle.is_bearish and current_candle.is_bullish):
            return None
        
        # Check body engulfment
        if not self._is_bullish_engulfment(prev_candle, current_candle):
            return None
        
        # Calculate confidence based on various factors
        confidence = self._calculate_bullish_confidence(prev_candle, current_candle)
        
        if confidence < 0.3:  # Minimum confidence threshold
            return None
        
        pattern = Pattern(
            pattern_type=PatternType.BULLISH_ENGULFING,
            confidence=confidence,
            confidence_level=get_confidence_level(confidence),
            timestamp=current_candle.timestamp,
            candles=[prev_candle, current_candle],
            description=f"Bullish Engulfing: {confidence:.1%} confidence"
        )
        
        self.logger.debug(f"Bullish engulfing detected at {current_candle.timestamp} with {confidence:.1%} confidence")
        return pattern
    
    def detect_bearish_engulfing(
        self, 
        prev_candle: Candlestick, 
        current_candle: Candlestick
    ) -> Optional[Pattern]:
        """
        Detect bearish engulfing pattern.
        
        Bearish Engulfing Criteria:
        1. Previous candle is bullish (green)
        2. Current candle is bearish (red)
        3. Current candle's body completely engulfs previous candle's body
        4. Current open > Previous close AND Current close < Previous open
        
        Args:
            prev_candle: Previous candlestick
            current_candle: Current candlestick
            
        Returns:
            Pattern object if bearish engulfing detected, None otherwise
        """
        # Basic bearish engulfing criteria
        if not (prev_candle.is_bullish and current_candle.is_bearish):
            return None
        
        # Check body engulfment
        if not self._is_bearish_engulfment(prev_candle, current_candle):
            return None
        
        # Calculate confidence based on various factors
        confidence = self._calculate_bearish_confidence(prev_candle, current_candle)
        
        if confidence < 0.3:  # Minimum confidence threshold
            return None
        
        pattern = Pattern(
            pattern_type=PatternType.BEARISH_ENGULFING,
            confidence=confidence,
            confidence_level=get_confidence_level(confidence),
            timestamp=current_candle.timestamp,
            candles=[prev_candle, current_candle],
            description=f"Bearish Engulfing: {confidence:.1%} confidence"
        )
        
        self.logger.debug(f"Bearish engulfing detected at {current_candle.timestamp} with {confidence:.1%} confidence")
        return pattern
    
    def _is_bullish_engulfment(self, prev_candle: Candlestick, current_candle: Candlestick) -> bool:
        """Check if current candle engulfs previous candle for bullish pattern."""
        # Current open must be below previous close
        # Current close must be above previous open
        return (
            current_candle.open_price < prev_candle.close_price and
            current_candle.close_price > prev_candle.open_price
        )
    
    def _is_bearish_engulfment(self, prev_candle: Candlestick, current_candle: Candlestick) -> bool:
        """Check if current candle engulfs previous candle for bearish pattern."""
        # Current open must be above previous close
        # Current close must be below previous open
        return (
            current_candle.open_price > prev_candle.close_price and
            current_candle.close_price < prev_candle.open_price
        )
    
    def _calculate_bullish_confidence(self, prev_candle: Candlestick, current_candle: Candlestick) -> float:
        """Calculate confidence score for bullish engulfing pattern."""
        confidence_factors: List[float] = []
        
        # Factor 1: Body size ratio (larger engulfing body = higher confidence)
        body_ratio = float(current_candle.body_size / prev_candle.body_size)
        body_confidence = min(body_ratio / self.min_engulfment_ratio, 1.0)
        confidence_factors.append(body_confidence * 0.3)
        
        # Factor 2: Volume increase (if available and significant)
        volume_confidence = 0.2  # Default moderate confidence
        if current_candle.volume > prev_candle.volume:
            volume_ratio = float(current_candle.volume / prev_candle.volume)
            volume_confidence = min(volume_ratio / 1.5, 1.0) * 0.2
        confidence_factors.append(volume_confidence)
        
        # Factor 3: Body to range ratio (bodies should be significant)
        prev_body_ratio = float(prev_candle.body_size / prev_candle.total_range)
        curr_body_ratio = float(current_candle.body_size / current_candle.total_range)
        body_significance = (prev_body_ratio + curr_body_ratio) / 2
        confidence_factors.append(body_significance * 0.25)
        
        # Factor 4: Gap between candles (small gap is better for engulfing)
        gap_factor = 1.0
        if prev_candle.close_price != current_candle.open_price:
            gap_size = abs(float(current_candle.open_price - prev_candle.close_price))
            avg_body = float((prev_candle.body_size + current_candle.body_size) / 2)
            gap_ratio = gap_size / avg_body if avg_body > 0 else 0
            gap_factor = max(0.5, 1.0 - gap_ratio)  # Smaller gaps are better
        confidence_factors.append(gap_factor * 0.25)
        
        # Combine all factors
        total_confidence = sum(confidence_factors)
        return min(max(total_confidence, 0.0), 1.0)
    
    def _calculate_bearish_confidence(self, prev_candle: Candlestick, current_candle: Candlestick) -> float:
        """Calculate confidence score for bearish engulfing pattern."""
        # Same logic as bullish but for bearish patterns
        confidence_factors: List[float] = []
        
        # Factor 1: Body size ratio
        body_ratio = float(current_candle.body_size / prev_candle.body_size)
        body_confidence = min(body_ratio / self.min_engulfment_ratio, 1.0)
        confidence_factors.append(body_confidence * 0.3)
        
        # Factor 2: Volume increase
        volume_confidence = 0.2
        if current_candle.volume > prev_candle.volume:
            volume_ratio = float(current_candle.volume / prev_candle.volume)
            volume_confidence = min(volume_ratio / 1.5, 1.0) * 0.2
        confidence_factors.append(volume_confidence)
        
        # Factor 3: Body significance
        prev_body_ratio = float(prev_candle.body_size / prev_candle.total_range)
        curr_body_ratio = float(current_candle.body_size / current_candle.total_range)
        body_significance = (prev_body_ratio + curr_body_ratio) / 2
        confidence_factors.append(body_significance * 0.25)
        
        # Factor 4: Gap factor
        gap_factor = 1.0
        if prev_candle.close_price != current_candle.open_price:
            gap_size = abs(float(current_candle.open_price - prev_candle.close_price))
            avg_body = float((prev_candle.body_size + current_candle.body_size) / 2)
            gap_ratio = gap_size / avg_body if avg_body > 0 else 0
            gap_factor = max(0.5, 1.0 - gap_ratio)
        confidence_factors.append(gap_factor * 0.25)
        
        total_confidence = sum(confidence_factors)
        return min(max(total_confidence, 0.0), 1.0)
    
    def validate_pattern(self, pattern: Pattern) -> bool:
        """
        Validate that a detected pattern meets quality criteria.
        
        Args:
            pattern: Pattern to validate
            
        Returns:
            True if pattern is valid, False otherwise
        """
        if len(pattern.candles) != 2:
            return False
        
        prev_candle, current_candle = pattern.candles
        
        # Check minimum body sizes
        min_body_size = max(
            float(prev_candle.total_range) * self.min_body_ratio,
            float(current_candle.total_range) * self.min_body_ratio
        )
        
        if (float(prev_candle.body_size) < min_body_size or 
            float(current_candle.body_size) < min_body_size):
            return False
        
        # Check pattern-specific criteria
        if pattern.pattern_type == PatternType.BULLISH_ENGULFING:
            return self._is_bullish_engulfment(prev_candle, current_candle)
        elif pattern.pattern_type == PatternType.BEARISH_ENGULFING:
            return self._is_bearish_engulfment(prev_candle, current_candle)
        
        return True
    
    def get_pattern_strength(self, pattern: Pattern) -> str:
        """Get human-readable pattern strength description."""
        if pattern.confidence >= 0.9:
            return "Very Strong"
        elif pattern.confidence >= 0.75:
            return "Strong"
        elif pattern.confidence >= 0.5:
            return "Moderate"
        else:
            return "Weak"
