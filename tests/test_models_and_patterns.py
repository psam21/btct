"""
Comprehensive unit tests for data models and patterns.

Tests the data models (FR001, FR002) and pattern detection logic (FR007, FR008).
"""

import pytest
from datetime import datetime
from decimal import Decimal

from apis.models import (
    Candlestick, MarketData, Signal, Pattern, AnalysisResult,
    SignalType, PatternType, ConfidenceLevel
)
from logic.patterns import PatternDetector


class TestCandlestickModel:
    """Test suite for Candlestick data model."""
    
    def test_candlestick_creation(self):
        """Test creating a Candlestick with valid data."""
        timestamp = datetime(2024, 1, 1, 12, 0, 0)
        candlestick = Candlestick(
            timestamp=timestamp,
            open_price=Decimal("45000.00"),
            high_price=Decimal("45500.00"),
            low_price=Decimal("44800.00"),
            close_price=Decimal("45200.00"),
            volume=Decimal("123.45"),
            symbol="BTCUSDT"
        )
        
        assert candlestick.timestamp == timestamp
        assert candlestick.open_price == Decimal("45000.00")
        assert candlestick.high_price == Decimal("45500.00")
        assert candlestick.low_price == Decimal("44800.00")
        assert candlestick.close_price == Decimal("45200.00")
        assert candlestick.volume == Decimal("123.45")
        assert candlestick.symbol == "BTCUSDT"
    
    def test_bullish_candlestick_properties(self):
        """Test properties of a bullish candlestick."""
        candlestick = Candlestick(
            timestamp=datetime.now(),
            open_price=Decimal("45000.00"),
            high_price=Decimal("45500.00"),
            low_price=Decimal("44800.00"),
            close_price=Decimal("45200.00"),  # close > open = bullish
            volume=Decimal("123.45"),
            symbol="BTCUSDT"
        )
        
        assert candlestick.is_bullish is True
        assert candlestick.is_bearish is False
        assert candlestick.body_size == Decimal("200.00")  # |45200 - 45000|
        assert candlestick.upper_shadow == Decimal("300.00")  # 45500 - 45200
        assert candlestick.lower_shadow == Decimal("200.00")  # 45000 - 44800
        assert candlestick.total_range == Decimal("700.00")  # 45500 - 44800
    
    def test_bearish_candlestick_properties(self):
        """Test properties of a bearish candlestick."""
        candlestick = Candlestick(
            timestamp=datetime.now(),
            open_price=Decimal("45200.00"),
            high_price=Decimal("45500.00"),
            low_price=Decimal("44800.00"),
            close_price=Decimal("45000.00"),  # close < open = bearish
            volume=Decimal("123.45"),
            symbol="BTCUSDT"
        )
        
        assert candlestick.is_bullish is False
        assert candlestick.is_bearish is True
        assert candlestick.body_size == Decimal("200.00")  # |45000 - 45200|
        assert candlestick.upper_shadow == Decimal("300.00")  # 45500 - 45200
        assert candlestick.lower_shadow == Decimal("200.00")  # 45000 - 44800
        assert candlestick.total_range == Decimal("700.00")  # 45500 - 44800
    
    def test_doji_candlestick_properties(self):
        """Test properties of a doji candlestick (open = close)."""
        candlestick = Candlestick(
            timestamp=datetime.now(),
            open_price=Decimal("45000.00"),
            high_price=Decimal("45200.00"),
            low_price=Decimal("44800.00"),
            close_price=Decimal("45000.00"),  # close = open = doji
            volume=Decimal("123.45"),
            symbol="BTCUSDT"
        )
        
        assert candlestick.is_bullish is False
        assert candlestick.is_bearish is False
        assert candlestick.body_size == Decimal("0.00")
        assert candlestick.upper_shadow == Decimal("200.00")  # 45200 - 45000
        assert candlestick.lower_shadow == Decimal("200.00")  # 45000 - 44800
        assert candlestick.total_range == Decimal("400.00")  # 45200 - 44800
    
    def test_candlestick_string_representation(self):
        """Test string representation of candlestick."""
        candlestick = Candlestick(
            timestamp=datetime(2024, 1, 1),
            open_price=Decimal("45000.00"),
            high_price=Decimal("45500.00"),
            low_price=Decimal("44800.00"),
            close_price=Decimal("45200.00"),
            volume=Decimal("123.45"),
            symbol="BTCUSDT"
        )
        
        str_repr = str(candlestick)
        assert "🟢" in str_repr  # Bullish indicator
        assert "2024-01-01" in str_repr
        assert "45000" in str_repr
        assert "45500" in str_repr
        assert "44800" in str_repr
        assert "45200" in str_repr


