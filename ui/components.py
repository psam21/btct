"""
UI Components for Bitcoin Historical Data App

Simple Streamlit UI for fetching and displaying Bitcoin historical data.
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from apis.models import MarketData
from apis.binance import fetch_historical_data
from utils.cache import cache_data


def render_app():
    """Main application renderer."""
    initialize_session_state()
    render_header()
    render_sidebar()
    render_main_content()


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.market_data = None
        st.session_state.last_refresh = None
        st.session_state.settings = {
            'symbol': 'BTCUSDT',
            'timeframe': '1w',
            'show_debug': False
        }


def render_header():
    """Render application header."""
    st.title("₿ Bitcoin Historical Data")
    st.markdown("**Weekly BTC/USDT data from 2019 to present**")
    st.markdown("---")


def render_sidebar():
    """Render sidebar controls."""
    st.sidebar.title("⚙️ Controls")
    
    # Market Settings
    st.sidebar.subheader("📈 Settings")
    st.session_state.settings['symbol'] = st.sidebar.selectbox(
        "Trading Pair",
        options=["BTCUSDT"],
        index=0
    )
    
    st.session_state.settings['timeframe'] = st.sidebar.selectbox(
        "Timeframe",
        options=["1w"],
        index=0,
        help="Weekly timeframe"
    )
    
    # Data Controls
    st.sidebar.subheader("📊 Actions")
    
    if st.sidebar.button("🔄 Fetch Historical Data", type="primary"):
        fetch_live_data()
        st.rerun()
    
    if st.sidebar.button("🗑️ Clear Data"):
        st.session_state.market_data = None
        st.rerun()
    
    # Debug
    st.session_state.settings['show_debug'] = st.sidebar.checkbox(
        "Show Debug Info", 
        value=st.session_state.settings['show_debug']
    )
    
    # Status
    st.sidebar.subheader("📊 Status")
    if st.session_state.market_data:
        candle_count = len(st.session_state.market_data.candles)
        st.sidebar.success(f"✅ {candle_count} candles loaded")
    else:
        st.sidebar.warning("⚠️ No data loaded")
    
    if st.session_state.last_refresh:
        st.sidebar.info(f"🔄 {st.session_state.last_refresh}")


def render_main_content():
    """Render main application content."""
    if st.session_state.market_data is None:
        render_welcome_screen()
    else:
        render_data_dashboard()
    
    if st.session_state.settings['show_debug']:
        render_debug_info()


def render_welcome_screen():
    """Render welcome screen when no data is loaded."""
    st.markdown("### 📊 Bitcoin Historical Data")
    st.markdown("Click **'Fetch Historical Data'** in the sidebar to load weekly BTC data from 2019 to present.")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        if st.button("🔄 Fetch Historical Data", key="main_fetch"):
            fetch_live_data()
            st.rerun()
    
    with col_b:
        st.markdown("**Expected data:**")
        st.markdown("- ~342 weekly candles")
        st.markdown("- 2019-01-01 to 2025-07-25")
        st.markdown("- OHLC + Volume data")


def render_data_dashboard():
    """Render data dashboard when data is loaded."""
    market_data = st.session_state.market_data
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total Candles", len(market_data.candles))
    
    with col2:
        first_date = market_data.candles[0].timestamp.strftime("%Y-%m-%d")
        st.metric("📅 Start Date", first_date)
    
    with col3:
        last_date = market_data.candles[-1].timestamp.strftime("%Y-%m-%d")
        st.metric("📅 End Date", last_date)
    
    with col4:
        latest_price = f"${float(market_data.candles[-1].close_price):,.2f}"
        st.metric("💰 Latest Close", latest_price)
    
    # Data Table
    st.subheader("📊 OHLC Data")
    render_data_table(market_data.candles)


def render_data_table(candles):
    """Render OHLC data table."""
    table_data = []
    
    for candle in candles:
        row = {
            "Date": candle.timestamp.strftime("%Y-%m-%d"),
            "Open": f"${float(candle.open_price):,.2f}",
            "High": f"${float(candle.high_price):,.2f}",
            "Low": f"${float(candle.low_price):,.2f}",
            "Close": f"${float(candle.close_price):,.2f}",
            "Volume": f"{float(candle.volume):,.0f}"
        }
        table_data.append(row)
    
    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, height=400)


def fetch_live_data():
    """Fetch historical market data with user feedback."""
    progress_placeholder = st.empty()
    status_placeholder = st.empty()
    
    try:
        with progress_placeholder.container():
            st.info("🔄 Fetching historical data from Binance...")
        
        with status_placeholder.container():
            st.write("📅 Fetching weekly candles from 2019 to present...")
        
        market_data = fetch_historical_data(
            symbol=st.session_state.settings['symbol']
        )
        
        if market_data and market_data.candles:
            st.session_state.market_data = market_data
            
            candle_count = len(market_data.candles)
            start_date = market_data.candles[0].timestamp.strftime("%Y-%m-%d")
            end_date = market_data.candles[-1].timestamp.strftime("%Y-%m-%d")
            
            st.session_state.last_refresh = f"✅ {candle_count} candles ({start_date} to {end_date})"
            
            progress_placeholder.empty()
            status_placeholder.empty()
            
            st.success(f"✅ Fetched {candle_count} weekly candles ({start_date} to {end_date})")
            
            cache_data(f"market_data_{st.session_state.settings['symbol']}", market_data)
            
        else:
            progress_placeholder.empty()
            status_placeholder.empty()
            st.error("❌ Failed to fetch market data from Binance API")
            st.session_state.last_refresh = "❌ Failed to fetch data"
            
    except Exception as e:
        progress_placeholder.empty()
        status_placeholder.empty()
        error_msg = f"❌ Error: {str(e)}"
        st.error(error_msg)
        st.session_state.last_refresh = error_msg
        st.write("**Debug Info:**")
        st.code(str(e))


def render_debug_info():
    """Render debug information."""
    st.subheader("🔧 Debug Information")
    
    debug_data = {
        "app_version": "1.0.0-clean",
        "symbol": st.session_state.settings['symbol'],
        "timeframe": st.session_state.settings['timeframe'],
        "market_data_loaded": bool(st.session_state.market_data),
        "last_refresh": st.session_state.last_refresh or "Never"
    }
    
    if st.session_state.market_data:
        debug_data.update({
            "candle_count": len(st.session_state.market_data.candles),
            "first_candle": str(st.session_state.market_data.candles[0].timestamp),
            "last_candle": str(st.session_state.market_data.candles[-1].timestamp)
        })
    
    st.json(debug_data)
