from datetime import datetime
from typing import Dict
import yfinance as yf
from .config import settings
from logging import getLogger
logger = getLogger("watcher")

class PriceProvider:
    def __init__(self, ticker_map: Dict[str, str]):
        self.map = ticker_map

    def validate_ticker(self, ticker: str) -> bool:
        """Check if a ticker exists on Yahoo Finance"""
        try:
            y_ticker = self.map.get(ticker, ticker)
            stock = yf.Ticker(y_ticker)
            # Use fast_info which is much faster than info
            # Just check if we can get the timezone (which means the ticker exists)
            _ = stock.fast_info.get('timezone')
            return True
        except Exception as e:
            logger.warning(f"Ticker validation failed for {ticker}: {e}")
            return False

    def get_last(self, ticker: str) -> tuple[float, datetime, str, str, str, str | None, float | None]:
        """Returns (price, asof, currency, exchange, timezone, market_state, open_price)"""
        y_ticker = self.map.get(ticker, ticker)
        stock = yf.Ticker(y_ticker)
        
        # Explicitly set auto_adjust to avoid FutureWarning
        data = yf.download(y_ticker, period="1d", interval="1m", progress=False, auto_adjust=True)
        if data.empty:
            raise RuntimeError(f"No data for {ticker}")
        
        last = data.tail(1)
        logger.info(f"Yahoo data for {ticker}: {last}")
        
        # Handle both multi-index and single-index columns for current price
        if 'Close' in data.columns:
            price = float(last['Close'].iloc[0])
        elif ('Close', y_ticker) in data.columns:
            price = float(last['Close'][y_ticker].iloc[0])
        else:
            # Fallback: try to get the first numeric column
            price = float(last.iloc[0, 0])
        
        asof = last.index[-1].to_pydatetime()
        
        # Get currency, exchange, timezone, and open price from fast_info (faster than full info)
        try:
            currency = stock.fast_info.get('currency', 'USD')
            print(f"[DEBUG] {ticker} - currency from fast_info: {currency}")
        except Exception as e:
            print(f"[DEBUG] {ticker} - failed to get currency: {e}")
            currency = 'USD'
        
        try:
            exchange = stock.fast_info.get('exchange', 'Unknown')
            print(f"[DEBUG] {ticker} - exchange from fast_info: {exchange}")
        except Exception as e:
            print(f"[DEBUG] {ticker} - failed to get exchange: {e}")
            exchange = 'Unknown'
        
        try:
            timezone_name = stock.fast_info.get('timezone', 'America/New_York')
            print(f"[DEBUG] {ticker} - timezone from fast_info: {timezone_name}")
        except Exception as e:
            print(f"[DEBUG] {ticker} - failed to get timezone: {e}")
            timezone_name = 'America/New_York'
        
        # Get opening price from fast_info (today's opening price)
        open_price = None
        try:
            open_price = stock.fast_info.get('open')
            print(f"[DEBUG] {ticker} - open price from fast_info: {open_price}")
        except Exception as e:
            print(f"[DEBUG] {ticker} - failed to get open price: {e}")
        
        # Try to get marketState from full info (not available in fast_info)
        market_state = None
        market = None
        try:
            info = stock.info
            market_state = info.get('marketState', None)
            market = info.get('market', None)  # e.g., 'us_market', 'it_market', etc.
            
            # If exchange wasn't in fast_info, try to get it from info
            if exchange == 'Unknown':
                exchange = info.get('exchange', 'Unknown')
                print(f"[DEBUG] {ticker} - exchange from info: {exchange}")
            
            print(f"[DEBUG] {ticker} - Market info: exchange={exchange}, market={market}, state={market_state}, timezone={timezone_name}")
        except Exception as e:
            print(f"[DEBUG] {ticker} - Could not fetch full info: {e}")
        
        return price, asof, currency, exchange, timezone_name, market_state, open_price

    def get_stock_details(self, ticker: str) -> dict:
        """Get comprehensive stock details for investment analysis"""
        y_ticker = self.map.get(ticker, ticker)
        stock = yf.Ticker(y_ticker)
        
        try:
            info = stock.info
            fast = stock.fast_info
            
            # Helper to safely get values from dict
            def safe_get(d, key, default=None):
                try:
                    val = d.get(key, default)
                    return val if val not in [None, 'N/A', float('inf'), float('-inf')] else default
                except:
                    return default
            
            # Helper to safely get values from FastInfo object
            def safe_get_fast(obj, key, default=None):
                try:
                    val = getattr(obj, key, default)
                    return val if val not in [None, 'N/A', float('inf'), float('-inf')] else default
                except:
                    return default
            
            # Helper to convert Unix timestamp to ISO date string
            def safe_get_date(d, key):
                try:
                    val = d.get(key)
                    if val is None:
                        return None
                    # If it's a Unix timestamp (integer)
                    if isinstance(val, (int, float)):
                        from datetime import datetime
                        return datetime.fromtimestamp(val).strftime('%Y-%m-%d')
                    # If it's already a string
                    if isinstance(val, str):
                        return val
                    return None
                except:
                    return None
            
            return {
                'ticker': ticker,
                'name': safe_get(info, 'longName'),
                'currency': safe_get_fast(fast, 'currency', 'USD'),
                'current_price': safe_get_fast(fast, 'last_price'),
                
                # Market data
                'market_cap': safe_get(info, 'marketCap'),
                'volume': safe_get(info, 'volume'),
                'avg_volume': safe_get(info, 'averageVolume'),
                'fifty_two_week_high': safe_get(info, 'fiftyTwoWeekHigh'),
                'fifty_two_week_low': safe_get(info, 'fiftyTwoWeekLow'),
                'fifty_two_week_change': safe_get(info, '52WeekChange'),
                'beta': safe_get(info, 'beta'),
                
                # Valuation
                'pe_ratio': safe_get(info, 'trailingPE'),
                'forward_pe': safe_get(info, 'forwardPE'),
                'peg_ratio': safe_get(info, 'pegRatio'),
                'price_to_book': safe_get(info, 'priceToBook'),
                'price_to_sales': safe_get(info, 'priceToSalesTrailing12Months'),
                'enterprise_value': safe_get(info, 'enterpriseValue'),
                
                # Profitability
                'profit_margin': safe_get(info, 'profitMargins'),
                'operating_margin': safe_get(info, 'operatingMargins'),
                'roe': safe_get(info, 'returnOnEquity'),
                'roa': safe_get(info, 'returnOnAssets'),
                
                # Growth
                'revenue_growth': safe_get(info, 'revenueGrowth'),
                'earnings_growth': safe_get(info, 'earningsGrowth'),
                
                # Dividends
                'dividend_yield': safe_get(info, 'dividendYield'),
                'payout_ratio': safe_get(info, 'payoutRatio'),
                'ex_dividend_date': safe_get_date(info, 'exDividendDate'),
                
                # Financial health
                'debt_to_equity': safe_get(info, 'debtToEquity'),
                'current_ratio': safe_get(info, 'currentRatio'),
                'quick_ratio': safe_get(info, 'quickRatio'),
                'free_cashflow': safe_get(info, 'freeCashflow'),
                
                # Analyst info
                'target_mean_price': safe_get(info, 'targetMeanPrice'),
                'target_high_price': safe_get(info, 'targetHighPrice'),
                'target_low_price': safe_get(info, 'targetLowPrice'),
                'recommendation_mean': safe_get(info, 'recommendationMean'),
                'recommendation_key': safe_get(info, 'recommendationKey'),
                'number_of_analyst_opinions': safe_get(info, 'numberOfAnalystOpinions'),
            }
        except Exception as e:
            logger.error(f"Error fetching stock details for {ticker}: {e}")
            raise RuntimeError(f"Failed to fetch details for {ticker}")

    def get_historical_prices(self, ticker: str, period: str = "1y", interval: str = "1d") -> list:
        """
        Get historical price data for charting
        period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
        interval: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
        """
        y_ticker = self.map.get(ticker, ticker)
        stock = yf.Ticker(y_ticker)
        
        try:
            hist = stock.history(period=period, interval=interval)
            if hist.empty:
                return []
            
            result = []
            for idx, row in hist.iterrows():
                result.append({
                    'date': idx.to_pydatetime(),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume'])
                })
            return result
        except Exception as e:
            logger.error(f"Error fetching historical prices for {ticker}: {e}")
            return []