class TestPatternModel:
    """Test suite for Pattern data model."""
    
    def test_pattern_creation(self):
        """Test creating a Pattern with valid data."""
        candles = [
            Candlestick(
                timestamp=datetime(2024, 1, 1),
                open_price=Decimal("45000.00"),
                high_price=Decimal("45100.00"),
                low_price=Decimal("44900.00"),
                close_price=Decimal("44950.00"),  # Bearish
                volume=Decimal("100.00"),
                symbol="BTCUSDT"
            ),
            Candlestick(
                timestamp=datetime(2024, 1, 2),
                open_price=Decimal("44900.00"),
                high_price=Decimal("45500.00"),
                low_price=Decimal("44800.00"),
                close_price=Decimal("45400.00"),  # Bullish engulfing
                volume=Decimal("200.00"),
                symbol="BTCUSDT"
            )
        ]
        
        pattern = Pattern(
            pattern_type=PatternType.BULLISH_ENGULFING,
            confidence=0.85,
            confidence_level=ConfidenceLevel.HIGH,
            timestamp=datetime(2024, 1, 2),
            candles=candles,
            description="Strong bullish engulfing pattern"
        )
        
        assert pattern.pattern_type == PatternType.BULLISH_ENGULFING
        assert pattern.confidence == 0.85
        assert pattern.confidence_level == ConfidenceLevel.HIGH
        assert len(pattern.candles) == 2
        assert pattern.description == "Strong bullish engulfing pattern"
    
    def test_pattern_validation(self):
        """Test pattern validation criteria."""
        # Create valid pattern using Pattern class directly
        # Bearish candle (first)
        bearish_candle = Candlestick(
            timestamp=datetime(2024, 1, 1),
            open_price=Decimal("45000.00"),
            high_price=Decimal("45010.00"),  # Total range: 50 points
            low_price=Decimal("44960.00"),   
            close_price=Decimal("44970.00"), # 30-point bearish body (60% ratio exactly)  
            volume=Decimal("100.00"),
            symbol="BTCUSDT"
        )
        
        # Bullish candle (second) - must properly engulf the previous one
        bullish_candle = Candlestick(
            timestamp=datetime(2024, 1, 2),
            open_price=Decimal("44960.00"),  # Opens below previous close (44970) - required for engulfing
            high_price=Decimal("45200.00"),  # Total range: 270 points
            low_price=Decimal("44930.00"),
            close_price=Decimal("45020.00"), # Closes above previous open (45000) - required for engulfing
            volume=Decimal("200.00"),
            symbol="BTCUSDT"
        )
        
        # Create pattern directly
        pattern = Pattern(
            pattern_type=PatternType.BULLISH_ENGULFING,
            confidence=0.85,
            confidence_level=ConfidenceLevel.HIGH,
            timestamp=datetime(2024, 1, 2),
            candles=[bearish_candle, bullish_candle],
            description="Bullish engulfing pattern detected"
        )
        
        # Test pattern basic validation
        assert pattern.pattern_type == PatternType.BULLISH_ENGULFING
        assert len(pattern.candles) == 2
        assert pattern.confidence > 0.0
