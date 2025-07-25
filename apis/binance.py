"""
Binance API integration for Bitcoin futures trading signal application.

This module implements FR015: Historical Data Fetching from Binance
Handles all API interaction logic as per FR004 component responsibilities.
"""

import requests
from datetime import datetime
from typing import List, Optional
from decimal import Decimal

from apis.models import MarketData, Candlestick
from datetime import datetime, timedelta
import time


def fetch_historical_data(
    symbol: str = "BTCUSDT", 
    timeframe: str = "1w", 
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Optional[MarketData]:
    """
    Fetch historical market data from Binance API with batch processing.
    
    Implements FR015: Historical Data Fetching from Binance with proper batching
    to avoid API limits and get complete historical data.
    
    Args:
        symbol: Trading pair symbol (default: BTCUSDT)
        timeframe: Timeframe for candlestick data (default: 1w for weekly)
        start_date: Start date for historical data (default: 2019-01-01)
        end_date: End date for historical data (default: now)
    
    Returns:
        MarketData object with complete historical candlesticks or None if failed
    """
    if start_date is None:
        start_date = datetime(2019, 1, 1)  # Default to 2019 start
    if end_date is None:
        end_date = datetime.now()
    
    print(f"Fetching historical data from {start_date.date()} to {end_date.date()}...")
    
    all_candlesticks = []
    current_start = start_date
    batch_size = 1000  # Binance API limit
    
    while current_start < end_date:
        try:
            # Calculate batch end time
            if timeframe == "1w":
                batch_end = current_start + timedelta(weeks=batch_size)
            elif timeframe == "1d":
                batch_end = current_start + timedelta(days=batch_size)
            elif timeframe == "1h":
                batch_end = current_start + timedelta(hours=batch_size)
            else:
                # Default to treating as days
                batch_end = current_start + timedelta(days=batch_size)
            
            # Don't go beyond end_date
            if batch_end > end_date:
                batch_end = end_date
            
            # Convert to milliseconds for Binance API
            start_time = int(current_start.timestamp() * 1000)
            end_time = int(batch_end.timestamp() * 1000)
            
            print(f"  Fetching batch: {current_start.date()} to {batch_end.date()}")
            
            # Fetch batch
            batch_data = _fetch_batch(symbol, timeframe, start_time, end_time)
            
            if batch_data:
                all_candlesticks.extend(batch_data)
                print(f"    Got {len(batch_data)} candles")
            else:
                print(f"    No data for this batch")
                break
            
            # Move to next batch
            current_start = batch_end + timedelta(seconds=1)
            
            # Rate limiting - be nice to Binance API
            time.sleep(0.1)
            
        except Exception as e:
            print(f"Error fetching batch starting {current_start}: {e}")
            break
    
    if not all_candlesticks:
        print("No historical data fetched")
        return None
    
    # Remove duplicates and sort by timestamp
    unique_candles = {}
    for candle in all_candlesticks:
        unique_candles[candle.timestamp] = candle
    
    sorted_candles = sorted(unique_candles.values(), key=lambda x: x.timestamp)
    
    print(f"Total historical data: {len(sorted_candles)} candles")
    
    return MarketData(
        symbol=symbol,
        timeframe=timeframe,
        candles=sorted_candles,
        last_updated=datetime.now()
    )


def _fetch_batch(symbol: str, timeframe: str, start_time: int, end_time: int) -> List[Candlestick]:
    """
    Fetch a single batch of data from Binance API.
    
    Args:
        symbol: Trading pair symbol
        timeframe: Timeframe for candlestick data
        start_time: Start time in milliseconds
        end_time: End time in milliseconds
    
    Returns:
        List of Candlestick objects for this batch
    """
    try:
        url = "https://api.binance.com/api/v3/klines"
        params = {
            "symbol": symbol,
            "interval": timeframe,
            "startTime": start_time,
            "endTime": end_time,
            "limit": 1000
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        klines_data = response.json()
        
        if not klines_data:
            return []
        
        return convert_klines_to_candlesticks(klines_data)
        
    except Exception as e:
        print(f"Error in batch fetch: {e}")
        return []


def fetch_market_data(symbol: str = "BTCUSDT", timeframe: str = "1w", limit: int = 100) -> Optional[MarketData]:
    """
    Fetch market data from Binance API.
    
    Implements FR015: Historical Data Fetching from Binance
    
    Args:
        symbol: Trading pair symbol (default: BTCUSDT)
        timeframe: Timeframe for candlestick data (default: 1w for weekly)
        limit: Number of candles to fetch (default: 100)
    
    Returns:
        MarketData object with candlesticks or None if failed
    """
    try:
        # Binance API endpoint for klines
        url = "https://api.binance.com/api/v3/klines"
        params = {
            "symbol": symbol,
            "interval": timeframe,
            "limit": limit
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        klines_data = response.json()
        
        if not klines_data:
            return None
        
        # Convert to candlesticks
        candlesticks = convert_klines_to_candlesticks(klines_data)
        
        # Create MarketData object
        market_data = MarketData(
            symbol=symbol,
            timeframe=timeframe,
            candles=candlesticks,
            last_updated=datetime.now()
        )
        
        return market_data
        
    except requests.RequestException as e:
        print(f"❌ Network error fetching data from Binance API: {e}")
        print("🚨 This may be due to network restrictions on Streamlit Cloud")
        return None
    except Exception as e:
        print(f"❌ Error processing Binance data: {e}")
        return None


def convert_klines_to_candlesticks(klines_data: List[List]) -> List[Candlestick]:
    """
    Convert Binance klines data to Candlestick objects.
    
    Args:
        klines_data: Raw klines data from Binance API
    
    Returns:
        List of Candlestick objects
    """
    candlesticks = []
    
    for kline in klines_data:
        try:
            candlestick = Candlestick(
                timestamp=datetime.fromtimestamp(int(kline[0]) / 1000),
                open_price=Decimal(str(kline[1])),
                high_price=Decimal(str(kline[2])),
                low_price=Decimal(str(kline[3])),
                close_price=Decimal(str(kline[4])),
                volume=Decimal(str(kline[5])),
                symbol=klines_data[0][12] if len(kline) > 12 else "BTCUSDT"  # Use symbol from data or default
            )
            candlesticks.append(candlestick)
        except (ValueError, IndexError) as e:
            print(f"Error converting kline data: {e}")
            continue
    
    return candlesticks


def get_server_time() -> Optional[datetime]:
    """
    Get Binance server time for synchronization.
    
    Returns:
        Current Binance server time or None if failed
    """
    try:
        url = "https://api.binance.com/api/v3/time"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        server_time_data = response.json()
        server_time = datetime.fromtimestamp(server_time_data['serverTime'] / 1000)
        
        return server_time
        
    except requests.RequestException as e:
        print(f"Error fetching server time: {e}")
        return None


def check_api_connection() -> bool:
    """
    Check if Binance API is accessible.
    
    Returns:
        True if API is accessible, False otherwise
    """
    try:
        print("Testing Binance API connection...")
        server_time = get_server_time()
        if server_time is not None:
            print(f"✅ Binance API connected. Server time: {server_time}")
            return True
        else:
            print("❌ Failed to get server time from Binance API")
            return False
    except Exception as e:
        print(f"❌ API connection test failed: {e}")
        return False
