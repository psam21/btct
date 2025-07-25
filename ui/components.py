"""
UI Components for Bitcoin Historical Data App

Simple Streamlit UI for fetching and displaying Bitcoin historical data.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import io
import sys
from contextlib import redirect_stdout, redirect_stderr

from apis.models import MarketData
from apis.binance import fetch_historical_data
from utils.cache import cache_data


class LogCapture:
    """Capture all logs and outputs for instrumentation."""
    def __init__(self):
        self.logs = []
    
    def write(self, message):
        if message.strip():
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            self.logs.append(f"[{timestamp}] {message.strip()}")
    
    def flush(self):
        pass
    
    def get_logs(self):
        return self.logs
    
    def clear_logs(self):
        self.logs.clear()


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
        st.session_state.log_capture = LogCapture()
        st.session_state.settings = {
            'symbol': 'BTCUSDT',
            'timeframe': '1w',
            'show_debug': False
        }
        st.session_state.user_actions = []


def log_user_action(action: str):
    """Log user actions for instrumentation."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.user_actions.append(f"[{timestamp}] USER ACTION: {action}")
    st.session_state.log_capture.write(f"USER ACTION: {action}")


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
    symbol = st.sidebar.selectbox(
        "Trading Pair",
        options=["BTCUSDT"],
        index=0
    )
    
    if symbol != st.session_state.settings['symbol']:
        log_user_action(f"Changed symbol to {symbol}")
        st.session_state.settings['symbol'] = symbol
    
    timeframe = st.sidebar.selectbox(
        "Timeframe",
        options=["1w"],
        index=0,
        help="Weekly timeframe"
    )
    
    if timeframe != st.session_state.settings['timeframe']:
        log_user_action(f"Changed timeframe to {timeframe}")
        st.session_state.settings['timeframe'] = timeframe
    
    # Data Controls
    st.sidebar.subheader("📊 Actions")
    
    if st.sidebar.button("🔄 Fetch Historical Data", type="primary"):
        log_user_action("Clicked 'Fetch Historical Data' button")
        fetch_live_data()
        st.rerun()
    
    if st.sidebar.button("🗑️ Clear Data"):
        log_user_action("Clicked 'Clear Data' button")
        st.session_state.market_data = None
        st.session_state.last_refresh = None
        st.rerun()
    
    if st.sidebar.button("🧹 Clear Logs"):
        log_user_action("Clicked 'Clear Logs' button")
        st.session_state.log_capture.clear_logs()
        st.session_state.user_actions.clear()
        st.rerun()
    
    # Debug
    show_debug = st.sidebar.checkbox(
        "Show Debug Info", 
        value=st.session_state.settings['show_debug']
    )
    
    if show_debug != st.session_state.settings['show_debug']:
        log_user_action(f"Toggled debug info: {show_debug}")
        st.session_state.settings['show_debug'] = show_debug
    
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
    """Render main application content with tabs."""
    # Create tabs
    if st.session_state.market_data:
        tab1, tab2, tab3 = st.tabs(["📊 Data", "🔧 Instrumentation", "🐛 Debug"])
    else:
        tab1, tab2 = st.tabs(["📊 Data", "🔧 Instrumentation"])
        tab3 = None
    
    with tab1:
        if st.session_state.market_data is None:
            render_empty_data_view()
        else:
            render_data_dashboard()
    
    with tab2:
        render_instrumentation()
    
    if tab3:
        with tab3:
            render_debug_info()


def render_empty_data_view():
    """Render empty state with just the table structure."""
    st.subheader("📊 OHLC Data")
    st.info("👆 Use the **'Fetch Historical Data'** button in the sidebar to load data")
    
    # Show empty table structure
    empty_df = pd.DataFrame(columns=["Date", "Open", "High", "Low", "Close", "Volume"])
    st.dataframe(empty_df, use_container_width=True, height=200)


