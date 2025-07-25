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
        print(f"Error fetching data from Binance API: {e}")
        return None
    except Exception as e:
        print(f"Error processing Binance data: {e}")
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


def fetch_historical_data(symbol: str = "BTCUSDT", start_date: datetime = None, end_date: datetime = None) -> Optional[MarketData]:
    """
    Fetch complete historical data from 2019 to current date using batch processing.
    
    Implements FR015: Fetch all historical data from Binance (from 2019 to now)
    
    Args:
        symbol: Trading pair symbol
        start_date: Start date for historical data (default: 2019-01-01)
        end_date: End date for historical data (default: current date)
    
    Returns:
        MarketData object with complete historical data
    """
    if start_date is None:
        start_date = datetime(2019, 1, 1)
    if end_date is None:
        end_date = datetime.now()
    
    # Convert dates to milliseconds
    start_time = int(start_date.timestamp() * 1000)
    end_time = int(end_date.timestamp() * 1000)
    
    # Calculate interval in milliseconds (weekly = 7 * 24 * 60 * 60 * 1000)
    interval_ms = 7 * 24 * 60 * 60 * 1000
    batch_size = 1000  # Binance limit per request
    
    all_candlesticks = []
    current_time = start_time
    
    try:
        while current_time < end_time:
            # Calculate batch end time
            batch_end = min(current_time + (batch_size * interval_ms), end_time)
            
            # Fetch batch
            batch_candlesticks = _fetch_batch(symbol, "1w", current_time, batch_end)
            
            if batch_candlesticks:
                all_candlesticks.extend(batch_candlesticks)
                print(f"Fetched batch: {len(batch_candlesticks)} candles from {datetime.fromtimestamp(current_time/1000)} to {datetime.fromtimestamp(batch_end/1000)}")
            else:
                print(f"Failed to fetch batch from {datetime.fromtimestamp(current_time/1000)}")
                break
            
            # Move to next batch
            current_time = batch_end
            
            # Rate limiting - wait 100ms between requests
            time.sleep(0.1)
            
            # Stop if we got less than expected (reached current time)
            if len(batch_candlesticks) < batch_size:
                break
        
        if not all_candlesticks:
            print("No historical data fetched")
            return None
        
        # Remove duplicates and sort by timestamp
        unique_candlesticks = []
        seen_timestamps = set()
        
        for candle in sorted(all_candlesticks, key=lambda x: x.timestamp):
            if candle.timestamp not in seen_timestamps:
                unique_candlesticks.append(candle)
                seen_timestamps.add(candle.timestamp)
        
        # Create MarketData object
        market_data = MarketData(
            symbol=symbol,
            timeframe="1w",
            candles=unique_candlesticks,
            last_updated=datetime.now()
        )
        
        print(f"Successfully fetched {len(unique_candlesticks)} historical candles from {start_date} to {end_date}")
        return market_data
        
    except Exception as e:
        print(f"Error fetching historical data: {e}")
        return None


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
        server_time = get_server_time()
        return server_time is not None
    except Exception:
        return False
