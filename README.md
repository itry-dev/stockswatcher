# StocksWatcher

A real-time stock price monitoring application with comprehensive financial analysis, customizable price alerts, and optional Telegram notifications.

## 🎯 What is StocksWatcher?

StocksWatcher is a self-hosted solution for investors and traders who want to:
- **Track Multiple Stocks**: Monitor dozens of stocks in real-time from a single dashboard
- **Set Price Targets**: Configure custom price levels and get notified when stocks approach them
- **Make Informed Decisions**: Access detailed financial metrics, analyst ratings, and historical charts for each stock
- **Stay Updated**: Receive optional Telegram alerts when price targets are near (disabled by default for privacy)
- **Maintain Privacy**: Your watchlist and data stay on your own server—nothing sent to third parties

Perfect for day traders, long-term investors, or anyone who wants to keep a close eye on their portfolio without constantly checking multiple websites.

## ✨ Key Features

- 📊 **Real-time Price Monitoring**: WebSocket updates every 5 minutes (configurable)
- 🎯 **Custom Price Levels**: Set multiple target prices per stock with proximity alerts
- 📈 **Comprehensive Stock Analysis**: Click any ticker to view detailed financial metrics, charts, and analyst ratings
- 🔔 **Optional Telegram Alerts**: Get notified when stocks approach target levels (opt-in)
- 💱 **Multi-Currency Support**: Displays prices in native currencies (USD, EUR, etc.)
- 🔍 **Ticker Validation**: Verifies stocks exist on Yahoo Finance before adding
- 🐳 **Docker Ready**: One-command deployment with Docker Compose

## Overview

StocksWatcher monitors stock prices at regular intervals and alerts you when prices get close to predefined levels. It features a FastAPI backend for data processing and optional notifications, and a Vue.js frontend for managing watched stocks and viewing real-time status updates.

## Backend

The backend is built with **FastAPI** and provides:

### Core Features
- **Scheduled Price Monitoring**: Uses APScheduler to fetch stock prices from Yahoo Finance at configurable intervals
- **Price Level Tracking**: Monitors multiple price levels per stock ticker
- **Optional Telegram Notifications**: Sends alerts when stock prices come within a threshold percentage of target levels (must be explicitly enabled)
- **Smart Alert Deduplication**: Prevents duplicate notifications using hash-based tracking
- **Real-time Updates**: WebSocket support for live price updates to connected clients
- **MongoDB Database**: Persists watch configurations and price cache using MongoDB

### Key Components
- `main.py`: FastAPI application with REST endpoints and WebSocket support
- `watcher.py`: Core monitoring logic that checks prices against configured levels
- `data_provider.py`: Integrates with Yahoo Finance API via yfinance library
- `telegram_notifier.py`: Handles Telegram bot messaging
- `repository.py`: Database operations for watches and price cache with MongoDB
- `models.py`: Data models for Watch and PriceCache

### API Endpoints
- `GET /watches`: List all configured stock watches
- `POST /watches`: Add or update a stock watch with price levels (validates ticker exists on Yahoo Finance)
- `GET /status`: Get current prices and distance to nearest levels for all watches (fetches from cache or Yahoo Finance if not available)
- `GET /info`: Get last update time, next update time, and check interval
- `GET /stocks/{ticker}/details`: Get comprehensive financial details for a stock (valuation, profitability, dividends, analyst ratings, etc.)
- `GET /stocks/{ticker}/history`: Get historical price data for charting (configurable period and interval)
- `WS /ws`: WebSocket endpoint for real-time status updates

### Configuration
Configured via environment variables:
- `MONGODB_URL`: MongoDB connection string (default: `mongodb://localhost:27017`)
- `MONGODB_DB_NAME`: MongoDB database name (default: `stockswatcher`)
- `CHECK_INTERVAL_MINUTES`: How often to check prices (default: `5`)
- `NEAR_LEVEL_PCT`: Threshold percentage to trigger alerts (default: `0.005` = 0.5%)
- `TELEGRAM_NOTIFICATION_ENABLED`: Enable/disable Telegram notifications (default: `False`)
- `TELEGRAM_BOT_TOKEN`: Telegram bot token (required only if notifications enabled)
- `TELEGRAM_CHAT_ID`: Target chat ID for notifications (required only if notifications enabled)
- `TICKER_MAP`: Mapping of custom ticker names to Yahoo Finance symbols

## Frontend

The frontend is built with **Vue 3**, **TypeScript**, and **Tailwind CSS**:

### Features
- **Dedicated Add Watch Component**: Separate form for adding stocks with validation
- **Ticker Validation**: Verifies tickers exist on Yahoo Finance before adding
- **Interactive Watch Table**: Displays all configured stocks with their target levels
- **Real-time Price Updates**: WebSocket connection shows live prices without page refresh
- **Stock Details Page**: Click any ticker to view comprehensive financial analysis including:
  - Interactive price chart with historical data (powered by Chart.js)
  - Market data (market cap, volume, 52-week range, beta)
  - Valuation metrics (P/E, PEG, Price/Book, Price/Sales)
  - Profitability indicators (profit margins, ROE, ROA)
  - Growth metrics (revenue and earnings growth)
  - Dividend information (yield, payout ratio, ex-dividend date)
  - Financial health (debt/equity, current ratio, free cash flow)
  - Analyst ratings and price targets with color-coded recommendation badges
