from typing import Optional, List
from datetime import datetime


class Watch:
    ticker: str
    levels: List[float]
    enabled: bool = True
    last_alert_hash: Optional[str] = None
    updated_at: datetime
    
    def __init__(self, ticker: str, levels: List[float], enabled: bool = True, 
                 last_alert_hash: Optional[str] = None, updated_at: Optional[datetime] = None):
        self.ticker = ticker
        self.levels = levels
        self.enabled = enabled
        self.last_alert_hash = last_alert_hash
        self.updated_at = updated_at or datetime.utcnow()


class PriceCache:
    ticker: str
    price: float
    asof: datetime
    currency: str = 'USD'
    exchange: str = 'Unknown'
    timezone: str = 'America/New_York'
    market_state: Optional[str] = None  # Yahoo's real-time market state
    open_price: Optional[float] = None  # Market opening price for daily % change
    
    def __init__(self, ticker: str, price: float, asof: datetime, currency: str = 'USD', 
                 exchange: str = 'Unknown', timezone: str = 'America/New_York',
                 market_state: Optional[str] = None, open_price: Optional[float] = None):
        self.ticker = ticker
        self.price = price
        self.asof = asof
        self.currency = currency
        self.exchange = exchange
        self.timezone = timezone
        self.market_state = market_state
        self.open_price = open_price