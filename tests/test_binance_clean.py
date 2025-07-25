"""
Unit tests for Binance API integration module.

Tests the live data fetching functionality (FR015).
"""

import pytest
from unittest.mock import patch, Mock
import requests
from datetime import datetime
from decimal import Decimal

from apis.binance import fetch_market_data, convert_klines_to_candlesticks
from apis.models import Candlestick, MarketData


class TestBinanceAPIBasics:
    """Test suite for basic Binance API functions."""
    
    def test_convert_klines_to_candlesticks(self):
        """Test converting klines data to candlesticks."""
        # Sample klines data from Binance API format
        sample_klines = [
            [
                1640995200000,  # Open time
                "45000.00",     # Open price
                "45500.00",     # High price
                "44800.00",     # Low price
                "45200.00",     # Close price
                "123.45",       # Volume
                1640998799999,  # Close time
                "5555555.12",   # Quote asset volume
                1234,           # Number of trades
                "61.72",        # Taker buy base asset volume
                "2777777.56",   # Taker buy quote asset volume
                "0"             # Unused field
            ]
        ]
        
        result = convert_klines_to_candlesticks(sample_klines)
        
        assert len(result) == 1
        
        # Test candlestick properties
        candle = result[0]
        assert isinstance(candle, Candlestick)
        assert candle.timestamp == datetime.fromtimestamp(1640995200000 / 1000)
        assert candle.open_price == Decimal("45000.00")
        assert candle.high_price == Decimal("45500.00")
        assert candle.low_price == Decimal("44800.00")
        assert candle.close_price == Decimal("45200.00")
        assert candle.volume == Decimal("123.45")
    
    def test_convert_empty_klines(self):
        """Test converting empty klines data."""
        result = convert_klines_to_candlesticks([])
        assert result == []
    
    def test_convert_invalid_klines_format(self):
        """Test converting klines with invalid format."""
        invalid_klines = [
            ["invalid", "data", "format"]  # Not enough fields
        ]
        
        # The function should handle this gracefully
        result = convert_klines_to_candlesticks(invalid_klines)
        assert result == []  # Should return empty list, not crash


class TestFetchMarketData:
    """Test suite for fetch_market_data function."""
    
    @patch('apis.binance.requests.get')
    def test_fetch_market_data_success(self, mock_get):
        """Test successful market data fetch."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            [
                1640995200000, "45000.00", "45500.00", "44800.00", "45200.00",
                "123.45", 1640998799999, "5555555.12", 1234, "61.72", "2777777.56", "0"
            ]
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = fetch_market_data("BTCUSDT", "1h", 10)
        
        # Verify API call
        expected_url = "https://api.binance.com/api/v3/klines"
        expected_params = {
            "symbol": "BTCUSDT",
            "interval": "1h",
            "limit": 10
        }
        mock_get.assert_called_once_with(expected_url, params=expected_params, timeout=10)
        
        # Verify result
        assert isinstance(result, MarketData)
        assert result.symbol == "BTCUSDT"
        assert result.timeframe == "1h"
        assert len(result.candles) == 1
        assert isinstance(result.candles[0], Candlestick)
    
    @patch('apis.binance.requests.get')
    def test_fetch_market_data_http_error(self, mock_get):
        """Test fetch_market_data with HTTP error."""
        # Mock HTTP error response
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("HTTP Error")
        mock_get.return_value = mock_response
        
        result = fetch_market_data("INVALID", "1h")
        
        # Should return None on error
        assert result is None
    
    @patch('apis.binance.requests.get')
    def test_fetch_market_data_connection_error(self, mock_get):
        """Test fetch_market_data with connection error."""
        # Mock connection error
        mock_get.side_effect = requests.ConnectionError("Connection failed")
        
        result = fetch_market_data("BTCUSDT", "1h")
        
        # Should return None on error
        assert result is None
    
    @patch('apis.binance.requests.get')
    def test_fetch_market_data_timeout_error(self, mock_get):
        """Test fetch_market_data with timeout error."""
        # Mock timeout error
        mock_get.side_effect = requests.Timeout("Request timed out")
        
        result = fetch_market_data("BTCUSDT", "1h")
        
        # Should return None on error
        assert result is None
    
    @patch('apis.binance.requests.get')
    def test_fetch_market_data_default_parameters(self, mock_get):
        """Test fetch_market_data with default parameters."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = fetch_market_data()
        
        # Verify default parameters were used
        expected_params = {
            "symbol": "BTCUSDT",
            "interval": "1w",
            "limit": 100
        }
        mock_get.assert_called_once_with(
            "https://api.binance.com/api/v3/klines",
            params=expected_params,
            timeout=10
        )


class TestBinanceAPIIntegration:
    """Integration tests for Binance API module."""
    
    @patch('apis.binance.requests.get')
    def test_complete_data_fetch_workflow(self, mock_get):
        """Test complete data fetching workflow."""
        # Mock successful API response with realistic data
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            [
                1640995200000, "45000.00", "45500.00", "44800.00", "45200.00",
                "123.45", 1640998799999, "5555555.12", 1234, "61.72", "2777777.56", "0"
            ],
            [
                1640998800000, "45200.00", "45800.00", "45100.00", "45600.00",
                "234.56", 1641002399999, "10666666.24", 2345, "117.28", "5333333.12", "0"
            ]
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Fetch market data
        result = fetch_market_data("BTCUSDT", "1h", 50)
        
        # Verify data structure and quality
        assert isinstance(result, MarketData)
        assert result.symbol == "BTCUSDT"
        assert result.timeframe == "1h"
        assert len(result.candles) == 2
        
        # Verify candlestick data quality
        for candle in result.candles:
            assert isinstance(candle, Candlestick)
            assert candle.open_price > 0
            assert candle.high_price >= candle.open_price
            assert candle.high_price >= candle.close_price
            assert candle.low_price <= candle.open_price
            assert candle.low_price <= candle.close_price
            assert candle.volume >= 0
            assert isinstance(candle.timestamp, datetime)
        
        # Verify candlesticks are in chronological order
        timestamps = [candle.timestamp for candle in result.candles]
        assert timestamps == sorted(timestamps)
    
    def test_data_conversion_accuracy(self):
        """Test data conversion accuracy with various inputs."""
        # Test with different numeric formats
        test_cases = [
            {
                "input": [1640995200000, "45000", "45500", "44800", "45200", "123"],
                "expected_open": Decimal("45000"),
                "expected_high": Decimal("45500"),
                "expected_low": Decimal("44800"),
                "expected_close": Decimal("45200"),
                "expected_volume": Decimal("123")
            },
            {
                "input": [1640995200000, "45000.50", "45500.75", "44800.25", "45200.00", "123.456789"],
                "expected_open": Decimal("45000.50"),
                "expected_high": Decimal("45500.75"),
                "expected_low": Decimal("44800.25"),
                "expected_close": Decimal("45200.00"),
                "expected_volume": Decimal("123.456789")
            }
        ]
        
        for case in test_cases:
            # Extend input to full kline format
            full_kline = case["input"] + [1640998799999, "5555555.12", 1234, "61.72", "2777777.56", "0"]
            
            result = convert_klines_to_candlesticks([full_kline])
            
            assert len(result) == 1
            candle = result[0]
            
            assert candle.open_price == case["expected_open"]
            assert candle.high_price == case["expected_high"]
            assert candle.low_price == case["expected_low"]
            assert candle.close_price == case["expected_close"]
            assert candle.volume == case["expected_volume"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