class TestSignalModel:
    """Test suite for Signal data model."""
    
    def test_signal_creation(self):
        """Test creating a Signal with valid data."""
        signal = Signal(
            id="signal_001",
            timestamp=datetime(2024, 1, 1, 15, 30, 0),
            signal_type=SignalType.GO_LONG,
            pattern_type=PatternType.BULLISH_ENGULFING,
            entry_price=Decimal("45200.00"),
            confidence=0.85,
            confidence_level=ConfidenceLevel.HIGH,
            commentary="Strong bullish engulfing pattern detected"
        )
        
        assert signal.id == "signal_001"
        assert signal.signal_type == SignalType.GO_LONG
        assert signal.pattern_type == PatternType.BULLISH_ENGULFING
        assert signal.entry_price == Decimal("45200.00")
        assert signal.confidence == 0.85
        assert signal.confidence_level == ConfidenceLevel.HIGH
        assert "bullish" in signal.commentary.lower()
    
    def test_signal_validation(self):
        """Test signal validation rules."""
        # Test invalid confidence
        with pytest.raises(ValueError, match="Confidence must be between 0.0 and 1.0"):
            Signal(
                id="signal_001",
                timestamp=datetime.now(),
                signal_type=SignalType.GO_LONG,
                pattern_type=PatternType.BULLISH_ENGULFING,
                entry_price=Decimal("45200.00"),
                confidence=1.5,  # Invalid
                confidence_level=ConfidenceLevel.HIGH,
                commentary="Test signal"
            )
        
        # Test invalid entry price
        with pytest.raises(ValueError, match="Entry price must be positive"):
            Signal(
                id="signal_002",
                timestamp=datetime.now(),
                signal_type=SignalType.GO_LONG,
                pattern_type=PatternType.BULLISH_ENGULFING,
                entry_price=Decimal("-100.00"),  # Invalid
                confidence=0.85,
                confidence_level=ConfidenceLevel.HIGH,
                commentary="Test signal"
            )


