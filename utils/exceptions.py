"""
Custom exception classes for the application.
"""


class BTCFuturesAppError(Exception):
    """Base exception class for BTC Futures app."""
    pass


class APIError(BTCFuturesAppError):
    """Exception raised for API-related errors."""
    pass


class BinanceAPIError(APIError):
    """Exception raised for Binance API specific errors."""
    
    def __init__(self, message: str, error_code: str = None, status_code: int = None):
        super().__init__(message)
        self.error_code = error_code
        self.status_code = status_code


class CacheError(BTCFuturesAppError):
    """Exception raised for cache-related errors."""
    pass


class DataValidationError(BTCFuturesAppError):
    """Exception raised for data validation errors."""
    pass


class SignalEngineError(BTCFuturesAppError):
    """Exception raised for signal engine errors."""
    pass


class PatternDetectionError(SignalEngineError):
    """Exception raised for pattern detection errors."""
    pass


class ConfigurationError(BTCFuturesAppError):
    """Exception raised for configuration errors."""
    pass


class RateLimitError(APIError):
    """Exception raised when API rate limits are exceeded."""
    
    def __init__(self, message: str, retry_after: int = None):
        super().__init__(message)
        self.retry_after = retry_after
