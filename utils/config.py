"""
Configuration management utilities.

Handles application configuration from environment variables and config files.
"""

import os
from typing import Any, Dict, Optional
from dotenv import load_dotenv


class Config:
    """Application configuration manager."""
    
    def __init__(self, env_file: Optional[str] = None):
        """Initialize configuration.
        
        Args:
            env_file: Path to .env file (optional)
        """
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()  # Load from default .env if it exists
    
    @property
    def binance_api_key(self) -> Optional[str]:
        """Get Binance API key."""
        return os.getenv("BINANCE_API_KEY")
    
    @property
    def binance_secret_key(self) -> Optional[str]:
        """Get Binance secret key."""
        return os.getenv("BINANCE_SECRET_KEY")
    
    @property
    def app_env(self) -> str:
        """Get application environment."""
        return os.getenv("APP_ENV", "development")
    
    @property
    def log_level(self) -> str:
        """Get logging level."""
        return os.getenv("LOG_LEVEL", "INFO")
    
    @property
    def cache_ttl(self) -> int:
        """Get cache TTL in seconds."""
        return int(os.getenv("CACHE_TTL", "3600"))
    
    @property
    def streamlit_port(self) -> int:
        """Get Streamlit server port."""
        return int(os.getenv("STREAMLIT_SERVER_PORT", "8501"))
    
    @property
    def streamlit_address(self) -> str:
        """Get Streamlit server address."""
        return os.getenv("STREAMLIT_SERVER_ADDRESS", "localhost")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        return os.getenv(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary.
        
        Returns:
            Dictionary of configuration values
        """
        return {
            "binance_api_key": self.binance_api_key,
            "binance_secret_key": "***" if self.binance_secret_key else None,
            "app_env": self.app_env,
            "log_level": self.log_level,
            "cache_ttl": self.cache_ttl,
            "streamlit_port": self.streamlit_port,
            "streamlit_address": self.streamlit_address,
        }


# Global configuration instance
config = Config()