class TestMarketDataModel:
    """Test suite for MarketData data model."""
    
    def test_market_data_creation(self):
        """Test creating MarketData with valid data."""
        candles = [
            Candlestick(
                timestamp=datetime(2024, 1, 1),
                open_price=Decimal("45000.00"),
                high_price=Decimal("45500.00"),
                low_price=Decimal("44800.00"),
                close_price=Decimal("45200.00"),
                volume=Decimal("123.45"),
                symbol="BTCUSDT"
            ),
            Candlestick(
                timestamp=datetime(2024, 1, 2),
                open_price=Decimal("45200.00"),
                high_price=Decimal("45800.00"),
                low_price=Decimal("45100.00"),
                close_price=Decimal("45600.00"),
                volume=Decimal("234.56"),
                symbol="BTCUSDT"
            )
        ]
        
        patterns = [
            Pattern(
                pattern_type=PatternType.BULLISH_ENGULFING,
                confidence=0.85,
                confidence_level=ConfidenceLevel.HIGH,
                timestamp=datetime(2024, 1, 2),
                candles=candles,
                description="Bullish engulfing pattern"
            )
        ]
        
        signals = [
            Signal(
                id="signal_001",
                timestamp=datetime(2024, 1, 2),
                signal_type=SignalType.GO_LONG,
                pattern_type=PatternType.BULLISH_ENGULFING,
                entry_price=Decimal("45600.00"),
                confidence=0.85,
                confidence_level=ConfidenceLevel.HIGH,
                commentary="Bullish signal"
            )
        ]
        
        market_data = MarketData(
            symbol="BTCUSDT",
            timeframe="1w",
            candles=candles,
            patterns=patterns,
            signals=signals,
            last_updated=datetime(2024, 1, 2, 16, 0, 0)
        )
        
        assert market_data.symbol == "BTCUSDT"
        assert market_data.timeframe == "1w"
        assert len(market_data.candles) == 2
        assert len(market_data.patterns) == 1
        assert len(market_data.signals) == 1
        assert market_data.latest_candle == candles[1]
        assert market_data.latest_signal == signals[0]
    
    def test_market_data_properties(self):
        """Test MarketData properties."""
        candles = [
            Candlestick(
                timestamp=datetime(2024, 1, 1),
                open_price=Decimal("45000.00"),
                high_price=Decimal("45500.00"),
                low_price=Decimal("44800.00"),
                close_price=Decimal("45200.00"),
                volume=Decimal("123.45"),
                symbol="BTCUSDT"
            ),
            Candlestick(
                timestamp=datetime(2024, 1, 2),
                open_price=Decimal("45200.00"),
                high_price=Decimal("45800.00"),
                low_price=Decimal("45100.00"),
                close_price=Decimal("45600.00"),
                volume=Decimal("234.56"),
                symbol="BTCUSDT"
            )
        ]
        
        market_data = MarketData(
            symbol="BTCUSDT",
            timeframe="1w",
            candles=candles,
            patterns=[],
            signals=[],
            last_updated=datetime.now()
        )
        
        # Test latest_candle property
        assert market_data.latest_candle == candles[1]  # Most recent
        
        # Test with empty candles
        empty_market_data = MarketData(
            symbol="BTCUSDT",
            timeframe="1w",
            candles=[],
            patterns=[],
            signals=[],
            last_updated=datetime.now()
        )
        
        assert empty_market_data.latest_candle is None
        assert empty_market_data.latest_signal is None
    
    def test_market_data_date_filtering(self):
        """Test filtering candles by date range."""
        candles = [
            Candlestick(
                timestamp=datetime(2024, 1, 1),
                open_price=Decimal("45000.00"),
                high_price=Decimal("45500.00"),
                low_price=Decimal("44800.00"),
                close_price=Decimal("45200.00"),
                volume=Decimal("123.45"),
                symbol="BTCUSDT"
            ),
            Candlestick(
                timestamp=datetime(2024, 1, 15),
                open_price=Decimal("45200.00"),
                high_price=Decimal("45800.00"),
                low_price=Decimal("45100.00"),
                close_price=Decimal("45600.00"),
                volume=Decimal("234.56"),
                symbol="BTCUSDT"
            ),
            Candlestick(
                timestamp=datetime(2024, 2, 1),
                open_price=Decimal("45600.00"),
                high_price=Decimal("46000.00"),
                low_price=Decimal("45400.00"),
                close_price=Decimal("45800.00"),
                volume=Decimal("345.67"),
                symbol="BTCUSDT"
            )
        ]
        
        market_data = MarketData(
            symbol="BTCUSDT",
            timeframe="1w",
            candles=candles,
            patterns=[],
            signals=[],
            last_updated=datetime.now()
        )
        
        # Filter for January 2024
        january_candles = market_data.get_candles_by_date_range(
            datetime(2024, 1, 1),
            datetime(2024, 1, 31)
        )
        
        assert len(january_candles) == 2
        assert all(candle.timestamp.month == 1 for candle in january_candles)
        
        # Filter for specific date range
        mid_january_candles = market_data.get_candles_by_date_range(
            datetime(2024, 1, 10),
            datetime(2024, 1, 20)
        )
        
        assert len(mid_january_candles) == 1
        assert mid_january_candles[0].timestamp == datetime(2024, 1, 15)


