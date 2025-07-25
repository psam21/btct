"""
UI Components for Bitcoin Futures Trading Signal App

This module contains all Streamlit UI components and layout management
as per FR004 and FR011/FR012 requirements.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from apis.models import MarketData, Candlestick, Signal, SignalType, PatternType, create_sample_candlestick
from logic.signal_engine import SignalEngine
from apis.binance import fetch_market_data, fetch_historical_data
from utils.cache import get_cached_data, cache_data


def render_app():
    """Main application renderer - orchestrates all UI components."""
    # Initialize session state
    initialize_session_state()
    
    # Render app components
    render_header()
    render_sidebar()
    render_main_content()


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.data_cache = {}
        st.session_state.last_refresh = None
        st.session_state.market_data = None
        st.session_state.signals = []
        st.session_state.signal_engine = SignalEngine(min_confidence=0.5)
        st.session_state.settings = {
            'auto_refresh': False,
            'cache_enabled': True,
            'show_debug': False,
            'min_confidence': 0.5,
            'symbol': 'BTCUSDT',
            'timeframe': '1w'
        }


def render_header():
    """Render application header."""
    st.title("₿ Bitcoin Futures Trading Signals")
    st.markdown("**Real-time BTC/USDT perpetual futures trading signals based on candlestick patterns**")
    st.markdown("---")


def render_sidebar():
    """Render sidebar controls."""
    st.sidebar.title("⚙️ Controls")
    
    # Signal Engine Settings
    st.sidebar.subheader("🧠 Signal Engine")
    st.session_state.settings['min_confidence'] = st.sidebar.slider(
        "Minimum Confidence",
        min_value=0.1,
        max_value=1.0,
        value=st.session_state.settings['min_confidence'],
        step=0.05,
        help="Minimum confidence level for signal generation"
    )
    
    # Update signal engine if confidence changed
    if st.session_state.signal_engine.min_confidence != st.session_state.settings['min_confidence']:
        st.session_state.signal_engine = SignalEngine(
            min_confidence=st.session_state.settings['min_confidence']
        )
    
    # Market Settings
    st.sidebar.subheader("📈 Market Settings")
    st.session_state.settings['symbol'] = st.sidebar.selectbox(
        "Trading Pair",
        options=['BTCUSDT'],
        index=0,
        help="Currently only BTC/USDT is supported"
    )
    
    st.session_state.settings['timeframe'] = st.sidebar.selectbox(
        "Timeframe",
        options=['1w'],
        index=0,
        help="Currently only weekly timeframe is supported"
    )
    
    # Data Controls
    st.sidebar.subheader("📊 Data Controls")
    
    # Fetch Live Data button (using proper API)
    if st.sidebar.button("🔄 Fetch Live Data", type="primary"):
        fetch_live_data()
        st.rerun()
    
    # Load Demo Data button
    if st.sidebar.button("📁 Load Demo Pattern"):
        load_demo_pattern()
        st.rerun()
    
    # Clear Data button
    if st.sidebar.button("🗑️ Clear Data"):
        st.session_state.market_data = None
        st.session_state.signals = []
        st.rerun()
    
    # App Settings
    st.sidebar.subheader("⚙️ App Settings")
    st.session_state.settings['show_debug'] = st.sidebar.checkbox(
        "Show Debug Info", 
        value=st.session_state.settings['show_debug']
    )
    
    # Status
    st.sidebar.subheader("📊 Status")
    st.sidebar.success("✅ Signal Engine Ready")
    if st.session_state.market_data:
        candle_count = len(st.session_state.market_data.candles)
        signal_count = len(st.session_state.signals)
        st.sidebar.info(f"📊 {candle_count} candles loaded")
        st.sidebar.info(f"🎯 {signal_count} signals generated")
    else:
        st.sidebar.warning("⚠️ No data loaded")
    
    if st.session_state.last_refresh:
        st.sidebar.info(f"🔄 Last refresh: {st.session_state.last_refresh}")


def render_main_content():
    """Render main application content."""
    # Main content area
    if st.session_state.market_data is None:
        render_welcome_screen()
    else:
        render_trading_dashboard()
    
    # Debug information
    if st.session_state.settings['show_debug']:
        render_debug_info()


def render_welcome_screen():
    """Render welcome screen when no data is loaded."""
    st.subheader("🚀 Welcome to Bitcoin Futures Signal Engine")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        ### 🎯 Get Started
        
        This application detects **bullish and bearish engulfing patterns** in Bitcoin futures data 
        and generates trading signals with confidence scoring.
        
        **To begin:**
        1. Click "🔄 Fetch Live Data" to get real market data from Binance
        2. Click "📁 Load Demo Pattern" to see a bullish engulfing pattern example
        3. Adjust the minimum confidence threshold to filter signals
        
        ### ✨ Features Implemented
        - ✅ **Pattern Detection**: Bullish/Bearish engulfing patterns
        - ✅ **Signal Generation**: GO_LONG/GO_SHORT with confidence scoring  
        - ✅ **Commentary Generation**: Detailed analysis of each signal
        - ✅ **Live Data**: Real market data from Binance API
        """)
        
        # Quick action buttons
        st.markdown("### 🚀 Quick Actions")
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("🔄 Fetch Live Data", key="main_live"):
                fetch_live_data()
                st.rerun()
        
        with col_b:
            if st.button("📁 Load Demo Pattern", key="main_demo"):
                load_demo_pattern()
                st.rerun()


