"""
Logging utilities for structured logging throughout the application.
"""

import logging
import sys
from typing import Any, Dict, Optional
from datetime import datetime


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with structured information.
        
        Args:
            record: Log record to format
            
        Returns:
            Formatted log message
        """
        # Create structured log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, "extra_fields"):
            log_entry.update(record.extra_fields)
        
        return str(log_entry)


class AppLogger:
    """Application logger with structured logging."""
    
    def __init__(self, name: str, level: str = "INFO"):
        """Initialize logger.
        
        Args:
            name: Logger name
            level: Logging level
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self) -> None:
        """Set up log handlers."""
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(console_handler)
        
        # File handler (optional)
        # file_handler = logging.FileHandler("app.log")
        # file_handler.setFormatter(StructuredFormatter())
        # self.logger.addHandler(file_handler)
    
    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message.
        
        Args:
            message: Log message
            **kwargs: Additional fields
        """
        self.logger.info(message, extra={"extra_fields": kwargs})
    
    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message.
        
        Args:
            message: Log message
            **kwargs: Additional fields
        """
        self.logger.error(message, extra={"extra_fields": kwargs})
    
    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message.
        
        Args:
            message: Log message
            **kwargs: Additional fields
        """
        self.logger.warning(message, extra={"extra_fields": kwargs})
    
    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message.
        
        Args:
            message: Log message
            **kwargs: Additional fields
        """
        self.logger.debug(message, extra={"extra_fields": kwargs})
    
    def exception(self, message: str, **kwargs: Any) -> None:
        """Log exception with traceback.
        
        Args:
            message: Log message
            **kwargs: Additional fields
        """
        self.logger.exception(message, extra={"extra_fields": kwargs})


def setup_logging(level: str = "INFO") -> AppLogger:
    """Set up application logging.
    
    Args:
        level: Logging level
        
    Returns:
        Configured logger instance
    """
    return AppLogger("btc_futures_app", level)


# Default logger instance
logger = setup_logging()