def render_instrumentation():
    """Render full instrumentation and logging tab."""
    st.subheader("🔧 User Activity & System Instrumentation")
    
    col1, col2 = st.columns([2, 1])
    
    with col2:
        if st.button("🔄 Refresh Logs"):
            st.rerun()
        
        st.markdown("**Log Statistics:**")
        st.metric("User Actions", len(st.session_state.user_actions))
        st.metric("System Logs", len(st.session_state.log_capture.get_logs()))
    
    with col1:
        # User Actions Tab
        st.markdown("### 👤 User Actions")
        if st.session_state.user_actions:
            user_actions_text = "\n".join(st.session_state.user_actions)
            st.text_area(
                "User Actions Log",
                value=user_actions_text,
                height=200,
                key="user_actions_display"
            )
        else:
            st.info("No user actions recorded yet")
    
    # System Logs
    st.markdown("### 🖥️ System Logs & API Calls")
    system_logs = st.session_state.log_capture.get_logs()
    if system_logs:
        system_logs_text = "\n".join(system_logs)
        st.text_area(
            "System Logs",
            value=system_logs_text,
            height=300,
            key="system_logs_display"
        )
    else:
        st.info("No system logs captured yet")
    
    # Session State Inspector
    st.markdown("### 🔍 Session State Inspector")
    if st.checkbox("Show Session State Details"):
        st.json({
            "market_data_loaded": st.session_state.market_data is not None,
            "candles_count": len(st.session_state.market_data.candles) if st.session_state.market_data else 0,
            "last_refresh": st.session_state.last_refresh,
            "settings": st.session_state.settings,
            "initialized": st.session_state.initialized
        })
    
    # Real-time monitoring
    st.markdown("### 📊 Real-time Status")
    status_col1, status_col2, status_col3 = st.columns(3)
    
    with status_col1:
        api_status = "🟢 Connected" if st.session_state.last_refresh and "✅" in st.session_state.last_refresh else "🔴 Disconnected"
        st.markdown(f"**API Status:** {api_status}")
    
    with status_col2:
        data_status = "✅ Loaded" if st.session_state.market_data else "⚠️ No Data"
        st.markdown(f"**Data Status:** {data_status}")
    
    with status_col3:
        current_time = datetime.now().strftime("%H:%M:%S")
        st.markdown(f"**Current Time:** {current_time}")


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
    """Fetch historical market data with user feedback and full instrumentation."""
    log_user_action("Starting data fetch process")
    
    progress_placeholder = st.empty()
    status_placeholder = st.empty()
    
    # Redirect stdout and stderr to capture all logs
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    
    try:
        # Capture all output
        sys.stdout = st.session_state.log_capture
        sys.stderr = st.session_state.log_capture
        
        with progress_placeholder.container():
            st.info("🔄 Fetching historical data from Binance...")
        
        st.session_state.log_capture.write("Starting Binance API data fetch")
        
        # Add network connectivity check for Streamlit Cloud
        with status_placeholder.container():
            st.write("🌐 Checking Binance API connectivity...")
        
        st.session_state.log_capture.write("Checking Binance API connectivity...")
        
        from apis.binance import check_api_connection
        if not check_api_connection():
            st.session_state.log_capture.write("❌ API connection failed - network restrictions detected")
            progress_placeholder.empty()
            status_placeholder.empty()
            st.error("❌ Cannot connect to Binance API. This may be due to network restrictions on Streamlit Cloud.")
            st.info("💡 **Streamlit Cloud Issue**: External API access may be limited. Try running locally or contact Streamlit support.")
            st.session_state.last_refresh = "❌ API connection failed"
            log_user_action("Data fetch failed - API connection issue")
            return
        
        st.session_state.log_capture.write("✅ API connection successful")
        
        with status_placeholder.container():
            st.write("📅 Fetching weekly candles from 2019 to present...")
        
        st.session_state.log_capture.write(f"Fetching historical data for {st.session_state.settings['symbol']}")
        
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
            
            st.session_state.log_capture.write(f"✅ Successfully fetched {candle_count} candles from {start_date} to {end_date}")
            log_user_action(f"Data fetch successful - {candle_count} candles loaded")
            
            cache_data(f"market_data_{st.session_state.settings['symbol']}", market_data)
            st.session_state.log_capture.write("Data cached successfully")
            
        else:
            st.session_state.log_capture.write("❌ Failed to fetch market data - no data returned")
            progress_placeholder.empty()
            status_placeholder.empty()
            st.error("❌ Failed to fetch market data from Binance API")
            st.warning("🚨 **Streamlit Cloud Limitation**: This app requires external API access which may be restricted on Streamlit Community Cloud.")
            st.info("💡 **Solutions**: Run locally or consider using Streamlit Cloud for Business which has fewer network restrictions.")
            st.session_state.last_refresh = "❌ Failed to fetch data"
            log_user_action("Data fetch failed - no data returned")
            
    except Exception as e:
        st.session_state.log_capture.write(f"❌ Exception during data fetch: {str(e)}")
        progress_placeholder.empty()
        status_placeholder.empty()
        error_msg = f"❌ Error: {str(e)}"
        st.error(error_msg)
        
        # Add specific guidance for common Streamlit Cloud issues
        if "timeout" in str(e).lower() or "connection" in str(e).lower():
            st.warning("🚨 **Network Issue**: This appears to be a network connectivity problem.")
            st.info("💡 **Streamlit Cloud**: External API calls may be blocked or limited on the free tier.")
            st.session_state.log_capture.write("Network connectivity issue detected")
        
        st.session_state.last_refresh = error_msg
        log_user_action(f"Data fetch failed with error: {str(e)}")
        
    finally:
        # Restore stdout and stderr
        sys.stdout = old_stdout
        sys.stderr = old_stderr


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