def render_trading_dashboard():
    """Render main trading dashboard with data and signals."""
    # Dashboard header
    col1, col2, col3, col4 = st.columns(4)
    
    market_data = st.session_state.market_data
    signals = st.session_state.signals
    
    with col1:
        st.metric("📊 Total Candles", len(market_data.candles))
    
    with col2:
        st.metric("🎯 Total Signals", len(signals))
    
    with col3:
        long_signals = len([s for s in signals if s.signal_type == SignalType.GO_LONG])
        st.metric("📈 Long Signals", long_signals)
    
    with col4:
        short_signals = len([s for s in signals if s.signal_type == SignalType.GO_SHORT])
        st.metric("📉 Short Signals", short_signals)
    
    # Main data table (FR011)
    st.subheader("📊 OHLC Data & Trading Signals")
    
    if len(market_data.candles) > 0:
        render_ohlc_table(market_data.candles, signals)
    else:
        st.warning("No candlestick data available")
    
    # Signal details
    if signals:
        st.subheader("🎯 Signal Analysis")
        render_signal_details(signals)
    else:
        st.info("No trading signals generated. Try lowering the minimum confidence threshold.")


def render_ohlc_table(candles: List[Candlestick], signals: List[Signal]):
    """
    Render OHLC data table with signal information.
    
    Implements FR011: OHLC Data Table
    Implements FR012: Trade Commentary
    """
    # Create signal lookup for faster access
    signal_lookup = {signal.candle.timestamp if signal.candle else None: signal for signal in signals}
    
    # Prepare table data
    table_data = []
    for candle in candles:
        signal = signal_lookup.get(candle.timestamp)
        
        # FR012: Commentary for each candlestick entry
        if signal:
            if signal.signal_type == SignalType.GO_LONG:
                commentary = f"Bullish Engulfing Pattern detected – Go Long (Confidence: {signal.confidence:.1%})"
            elif signal.signal_type == SignalType.GO_SHORT:
                commentary = f"Bearish Engulfing Pattern detected – Go Short (Confidence: {signal.confidence:.1%})"
            else:
                commentary = "No pattern detected"
        else:
            commentary = "No pattern detected"
        
        row = {
            "Timestamp": candle.timestamp.strftime("%Y-%m-%d %H:%M"),
            "Open": f"${float(candle.open_price):,.2f}",
            "High": f"${float(candle.high_price):,.2f}",
            "Low": f"${float(candle.low_price):,.2f}",
            "Close": f"${float(candle.close_price):,.2f}",
            "Volume": f"{float(candle.volume):,.0f}",
            "Pattern": signal.pattern_type.value if signal else "NO_PATTERN",
            "Signal": signal.signal_type.value if signal else "HOLD",
            "Confidence": f"{signal.confidence:.1%}" if signal else "-",
            "Commentary": commentary  # FR012: Trade Commentary
        }
        table_data.append(row)
    
    # Convert to DataFrame and display
    df = pd.DataFrame(table_data)
    
    # Display table with container width
    st.dataframe(df, use_container_width=True, height=400)


