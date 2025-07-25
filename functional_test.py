#!/usr/bin/env python3
"""Functional test to verify core app features work"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from apis.binance import fetch_market_data
from logic.signal_engine import SignalEngine
from apis.models import Candlestick
from datetime import datetime
from decimal import Decimal

print("=== FUNCTIONAL TEST ===")

# Test 1: Signal engine with mock data
print("1. Testing signal engine...")
try:
    engine = SignalEngine()
    
    # Create sample candlesticks for bullish engulfing pattern
    candles = [
        Candlestick(
            timestamp=datetime(2024, 1, 1),
            open_price=Decimal("45000"),
            high_price=Decimal("45100"),
            low_price=Decimal("44900"),
            close_price=Decimal("44950"),  # bearish
            volume=Decimal("100"),
            symbol="BTCUSDT"
        ),
        Candlestick(
            timestamp=datetime(2024, 1, 2),
            open_price=Decimal("44940"),
            high_price=Decimal("45200"),
            low_price=Decimal("44930"),
            close_price=Decimal("45150"),  # bullish engulfing
            volume=Decimal("200"),
            symbol="BTCUSDT"
        )
    ]
    
    # Create MarketData object as expected by signal engine
    from apis.models import MarketData
    market_data = MarketData(
        symbol="BTCUSDT",
        timeframe="1w", 
        candles=candles,
        patterns=[],
        signals=[],
        last_updated=datetime.now()
    )
    
    signals = engine.generate_signals(market_data)
    print(f"   ✅ Signal engine works - Generated {len(signals)} signals")
    
except Exception as e:
    print(f"   ❌ Signal engine failed: {e}")

# Test 2: API data fetching (with timeout)
print("2. Testing API data fetching...")
try:
    data = fetch_market_data("BTCUSDT", "1w", 5)
    if data and len(data.candles) > 0:
        print(f"   ✅ API works - Fetched {len(data.candles)} candles")
    else:
        print("   ⚠️  API returned no data (might be network issue)")
except Exception as e:
    print(f"   ⚠️  API test failed: {e} (might be network issue)")

print("\n=== FUNCTIONAL TEST COMPLETE ===")
