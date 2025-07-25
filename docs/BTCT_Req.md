# 📈 Bitcoin Fut---

## 2. 🏗️ Application Architecture & Structure

### FR003: Modular ### FR008: Criteria for "Go Long"
- A **"Go Long"** signal shall be generated when a **bullish engulfing candlestick pattern** is identified.
- Pattern detection logic shall be implemented in **`logic/signal_engine.py`**.
- This pattern occurs when:
  - The body of the second candle **completely engulfs** the body of the previous red candle.
  - The second candle is **green (bullish)**.

### FR009: Criteria for "Go Short"
- A **"Go Short"** signal shall be generated when a **bearish engulfing candlestick pattern** is identified.
- Pattern detection logic shall be implemented in **`logic/signal_engine.py`**.
- This pattern occurs when:
  - The body of the second candle **completely engulfs** the body of the previous green candle.
  - The second candle is **red (bearish)**.

### FR010: Signal Timing- The application shall follow a **modular architecture** with clear separation of concerns, organized into the following structure:
  ```
  btc_futures_signal_app/
  ├── app.py                      # Minimal entry point
  ├── requirements.txt
  ├── README.md
  ├── apis/                       # Binance API interaction
  │   └── binance.py
  ├── logic/                      # Trading signal logic
  │   └── signal_engine.py
  ├── ui/                         # Streamlit layout controls
  │   └── components.py
  ├── plots/                      # Charting layer
  │   └── charting.py
  ├── utils/                      # Common helpers
  │   └── cache.py
  ├── tests/                      # Test suite
  │   ├── test_signals.py
  │   └── test_binance_api.py
  └── .streamlit/                 # Streamlit config
      └── config.toml
  ```

### FR004: Component Responsibilities
- **`app.py`**: Minimal entry point that orchestrates components and handles Streamlit configuration
- **`apis/binance.py`**: Binance API integration for fetching historical and real-time data
- **`logic/signal_engine.py`**: Core business logic for pattern detection and signal generation
- **`ui/components.py`**: Streamlit UI components and layout management
- **`plots/charting.py`**: Plotly-based charting functionality (optional feature)
- **`utils/cache.py`**: Caching abstraction layer for data persistence and performance optimization

### FR005: Data Persistence & Caching Strategy
- **Initial Implementation**: Use **Streamlit's session state** and `st.cache_data` for in-memory caching
- **Caching Layer**: Implement a dedicated caching abstraction in `utils/cache.py` to:
  - Cache fetched historical candlestick data
  - Store intermediate computation results (detected patterns)
  - Provide configurable cache TTL settings
- **Future Enhancement**: Caching abstraction will allow easy migration to persistent storage (SQLite, PostgreSQL) without code changes in other modulesnal App - Requirements Specification

This document outlines the **techno-functional specifications** for a **Streamlit-based application** that generates **trading signals for Bitcoin (BTC/USDT) perpetual futures** on the **Binance** exchange.

---

## 1. 🧱 Application Deployment & Framework

### FR001: Streamlit Framework
- The entire application shall be developed using the **Streamlit** framework, a Python-based open-source app framework that allows rapid development of interactive data applications.
- Streamlit is chosen for its simplicity, interactive capabilities, and ease of deployment in a web environment.

### FR002: Deployable on Streamlit Community Cloud
- The application must be fully **deployable on Streamlit Community Cloud**, which provides free hosting for small-scale apps.
- This deployment ensures public accessibility without the need for external servers or infrastructure setup.

---

## 2. 💾 Data Persistence & Caching

### FR003: Initial In-Memory Data Storage
- During the initial version of the application, **Streamlit’s session state** or equivalent in-memory caching (e.g., `st.cache_data`) shall be used for temporary data storage and reuse.
- Cached data includes:
  - Fetched historical candlestick data
  - Intermediate computation results (e.g., detected patterns)

### FR004: Future Data Persistence Enhancement
- A future upgrade will introduce a **persistent storage layer** such as SQLite, PostgreSQL, or other suitable databases.
- This will allow the application to:
  - Retain historical analysis across sessions
  - Enable querying and retrieval of past signals
  - Improve scalability and long-term performance

---

## 3. 🔍 Core Trading Signal Logic

### FR006: Signal Generation for BTC/USDT Perpetual Futures
- The primary function is to analyze the **BTC/USDT perpetual futures** market from Binance and produce **buy/sell signals** based on candlestick patterns.
- All signal generation logic shall be implemented in the **`logic/signal_engine.py`** module.

### FR007: Signal Types
- The system shall generate two types of trading signals:
  - **“Go Long”** (buy opportunity)
  - **“Go Short”** (sell opportunity)

### FR007: Criteria for “Go Long”
- A **“Go Long”** signal shall be generated when a **bullish engulfing candlestick pattern** is identified.
- This pattern occurs when:
  - The body of the second candle **completely engulfs** the body of the previous red candle.
  - The second candle is **green (bullish)**.