def render_signal_details(signals: List[Signal]):
    """Render detailed signal analysis."""
    for i, signal in enumerate(signals, 1):
        with st.expander(f"🎯 Signal #{i}: {signal.signal_type.value} - {signal.confidence:.1%} Confidence"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Pattern:** {signal.pattern_type.value}")
                st.markdown(f"**Entry Price:** ${float(signal.entry_price):,.2f}")
                st.markdown(f"**Confidence:** {signal.confidence:.1%} ({signal.confidence_level.value})")
                st.markdown(f"**Timestamp:** {signal.timestamp}")
                st.markdown(f"**Commentary:** {signal.commentary}")
            
            with col2:
                # Signal strength indicator
                confidence_color = "#28a745" if signal.confidence >= 0.8 else "#ffc107" if signal.confidence >= 0.5 else "#dc3545"
                st.markdown(f"""
                <div style="text-align: center; padding: 10px; border-radius: 5px; background-color: {confidence_color}20; border: 1px solid {confidence_color};">
                    <h3 style="color: {confidence_color}; margin: 0;">{signal.confidence:.1%}</h3>
                    <p style="margin: 5px 0 0 0;">{signal.confidence_level.value}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Pattern details
                if signal.pattern and len(signal.pattern.candles) >= 2:
                    prev_candle = signal.pattern.candles[0]
                    curr_candle = signal.pattern.candles[1]
                    
                    st.markdown("**Pattern Details:**")
                    st.markdown(f"- Previous: {float(prev_candle.body_size):,.0f} body")
                    st.markdown(f"- Current: {float(curr_candle.body_size):,.0f} body") 
                    st.markdown(f"- Ratio: {float(curr_candle.body_size / prev_candle.body_size):.1f}x")


def fetch_live_data():
    """Fetch live market data using proper API separation."""
    try:
        # Use the proper API module (FR015) with batch processing for complete historical data
        market_data = fetch_historical_data(
            symbol=st.session_state.settings['symbol']
        )
        
        if market_data:
            st.session_state.market_data = market_data
            
            # Generate signals
            st.session_state.signals = st.session_state.signal_engine.generate_signals(market_data)
            st.session_state.last_refresh = f"Fetched live data: {len(market_data.candles)} candles"
            
            # Cache the data (FR016)
            cache_data(f"market_data_{st.session_state.settings['symbol']}", market_data)
        else:
            st.error("Failed to fetch live market data")
            
    except Exception as e:
        st.error(f"Error fetching live data: {e}")


def load_demo_pattern():
    """Load demo data with a clear bullish engulfing pattern."""
    candles = []
    
    # Create bearish candle
    bearish_candle = create_sample_candlestick(
        timestamp=datetime(2024, 1, 1, 0, 0, 0),
        open_price=45000.0,
        high_price=45200.0,
        low_price=44500.0,
        close_price=44600.0,  # Bearish
        volume=1000.0
    )
    candles.append(bearish_candle)
    
    # Create bullish engulfing candle
    engulfing_candle = create_sample_candlestick(
        timestamp=datetime(2024, 1, 8, 0, 0, 0),
        open_price=44400.0,  # Below previous close
        high_price=46000.0,
        low_price=44300.0,
        close_price=45800.0,  # Above previous open - engulfing!
        volume=1500.0  # Higher volume
    )
    candles.append(engulfing_candle)
    
    # Add follow-up candle
    followup_candle = create_sample_candlestick(
        timestamp=datetime(2024, 1, 15, 0, 0, 0),
        open_price=45800.0,
        high_price=46200.0,
        low_price=45600.0,
        close_price=46100.0,
        volume=1200.0
    )
    candles.append(followup_candle)
    
    # Create market data
    st.session_state.market_data = MarketData(
        symbol="BTCUSDT",
        timeframe="1w",
        candles=candles,
        patterns=[],
        signals=[],
        last_updated=datetime.now()
    )
    
    # Generate signals
    st.session_state.signals = st.session_state.signal_engine.generate_signals(st.session_state.market_data)
    st.session_state.last_refresh = f"Loaded demo pattern with {len(st.session_state.signals)} signals"


def render_debug_info():
    """Render debug information."""
    st.subheader("🔧 Debug Information")
    
    debug_data = {
        "app_version": "0.4.0-phase4",
        "streamlit_version": st.__version__,
        "signal_engine_config": {
            "min_confidence": st.session_state.signal_engine.min_confidence,
            "timeout_hours": st.session_state.signal_engine.signal_timeout_hours
        },
        "session_state_keys": list(st.session_state.keys()),
        "settings": st.session_state.settings
    }
    
    if st.session_state.market_data:
        debug_data["market_data"] = {
            "symbol": st.session_state.market_data.symbol,
            "timeframe": st.session_state.market_data.timeframe,
            "candle_count": len(st.session_state.market_data.candles),
            "signal_count": len(st.session_state.signals)
        }
    
    st.json(debug_data)