- **Visual Indicators**: Highlights when stocks are near target levels with colored badges
- **Quick Presets**: One-click buttons to add common stock configurations (TXN, INTC, STM, ENI, ENEL)
- **Flexible Levels**: Price levels are optional - you can add a watch without any levels
- **Currency Support**: Displays prices in their native currency (USD, EUR, etc.)
- **Timing Information**: Shows last update time and when the next price check will occur

### Key Components
- `App.vue`: Main application layout with router support
- `Home.vue`: Home page wrapper for the watch table
- `AddWatch.vue`: Dedicated form component for adding new stock watches with preset buttons
- `WatchTable.vue`: Interactive table showing watches, current prices, nearest levels, and proximity alerts
- `StockDetails.vue`: Comprehensive stock details page with financial metrics and charts
- `PriceChart.vue`: Interactive price chart component using Chart.js and vue-chartjs
- `DataItem.vue`: Reusable component for displaying labeled data values
- `api.ts`: API client for backend communication
- `router.ts`: Vue Router configuration for navigation
- `composables/useFormatters.ts`: Reusable formatting utilities for currency, numbers, percentages, and key labels

### Display Information
For each watched stock, the table shows:
- **Ticker**: Stock symbol
- **Levels**: Configured price levels to monitor
- **Price**: Current price from latest fetch
- **Open**: Market opening price for daily % change calculation
- **% Change**: Percentage change from market open (positive = green, negative = red)
- **Nearest**: Closest configured level to current price
- **Distance %**: Percentage distance to nearest level
- **Near**: Visual indicator if price is within alert threshold

## Tech Stack

**Backend:**
- FastAPI
- MongoDB (via pymongo)
- APScheduler
- yfinance (Yahoo Finance API)
- python-telegram-bot
- WebSockets

**Frontend:**
- Vue 3 (Composition API)
- TypeScript
- Tailwind CSS
- Vite
- Vue Router
- Chart.js & vue-chartjs
- Axios

## Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- MongoDB (local or Docker)

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

Start MongoDB:
```bash
# Using Docker
docker run -d -p 27017:27017 --name mongodb mongo:7

# Or use the docker-compose setup (see below)
```

Configure environment variables in `.env` file:
```
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=stockswatcher
CHECK_INTERVAL_MINUTES=5
NEAR_LEVEL_PCT=0.005

# Optional: Enable Telegram notifications
TELEGRAM_NOTIFICATION_ENABLED=true
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

> **Note**: Telegram notifications are disabled by default. To enable them, set `TELEGRAM_NOTIFICATION_ENABLED=true` and provide valid `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` values.

Run the backend:
```bash
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Docker Compose

**Option 1: Full Stack (All services in Docker)**
```bash
docker-compose up --build
```

This will start:
- MongoDB on port 27018 (mapped from 27017)
- Backend on port 8000
- Frontend on port 5273 (internally uses 5183)

Access the app at `http://localhost:5273`

**Option 2: MongoDB only (Recommended for development)**
```bash
# Start only MongoDB
docker-compose up -d mongodb

# Run backend locally (in one terminal)
cd backend
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
uvicorn app.main:app --reload

# Run frontend locally (in another terminal)
cd frontend
npm run dev
```

> **Note**: When running the full stack with Docker Compose, the frontend connects to the backend at `http://localhost:8000` from your browser. WebSocket connections should work automatically on the same host.
- Backend on port 8000
- Frontend on port 5173

## How It Works

1. Add stocks through the dedicated AddWatch form component in the frontend UI (tickers are validated against Yahoo Finance)
2. Configure optional target price levels for each stock (levels are not required)
3. Click any ticker in the watch table to view detailed financial analysis and interactive price charts
4. The backend scheduler fetches current prices from Yahoo Finance every N minutes
5. Both watches and prices are stored in MongoDB collections (watches and prices collections)
6. When loading the status page, prices are retrieved from cache; if unavailable, they're fetched from Yahoo Finance on-demand
7. For each stock with levels, it calculates the distance to the nearest configured level
8. When a price comes within the threshold percentage, a Telegram alert is sent (if notifications are enabled)
9. Real-time updates are pushed to the frontend via WebSocket during scheduled checks
10. The UI highlights stocks that are currently "near" their target levels
11. Stock details page provides comprehensive investment analysis with:
    - Historical price charts (customizable periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
    - Key financial metrics organized by category
    - Color-coded recommendation badges based on analyst ratings
    - All data sourced from Yahoo Finance API

## Testing

A Python test script is included to validate Yahoo Finance API responses:

```bash
python test_yahoo_api.py AAPL
```

This creates a detailed log file (`yahoo_test_AAPL_[timestamp].txt`) containing:
- Fast info attributes
- Full info dictionary with all available fields
- Historical price data
- Income statement
- Recommendations
- All available ticker attributes

> **Note**: Both `test_yahoo_api.py` and generated `yahoo_test_*.txt` files are excluded from git via `.gitignore`

### Testing Telegram Notifications

Before enabling Telegram notifications in production, you can test your bot configuration using the included test script:

```bash
python test_telegram.py <BOT_TOKEN> <CHAT_ID>
```

**Example:**
```bash
python test_telegram.py 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11 -1001234567890
```

The script will send three test messages to your Telegram bot:
1. Simple stock alert with basic formatting
2. Multi-ticker alert showing multiple stocks
3. Formatted alert with emojis and detailed information

**How to get credentials:**
1. **BOT_TOKEN**: Create a bot via [@BotFather](https://t.me/BotFather) on Telegram
2. **CHAT_ID**: Send a message to your bot, then visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`

If you receive all three test messages, your Telegram integration is configured correctly!
