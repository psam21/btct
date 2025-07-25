#!/usr/bin/env python3
"""Test the new batch fetching functionality"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from apis.binance import fetch_historical_data, fetch_market_data
from datetime import datetime

print("=== BATCH FETCHING TEST ===")

# Test 1: Small historical range to verify batching works
print("1. Testing batch fetching for small range...")
try:
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 6, 30)
    
    data = fetch_historical_data("BTCUSDT", "1w", start_date, end_date)
    
    if data and len(data.candles) > 0:
        print(f"   ✅ Batch fetching works - Got {len(data.candles)} candles")
        print(f"   📅 Date range: {data.candles[0].timestamp.date()} to {data.candles[-1].timestamp.date()}")
    else:
        print("   ❌ Batch fetching failed - No data returned")
        
except Exception as e:
    print(f"   ❌ Batch fetching failed: {e}")

# Test 2: Compare with regular fetch
print("\n2. Comparing with regular fetch...")
try:
    regular_data = fetch_market_data("BTCUSDT", "1w", 50)
    
    if regular_data and len(regular_data.candles) > 0:
        print(f"   ✅ Regular fetch works - Got {regular_data.candles} candles")
        print(f"   📅 Latest date: {regular_data.candles[-1].timestamp.date()}")
    else:
        print("   ❌ Regular fetch failed")
        
except Exception as e:
    print(f"   ❌ Regular fetch failed: {e}")

print("\n=== BATCH FETCHING TEST COMPLETE ===")
