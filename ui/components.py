"""
UI Components for Bitcoin Futures Trading Signal App

This module contains all Streamlit UI components and layout manage    
    def render_welcome_screen():
    """Render welcome screen when no data is loaded."""
    st.markdown("### 📊 Bitcoin Historical Data")
    
    # Quick action buttons
    col_a, col_b = st.columns(2)
    
    with col_a:
        if st.button("🔄 Fetch Historical Data", key="main_live"):
            fetch_live_data()
            st.rerun()
    
    with col_b:
        if st.button("🗑️ Clear All Data", key="main_clear"):
            st.session_state.market_data = None
            st.session_state.signals = []
            st.rerun()ttons
    col_a, col_b = st.columns(2)
    
    with col_a:
        if st.button("🔄 Fetch Historical Data", key="main_live"):
            fetch_live_data()
            st.rerun()
    
    with col_b:
        if st.button("🗑️ Clear All Data", key="main_clear"):
            st.session_state.market_data = None
            st.session_state.signals = []
            st.rerun()004 and FR011/FR012 requirements.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from apis.models import MarketData, Candlestick, Signal, SignalType, PatternType
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
        st.session_state.settings = {
            'auto_refresh': False,
            'cache_enabled': True,
            'show_debug': False,
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
    
    # Market Settings
    st.sidebar.subheader("📈 Market Settings")
    st.session_state.settings['symbol'] = st.sidebar.selectbox(
        "Trading Pair",
        options=["BTCUSDT"],
        index=0,
        help="Bitcoin USDT perpetual futures"
    )
    
    st.session_state.settings['timeframe'] = st.sidebar.selectbox(
        "Timeframe",
        options=["1w"],
        index=0,
        help="Currently only weekly timeframe is supported"
    )
    
    # Data Controls
    st.sidebar.subheader("📊 Data Controls")
    
    # Fetch Live Data button (using proper API)
    if st.sidebar.button("🔄 Fetch Historical Data", type="primary"):
        fetch_live_data()
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
    st.markdown("### 📊 Bitcoin Historical Data")
    
    # Quick action buttons
    col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("🔄 Fetch Historical Data", key="main_live"):
                fetch_live_data()
                st.rerun()
        
        with col_b:
            if st.button("�️ Clear All Data", key="main_clear"):
                st.session_state.market_data = None
                st.session_state.signals = []
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
    """Fetch historical market data with user feedback."""
    # Show progress
    progress_placeholder = st.empty()
    status_placeholder = st.empty()
    
    try:
        with progress_placeholder.container():
            st.info("🔄 Fetching historical data from Binance...")
        
        with status_placeholder.container():
            st.write("📅 Fetching weekly candles from 2019 to present...")
        
        # Use the proper API module (FR015) with batch processing for complete historical data
        market_data = fetch_historical_data(
            symbol=st.session_state.settings['symbol']
        )
        
        if market_data and market_data.candles:
            st.session_state.market_data = market_data
            st.session_state.signals = []  # Clear old signals
            
            # Update status with success info
            candle_count = len(market_data.candles)
            start_date = market_data.candles[0].timestamp.strftime("%Y-%m-%d") if market_data.candles else "N/A"
            end_date = market_data.candles[-1].timestamp.strftime("%Y-%m-%d") if market_data.candles else "N/A"
            
            st.session_state.last_refresh = f"✅ Successfully fetched {candle_count} weekly candles from {start_date} to {end_date}"
            
            # Clear progress indicators
            progress_placeholder.empty()
            status_placeholder.empty()
            
            # Show success message
            st.success(f"✅ Fetched {candle_count} weekly candles ({start_date} to {end_date})")
            
            # Cache the data (FR016)
            cache_data(f"market_data_{st.session_state.settings['symbol']}", market_data)
            
        else:
            progress_placeholder.empty()
            status_placeholder.empty()
            st.error("❌ Failed to fetch market data from Binance API")
            st.session_state.last_refresh = "❌ Failed to fetch data"
            
    except Exception as e:
        progress_placeholder.empty()
        status_placeholder.empty()
        error_msg = f"❌ Error fetching data: {str(e)}"
        st.error(error_msg)
        st.session_state.last_refresh = error_msg
        st.write("**Debug Info:**")
        st.code(str(e))


def render_debug_info():
    """Render debug information for troubleshooting."""
    if st.checkbox("🔧 Show Debug Info"):
        st.subheader("🔧 Debug Information")
        
        # Session state info
        debug_data = {
            "market_data": "Loaded" if st.session_state.get('market_data') else "None",
            "signals_count": len(st.session_state.get('signals', [])),
            "last_refresh": st.session_state.get('last_refresh', 'Never'),
            "symbol": st.session_state.get('settings', {}).get('symbol', 'Unknown'),
            "timeframe": st.session_state.get('settings', {}).get('timeframe', 'Unknown'),
            "session_state_keys": list(st.session_state.keys()),
        }
        
        if st.session_state.get('market_data'):
            debug_data["candles_count"] = len(st.session_state.market_data.candles)
            if st.session_state.market_data.candles:
                debug_data["date_range"] = f"{st.session_state.market_data.candles[0].timestamp} to {st.session_state.market_data.candles[-1].timestamp}"
        
        st.json(debug_data)


def render_debug_info():
    """Render debug information."""
    st.subheader("🔧 Debug Information")
    
    debug_data = {
        "app_version": "1.0.0-historical-data",
        "streamlit_version": st.__version__,
        "session_state_keys": list(st.session_state.keys()),
        "settings": st.session_state.settings
    }
    
    if st.session_state.market_data:
        debug_data["market_data"] = {
            "symbol": st.session_state.market_data.symbol,
            "timeframe": st.session_state.market_data.timeframe,
            "candle_count": len(st.session_state.market_data.candles),
            "first_candle": str(st.session_state.market_data.candles[0].timestamp) if st.session_state.market_data.candles else "None",
            "last_candle": str(st.session_state.market_data.candles[-1].timestamp) if st.session_state.market_data.candles else "None"
        }
    
    st.json(debug_data)