class TestAnalysisResultModel:
    """Test suite for AnalysisResult data model."""
    
    def test_analysis_result_creation(self):
        """Test creating AnalysisResult with valid data."""
        result = AnalysisResult(
            timestamp=datetime(2024, 1, 1, 16, 0, 0),
            symbol="BTCUSDT",
            total_candles_analyzed=100,
            patterns_detected=5,
            signals_generated=3,
            analysis_duration_ms=250.5,
            success=True
        )
        
        assert result.symbol == "BTCUSDT"
        assert result.total_candles_analyzed == 100
        assert result.patterns_detected == 5
        assert result.signals_generated == 3
        assert result.analysis_duration_ms == 250.5
        assert result.success is True
        assert result.error_message is None
    
    def test_analysis_result_rates(self):
        """Test AnalysisResult rate calculations."""
        result = AnalysisResult(
            timestamp=datetime.now(),
            symbol="BTCUSDT",
            total_candles_analyzed=100,
            patterns_detected=10,
            signals_generated=5,
            analysis_duration_ms=300.0,
            success=True
        )
        
        assert result.pattern_detection_rate == 0.1  # 10/100
        assert result.signal_generation_rate == 0.5  # 5/10 patterns generated signals
        
        # Test with zero candles
        zero_result = AnalysisResult(
            timestamp=datetime.now(),
            symbol="BTCUSDT",
            total_candles_analyzed=0,
            patterns_detected=0,
            signals_generated=0,
            analysis_duration_ms=0.0,
            success=False,
            error_message="No data available"
        )
        
        assert zero_result.pattern_detection_rate == 0.0
        assert zero_result.signal_generation_rate == 0.0
    
    def test_analysis_result_with_error(self):
        """Test AnalysisResult with error conditions."""
        error_result = AnalysisResult(
            timestamp=datetime.now(),
            symbol="BTCUSDT",
            total_candles_analyzed=0,
            patterns_detected=0,
            signals_generated=0,
            analysis_duration_ms=0.0,
            success=False,
            error_message="API connection failed"
        )
        
        assert error_result.success is False
        assert error_result.error_message == "API connection failed"
        assert error_result.pattern_detection_rate == 0.0


class TestEnums:
    """Test suite for enum types."""
    
    def test_signal_type_enum(self):
        """Test SignalType enum values."""
        assert SignalType.GO_LONG.value == "GO_LONG"
        assert SignalType.GO_SHORT.value == "GO_SHORT"
        assert SignalType.HOLD.value == "HOLD"
    
    def test_pattern_type_enum(self):
        """Test PatternType enum values."""
        assert PatternType.BULLISH_ENGULFING.value == "BULLISH_ENGULFING"
        assert PatternType.BEARISH_ENGULFING.value == "BEARISH_ENGULFING"
        assert PatternType.NO_PATTERN.value == "NO_PATTERN"
    
    def test_confidence_level_enum(self):
        """Test ConfidenceLevel enum values."""
        assert ConfidenceLevel.LOW.value == "LOW"
        assert ConfidenceLevel.MEDIUM.value == "MEDIUM"
        assert ConfidenceLevel.HIGH.value == "HIGH"
        assert ConfidenceLevel.VERY_HIGH.value == "VERY_HIGH"


