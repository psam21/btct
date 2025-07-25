"""
Bitfinex API integration for Bitcoin historical data fetching.

This module implements historical data fetching from Bitfinex with data going back to 2013.
Uses spot BTC/USD data with 1-year batch processing to avoid API limits.
"""

import requests
from datetime import datetime, timedelta
from typing import List, Optional
from decimal import Decimal
import time

from apis.models import MarketData, Candlestick


def fetch_historical_data(
    symbol: str = "tBTCUSD", 
    timeframe: str = "1W", 
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Optional[MarketData]:
    """
    Fetch historical market data from Bitfinex API with batch processing.
    
    Bitfinex provides data from 2013 onwards for spot trading pairs.
    Uses 1-year batches to avoid API rate limits (30 req/min).
    
    Args:
        symbol: Trading pair symbol (default: tBTCUSD for spot BTC/USD)
        timeframe: Timeframe for candlestick data (default: 1W for weekly)
        start_date: Start date for historical data (default: 2013-01-01)
        end_date: End date for historical data (default: now)
    
    Returns:
        MarketData object with complete historical candlesticks or None if failed
    """
    if start_date is None:
        start_date = datetime(2013, 1, 1)  # Bitfinex has data from 2013
    if end_date is None:
        end_date = datetime.now()
    
    print(f"Fetching historical data from Bitfinex: {start_date.date()} to {end_date.date()}...")
    print(f"Symbol: {symbol} (spot trading), Timeframe: {timeframe}")
    
    all_candlesticks = []
    current_start = start_date
    
    # Process in 1-year batches as requested
    while current_start < end_date:
        try:
            # Calculate 1-year batch end
            batch_end = min(
                current_start + timedelta(days=365),
                end_date
            )
            
            print(f"  Fetching batch: {current_start.date()} to {batch_end.date()}")
            
            # Fetch 1-year batch
            batch_data = _fetch_batch(symbol, timeframe, current_start, batch_end)
            
            if batch_data:
                all_candlesticks.extend(batch_data)
                print(f"    Got {len(batch_data)} candles")
            else:
                print(f"    No data for this batch")
            
            # Move to next year
            current_start = batch_end + timedelta(days=1)
            
            # Rate limiting - Bitfinex allows 30 req/min, so wait 2 seconds between requests
            time.sleep(2.0)
            
        except Exception as e:
            print(f"Error fetching batch starting {current_start}: {e}")
            # Don't break on single batch failure, try next batch
            current_start = current_start + timedelta(days=365)
            continue
    
    if not all_candlesticks:
        print("No historical data fetched from Bitfinex")
        return None
    
    # Remove duplicates and sort by timestamp
    unique_candles = {}
    for candle in all_candlesticks:
        unique_candles[candle.timestamp] = candle
    
    sorted_candles = sorted(unique_candles.values(), key=lambda x: x.timestamp)
    
    print(f"Total historical data from Bitfinex: {len(sorted_candles)} candles")
    
    return MarketData(
        symbol=symbol,
        timeframe=timeframe,
        candles=sorted_candles,
        last_updated=datetime.now()
    )


def _fetch_batch(symbol: str, timeframe: str, start_date: datetime, end_date: datetime) -> List[Candlestick]:
    """
    Fetch a single batch of data from Bitfinex API.
    
    Args:
        symbol: Trading pair symbol (e.g., tBTCUSD)
        timeframe: Timeframe for candlestick data (e.g., 1W)
        start_date: Start date for this batch
        end_date: End date for this batch
    
    Returns:
        List of Candlestick objects for this batch
    """
    try:
        # Bitfinex API endpoint format: /v2/candles/trade:TIMEFRAME:SYMBOL/hist
        url = f"https://api-pub.bitfinex.com/v2/candles/trade:{timeframe}:{symbol}/hist"
        
        # Convert dates to milliseconds (Bitfinex uses millisecond timestamps)
        start_ms = int(start_date.timestamp() * 1000)
        end_ms = int(end_date.timestamp() * 1000)
        
        params = {
            "start": start_ms,
            "end": end_ms,
            "limit": 10000,  # Bitfinex allows up to 10,000 candles per request
            "sort": 1  # Sort in ascending order by timestamp
        }
        
        print(f"    Bitfinex API call: {url}")
        print(f"    Parameters: start={start_date.date()}, end={end_date.date()}, limit=10000")
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        
        candles_data = response.json()
        
        if not candles_data:
            print(f"    No data returned from Bitfinex")
            return []
        
        print(f"    Bitfinex returned {len(candles_data)} raw candles")
        return convert_bitfinex_to_candlesticks(candles_data, symbol)
        
    except requests.RequestException as e:
        print(f"❌ Network error fetching from Bitfinex API: {e}")
        return []
    except Exception as e:
        print(f"❌ Error processing Bitfinex data: {e}")
        return []


def convert_bitfinex_to_candlesticks(candles_data: List[List], symbol: str) -> List[Candlestick]:
    """
    Convert Bitfinex candles data to Candlestick objects.
    
    Bitfinex format: [MTS, OPEN, CLOSE, HIGH, LOW, VOLUME]
    - MTS: Millisecond epoch timestamp
    - OPEN: First execution during timeframe
    - CLOSE: Last execution during timeframe  
    - HIGH: Highest execution during timeframe
    - LOW: Lowest execution during timeframe
    - VOLUME: Quantity traded within timeframe
    
    Args:
        candles_data: Raw candles data from Bitfinex API
        symbol: Trading pair symbol
    
    Returns:
        List of Candlestick objects
    """
    candlesticks = []
    
    for candle_data in candles_data:
        try:
            if len(candle_data) < 6:
                print(f"Invalid candle data format: {candle_data}")
                continue
                
            # Bitfinex format: [MTS, OPEN, CLOSE, HIGH, LOW, VOLUME]
            timestamp_ms = candle_data[0]
            open_price = candle_data[1]
            close_price = candle_data[2]
            high_price = candle_data[3]
            low_price = candle_data[4]
            volume = candle_data[5]
            
            candlestick = Candlestick(
                timestamp=datetime.fromtimestamp(timestamp_ms / 1000),
                open_price=Decimal(str(open_price)),
                high_price=Decimal(str(high_price)),
                low_price=Decimal(str(low_price)),
                close_price=Decimal(str(close_price)),
                volume=Decimal(str(volume)),
                symbol=symbol
            )
            candlesticks.append(candlestick)
            
        except (ValueError, IndexError, TypeError) as e:
            print(f"Error converting Bitfinex candle data: {e}, data: {candle_data}")
            continue
    
    print(f"    Converted {len(candlesticks)} Bitfinex candles to Candlestick objects")
    return candlesticks


def check_api_connection() -> bool:
    """
    Check if Bitfinex API is accessible.
    
    Returns:
        True if API is accessible, False otherwise
    """
    try:
        print("Testing Bitfinex API connection...")
        
        # Test with a simple platform status call
        url = "https://api-pub.bitfinex.com/v2/platform/status"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        status_data = response.json()
        if status_data and len(status_data) > 0 and status_data[0] == 1:
            print("✅ Bitfinex API connected and platform is operational")
            return True
        else:
            print(f"❌ Bitfinex platform status: {status_data}")
            return False
            
    except requests.RequestException as e:
        print(f"❌ Network error connecting to Bitfinex API: {e}")
        return False
    except Exception as e:
        print(f"❌ Bitfinex API connection test failed: {e}")
        return False


def get_available_symbols() -> List[str]:
    """
    Get list of available trading symbols from Bitfinex.
    
    Returns:
        List of available symbol strings
    """
    try:
        url = "https://api-pub.bitfinex.com/v2/conf/pub:list:pair:exchange"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        symbols_data = response.json()
        if symbols_data and len(symbols_data) > 0:
            symbols = symbols_data[0]  # Symbols are in the first array element
            btc_symbols = [s for s in symbols if 'BTC' in s and 'USD' in s]
            print(f"Found {len(btc_symbols)} BTC/USD trading pairs on Bitfinex")
            return btc_symbols
        
        return []
        
    except Exception as e:
        print(f"Error fetching Bitfinex symbols: {e}")
        return ["tBTCUSD"]  # Default fallback
