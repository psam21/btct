#!/usr/bin/env python3
"""
Demo script showing Phase 3 Signal Engine functionality.

This script demonstrates:
- Pattern detection (bullish/bearish engulfing)
- Signal generation with confidence scoring
- Commentary generation
- Signal analytics

Run with: python demo_signal_engine.py
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from datetime import datetime
from apis.models import (
    MarketData, SignalType, PatternType,
    create_sample_candlestick
)
from logic.signal_engine import SignalEngine


def create_demo_data():
    """Create sample market data with various patterns."""
    candles = []
    
    print("🔄 Creating demo candlestick data...")
    
    # Sample 1: Bullish Engulfing Pattern
    print("   📊 Adding bearish candle...")
    bearish_candle = create_sample_candlestick(
        timestamp=datetime(2024, 1, 1, 0, 0, 0),
        open_price=45000.0,
        high_price=45200.0,
        low_price=44500.0,
        close_price=44600.0,  # Red/bearish candle
        volume=1000.0
    )
    candles.append(bearish_candle)
    
    print("   📊 Adding bullish engulfing candle...")
    engulfing_candle = create_sample_candlestick(
        timestamp=datetime(2024, 1, 8, 0, 0, 0),
        open_price=44400.0,  # Below previous close
        high_price=46000.0,
        low_price=44300.0,
        close_price=45800.0,  # Above previous open - creates engulfing pattern
        volume=1500.0  # Higher volume
    )
    candles.append(engulfing_candle)
    
    # Sample 2: Another candle for more data
    print("   📊 Adding follow-up candle...")
    followup_candle = create_sample_candlestick(
        timestamp=datetime(2024, 1, 15, 0, 0, 0),
        open_price=45800.0,
        high_price=46200.0,
        low_price=45600.0,
        close_price=46100.0,
        volume=1200.0
    )
    candles.append(followup_candle)
    
    return MarketData(
        symbol="BTCUSDT",
        timeframe="1w",
        candles=candles,
        patterns=[],
        signals=[],
        last_updated=datetime.now()
    )


def demo_signal_engine():
    """Demonstrate the signal engine functionality."""
    print("🚀 Bitcoin Futures Signal Engine Demo")
    print("=" * 50)
    
    # Create demo data
    market_data = create_demo_data()
    
    print(f"\n📈 Market Data Summary:")
    print(f"   Symbol: {market_data.symbol}")
    print(f"   Timeframe: {market_data.timeframe}")
    print(f"   Total Candles: {len(market_data.candles)}")
    print(f"   Date Range: {market_data.candles[0].timestamp} to {market_data.candles[-1].timestamp}")
    
    # Initialize signal engine
    print(f"\n🧠 Initializing Signal Engine...")
    engine = SignalEngine(min_confidence=0.3)  # Lower threshold for demo
    print(f"   Minimum Confidence: {engine.min_confidence}")
    print(f"   Signal Timeout: {engine.signal_timeout_hours} hours")
    
    # Generate signals
    print(f"\n🔍 Analyzing Market Data for Patterns...")
    signals = engine.generate_signals(market_data)
    
    print(f"\n📊 Analysis Results:")
    print(f"   Signals Generated: {len(signals)}")
    
    # Display signals
    if signals:
        print(f"\n🎯 Signal Details:")
        for i, signal in enumerate(signals, 1):
            print(f"\n   Signal #{i}:")
            print(f"   ├─ ID: {signal.id}")
            print(f"   ├─ Type: {signal.signal_type.value}")
            print(f"   ├─ Pattern: {signal.pattern_type.value}")
            print(f"   ├─ Entry Price: ${signal.entry_price:,.2f}")
            print(f"   ├─ Confidence: {signal.confidence:.1%} ({signal.confidence_level.value})")
            print(f"   ├─ Timestamp: {signal.timestamp}")
            print(f"   └─ Commentary: {signal.commentary}")
        
        # Generate summary
        print(f"\n📈 Signal Summary:")
        summary = engine.get_signal_summary(signals)
        print(f"   ├─ Total Signals: {summary['total_signals']}")
        print(f"   ├─ Long Signals: {summary['buy_signals']}")
        print(f"   ├─ Short Signals: {summary['sell_signals']}")
        print(f"   ├─ Average Confidence: {summary['avg_confidence']:.1%}")
        print(f"   └─ Confidence Distribution: {summary['confidence_distribution']}")
        
    else:
        print(f"   ⚠️ No signals generated (patterns may not meet confidence threshold)")
    
    print(f"\n✅ Demo completed successfully!")
    print(f"\nThis demonstrates Phase 3 completion:")
    print(f"   ✅ Pattern detection algorithms")
    print(f"   ✅ Signal generation logic")
    print(f"   ✅ Commentary generation")
    print(f"   ✅ Confidence scoring")
    print(f"   ✅ Signal analytics")
    

if __name__ == "__main__":
    try:
        demo_signal_engine()
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