class TestPatternDetectors:
    """Test suite for pattern detection logic."""
    
    def test_bullish_engulfing_detection(self):
        """Test bullish engulfing pattern detection."""
        detector = PatternDetector()
        
        # Create bullish engulfing pattern
        bearish_candle = Candlestick(
            timestamp=datetime(2024, 1, 1),
            open_price=Decimal("45200.00"),
            high_price=Decimal("45300.00"),
            low_price=Decimal("45000.00"),
            close_price=Decimal("45100.00"),  # Bearish
            volume=Decimal("100.00"),
            symbol="BTCUSDT"
        )
        
        bullish_candle = Candlestick(
            timestamp=datetime(2024, 1, 2),
            open_price=Decimal("45000.00"),  # Opens below previous close
            high_price=Decimal("45500.00"),
            low_price=Decimal("44900.00"),
            close_price=Decimal("45400.00"),  # Closes above previous open
            volume=Decimal("200.00"),  # Higher volume
            symbol="BTCUSDT"
        )
        
        # Test individual pattern detection
        pattern = detector.detect_bullish_engulfing(bearish_candle, bullish_candle)
        
        assert pattern is not None
        assert pattern.pattern_type == PatternType.BULLISH_ENGULFING
        assert pattern.confidence > 0.0
        assert len(pattern.candles) == 2
        assert "bullish" in pattern.description.lower()
    
    def test_bearish_engulfing_detection(self):
        """Test bearish engulfing pattern detection."""
        detector = PatternDetector()
        
        # Create bearish engulfing pattern
        bullish_candle = Candlestick(
            timestamp=datetime(2024, 1, 1),
            open_price=Decimal("45000.00"),
            high_price=Decimal("45300.00"),
            low_price=Decimal("44900.00"),
            close_price=Decimal("45200.00"),  # Bullish
            volume=Decimal("100.00"),
            symbol="BTCUSDT"
        )
        
        bearish_candle = Candlestick(
            timestamp=datetime(2024, 1, 2),
            open_price=Decimal("45300.00"),  # Opens above previous close
            high_price=Decimal("45400.00"),
            low_price=Decimal("44800.00"),
            close_price=Decimal("44900.00"),  # Closes below previous open
            volume=Decimal("200.00"),  # Higher volume
            symbol="BTCUSDT"
        )
        
        # Test individual pattern detection
        pattern = detector.detect_bearish_engulfing(bullish_candle, bearish_candle)
        
        assert pattern is not None
        assert pattern.pattern_type == PatternType.BEARISH_ENGULFING
        assert pattern.confidence > 0.0
        assert len(pattern.candles) == 2
        assert "bearish" in pattern.description.lower()
    
    def test_pattern_detector_integration(self):
        """Test PatternDetector with multiple patterns."""
        detector = PatternDetector()
        
        # Test with bullish engulfing pattern
        bearish_candle = Candlestick(
            timestamp=datetime(2024, 1, 1),
            open_price=Decimal("45200.00"),
            high_price=Decimal("45300.00"),
            low_price=Decimal("45000.00"),
            close_price=Decimal("45100.00"),
            volume=Decimal("100.00"),
            symbol="BTCUSDT"
        )
        
        bullish_candle = Candlestick(
            timestamp=datetime(2024, 1, 2),
            open_price=Decimal("45000.00"),
            high_price=Decimal("45500.00"),
            low_price=Decimal("44900.00"),
            close_price=Decimal("45400.00"),
            volume=Decimal("200.00"),
            symbol="BTCUSDT"
        )
        
        candles = [bearish_candle, bullish_candle]
        patterns = detector.detect_patterns(candles)
        
        assert len(patterns) >= 1
        assert any(p.pattern_type == PatternType.BULLISH_ENGULFING for p in patterns)
    
    def test_no_pattern_detection(self):
        """Test when no patterns are detected."""
        detector = PatternDetector()
        
        # Create non-engulfing pattern
        candle1 = Candlestick(
            timestamp=datetime(2024, 1, 1),
            open_price=Decimal("45000.00"),
            high_price=Decimal("45200.00"),
            low_price=Decimal("44900.00"),
            close_price=Decimal("45100.00"),
            volume=Decimal("100.00"),
            symbol="BTCUSDT"
        )
        
        candle2 = Candlestick(
            timestamp=datetime(2024, 1, 2),
            open_price=Decimal("45100.00"),
            high_price=Decimal("45300.00"),
            low_price=Decimal("45000.00"),
            close_price=Decimal("45200.00"),
            volume=Decimal("100.00"),
            symbol="BTCUSDT"
        )
        
        # Test individual detection
        bullish_pattern = detector.detect_bullish_engulfing(candle1, candle2)
        bearish_pattern = detector.detect_bearish_engulfing(candle1, candle2)
        
        # These should not be engulfing patterns
        assert bullish_pattern is None
        assert bearish_pattern is None
        
        # Test full pattern detection
        patterns = detector.detect_patterns([candle1, candle2])
        assert len(patterns) == 0
    
    def test_pattern_validation(self):
        """Test pattern validation logic."""
        detector = PatternDetector()
        
        # Create a valid bullish engulfing pattern with larger bodies that meet validation criteria
        bearish_candle = Candlestick(
            timestamp=datetime(2024, 1, 1),
            open_price=Decimal("45000.00"),
            high_price=Decimal("45050.00"),  # Small total range
            low_price=Decimal("44960.00"),   # 90 point range
            close_price=Decimal("44970.00"), # 30-point bearish body (33% ratio - still not enough)
            volume=Decimal("100.00"),
            symbol="BTCUSDT"
        )
        
        # Adjust to create bigger body ratio for bearish candle
        bearish_candle = Candlestick(
            timestamp=datetime(2024, 1, 1),
            open_price=Decimal("45000.00"),
            high_price=Decimal("45020.00"),  # Very small total range (60 points)
            low_price=Decimal("44960.00"),   
            close_price=Decimal("44965.00"), # 35-point bearish body (58% ratio - close but still under 60%)
            volume=Decimal("100.00"),
            symbol="BTCUSDT"
        )
        
        # Make bearish candle meet the 60% requirement exactly
        bearish_candle = Candlestick(
            timestamp=datetime(2024, 1, 1),
            open_price=Decimal("45000.00"),
            high_price=Decimal("45010.00"),  # Total range: 50 points
            low_price=Decimal("44960.00"),   
            close_price=Decimal("44970.00"), # 30-point bearish body (60% ratio exactly)  
            volume=Decimal("100.00"),
            symbol="BTCUSDT"
        )
        
        bullish_candle = Candlestick(
            timestamp=datetime(2024, 1, 2),
            open_price=Decimal("44965.00"),  # Opens below previous close (44970) 
            high_price=Decimal("45015.00"),  # Total range: 50 points (45015 - 44965)
            low_price=Decimal("44965.00"),   # Same as open for clean calculation
            close_price=Decimal("45005.00"), # 40-point bullish body (80% ratio), closes above previous open (45000)
            volume=Decimal("200.00"),
            symbol="BTCUSDT"
        )
        
        pattern = detector.detect_bullish_engulfing(bearish_candle, bullish_candle)
        assert pattern is not None
        
        # Test pattern validation
        is_valid = detector.validate_pattern(pattern)
        
        # Both candles should have significant body ratios now
        bearish_body_ratio = float(bearish_candle.body_size / bearish_candle.total_range)
        bullish_body_ratio = float(bullish_candle.body_size / bullish_candle.total_range)
        
        # Both should meet minimum body ratio requirement (60%)
        assert bearish_body_ratio >= detector.min_body_ratio, f"Bearish body ratio {bearish_body_ratio:.2f} < {detector.min_body_ratio}"
        assert bullish_body_ratio >= detector.min_body_ratio, f"Bullish body ratio {bullish_body_ratio:.2f} < {detector.min_body_ratio}"
        assert is_valid is True
        
        # Test pattern strength description
        strength = detector.get_pattern_strength(pattern)
        assert strength in ["Weak", "Moderate", "Strong", "Very Strong"]
    
    def test_insufficient_candles(self):
        """Test pattern detection with insufficient candles."""
        detector = PatternDetector()
        
        # Test with empty list
        patterns = detector.detect_patterns([])
        assert len(patterns) == 0
        
        # Test with single candle
        single_candle = [
            Candlestick(
                timestamp=datetime(2024, 1, 1),
                open_price=Decimal("45000.00"),
                high_price=Decimal("45200.00"),
                low_price=Decimal("44900.00"),
                close_price=Decimal("45100.00"),
                volume=Decimal("100.00"),
                symbol="BTCUSDT"
            )
        ]
        patterns = detector.detect_patterns(single_candle)
        assert len(patterns) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
