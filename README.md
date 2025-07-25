# Bitcoin Futures Trading Signal App

A Streamlit-based Bitcoin (BTC/USDT) perpetual futures trading signal application that detects bullish/bearish engulfing candlestick patterns and generates trading signals on weekly timeframes.

## Features

- **Real-time BTC/USDT perpetual futures data** from Binance
- **Candlestick pattern detection** (bullish/bearish engulfing patterns)
- **Trading signal generation** with commentary
- **Interactive data table** with OHLC data and signals
- **Caching system** for optimal performance
- **Streamlit Cloud deployment** ready

## Documentation

- **[Project Plan](docs/PROJECT_PLAN.md)** - Comprehensive 7-phase implementation roadmap
- **[Requirements](docs/BTCT_Req.md)** - Detailed functional requirements (FR001-FR018)

## Requirements

- Python 3.9+
- Binance API access (no authentication required for public data)
- Internet connection for data fetching

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd btc_futures_signal_app
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
streamlit run app.py
```

## Development

### Project Structure

```
btc_futures_signal_app/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Dependencies
├── README.md                   # Documentation
├── .gitignore                  # Git ignore rules
├── .env.example               # Environment variables template
├── docs/                      # Project documentation
│   ├── PROJECT_PLAN.md        # Implementation roadmap
│   └── BTCT_Req.md           # Functional requirements
├── apis/                      # Binance API integration
├── logic/                     # Signal generation logic
├── ui/                        # UI components
├── plots/                     # Chart components (optional)
├── utils/                     # Utilities (cache, config, etc.)
├── tests/                     # Test suite
└── .streamlit/               # Streamlit configuration
```

### Running Tests

```bash
pytest tests/ -v --cov=. --cov-report=html
```

### Code Quality

```bash
# Format code
black .
isort .

# Lint code
flake8 .
mypy .
```

## Usage

1. **Launch the app**: `streamlit run app.py`
2. **Select date range**: Use the sidebar controls to select analysis period
3. **View signals**: Check the data table for trading signals and commentary
4. **Analyze patterns**: Review detected bullish/bearish engulfing patterns

## Technical Details

### Signal Generation Logic

- **Bullish Engulfing**: Previous red candle + current green candle that completely engulfs it
- **Bearish Engulfing**: Previous green candle + current red candle that completely engulfs it
- **Signal Timing**: Signals generated for next candle open after pattern detection

### Data Source

- **Symbol**: BTC/USDT Perpetual Futures
- **Timeframe**: Weekly (1w)
- **Data Range**: 2019 to present
- **Source**: Binance Futures API

## License

This project is for educational and research purposes.

## Contributing

1. Fork the repository
2. Create feature branch
3. Implement changes with tests
4. Submit pull request

## Support

For issues and questions, please create an issue in the repository.