### FR008: Criteria for “Go Short”
- A **“Go Short”** signal shall be generated when a **bearish engulfing candlestick pattern** is identified.
- This pattern occurs when:
  - The body of the second candle **completely engulfs** the body of the previous green candle.
  - The second candle is **red (bearish)**.

### FR009: Signal Timing
- All trading signals are to be **emitted at the open of the candle** immediately following the engulfing pattern.
- This ensures the signal is based on confirmed data and avoids mid-candle predictions.

---

## 4. 📊 Data Visualization & Output

### FR011: OHLC Data Table
- The application shall render a **tabular display** of candlestick data for the selected time interval.
- Table rendering logic shall be implemented in **`ui/components.py`**.
- Columns shall include: **Open**, **High**, **Low**, **Close**, and **Timestamp**.

### FR012: Trade Commentary
- For each candlestick entry, the table shall include a **commentary field** that:
  - Explains if a signal is triggered (e.g., "Bullish Engulfing Pattern detected – Go Long")
  - Or states that no trade is suggested (e.g., "No pattern detected")
- Commentary generation shall be handled by **`logic/signal_engine.py`** and displayed via **`ui/components.py`**.

### FR013: Optional Visual Chart (Future)
- Optionally (not mandatory for the initial release), the application may include a **Plotly-based candlestick chart**.
- Chart implementation shall be in **`plots/charting.py`** module.
- This chart would:
  - Overlay signals (e.g., green/red arrows or annotations) directly onto the price chart.
  - Provide users with a more intuitive, visual representation of signal timing and price movement.

---

## 5. ⏱️ Candlestick Interval

### FR014: Weekly Candlestick Analysis
- The app shall operate on **1-week (weekly)** candlestick intervals.
- This higher timeframe is chosen to:
  - Reduce noise
  - Focus on long-term signal accuracy
  - Simplify initial data load and visualization

---

## 6. 🔗 Data Acquisition & Caching Strategy

### FR015: Historical Data Fetching from Binance
- The application shall fetch **complete historical BTC/USDT perpetual futures data** from the **Binance API**.
- All API interaction logic shall be implemented in **`apis/binance.py`** module.
- Data must cover the period from **2019 to the current date**.

### FR016: Data Caching Implementation
- Once fetched, historical data must be **stored in cache** using the caching abstraction in **`utils/cache.py`**.
- Benefits include:
  - **Reduced API calls** to Binance
  - **Improved application performance** and user experience
  - **Faster reloads** during session
- Cache implementation shall be modular to allow future migration to persistent storage.

---

## 7. 🧪 Testing & Quality Assurance

### FR017: Test Suite Implementation
- The application shall include a comprehensive test suite in the **`tests/`** directory:
  - **`test_signals.py`**: Unit tests for signal generation logic
  - **`test_binance_api.py`**: Tests for API integration and data fetching
- Tests shall validate:
  - Pattern detection accuracy
  - API connectivity and error handling
  - Data caching functionality
  - Signal timing and generation logic

### FR018: Streamlit Configuration
- Application configuration shall be managed via **`.streamlit/config.toml`** for:
  - Page layout settings
  - Theme customization
  - Performance optimization settings

---

## ✅ Summary of Functional Requirements

| ID     | Feature Description                                                                 | Implementation Module        |
|--------|--------------------------------------------------------------------------------------|------------------------------|
| FR001  | Use Streamlit for frontend and backend                                               | app.py                       |
| FR002  | Deploy on Streamlit Community Cloud                                                  | .streamlit/config.toml       |
| FR003  | Implement modular architecture with clear separation of concerns                     | Project structure            |
| FR004  | Define component responsibilities for maintainable code                              | Multiple modules             |
| FR005  | Implement caching abstraction layer                                                 | utils/cache.py               |
| FR006  | Generate BTC/USDT perpetual signals                                                  | logic/signal_engine.py       |
| FR007  | Signal types: Go Long or Go Short                                                    | logic/signal_engine.py       |
| FR008  | Go Long on bullish engulfing pattern                                                 | logic/signal_engine.py       |
| FR009  | Go Short on bearish engulfing pattern                                                | logic/signal_engine.py       |
| FR010  | Signal generated at open of next candle                                              | logic/signal_engine.py       |
| FR011  | Display OHLC data in a table                                                         | ui/components.py             |
| FR012  | Include comments explaining signals or lack thereof                                  | ui/components.py             |
| FR013  | (Optional) Show visual chart with signals using Plotly                               | plots/charting.py            |
| FR014  | Analyze weekly candlestick data                                                      | logic/signal_engine.py       |
| FR015  | Fetch all historical data from Binance (from 2019 to now)                            | apis/binance.py              |
| FR016  | Cache historical data to reduce API calls                                            | utils/cache.py               |
| FR017  | Implement comprehensive test suite                                                   | tests/                       |
| FR018  | Configure Streamlit application settings                                             | .streamlit/config.toml       |