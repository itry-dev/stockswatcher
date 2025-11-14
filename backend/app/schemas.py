from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class WatchCreate(BaseModel):
    ticker: str
    levels: List[float]
    enabled: bool = True


class WatchRead(BaseModel):
    id: int
    ticker: str
    levels: List[float]
    enabled: bool
    last_alert_hash: Optional[str]


class StatusRead(BaseModel):
    ticker: str
    price: float
    currency: str = 'USD'
    nearest_level: Optional[float]
    distance_pct: float
    near: bool
    open_price: Optional[float] = None
    price_change_pct: Optional[float] = None


class InfoRead(BaseModel):
    last_update: Optional[datetime]
    next_update: Optional[datetime]
    check_interval_minutes: int
    market_status: str  # Overall status: 'open', 'closed', 'pre-market', 'after-hours'
    markets: dict  # Per-exchange market status breakdown


class StockDetailsRead(BaseModel):
    ticker: str
    name: Optional[str]
    currency: str
    current_price: Optional[float]
    
    # Market data
    market_cap: Optional[float]
    volume: Optional[int]
    avg_volume: Optional[int]
    fifty_two_week_high: Optional[float]
    fifty_two_week_low: Optional[float]
    fifty_two_week_change: Optional[float]
    beta: Optional[float]
    
    # Valuation
    pe_ratio: Optional[float]
    forward_pe: Optional[float]
    peg_ratio: Optional[float]
    price_to_book: Optional[float]
    price_to_sales: Optional[float]
    enterprise_value: Optional[float]
    
    # Profitability
    profit_margin: Optional[float]
    operating_margin: Optional[float]
    roe: Optional[float]
    roa: Optional[float]
    
    # Growth
    revenue_growth: Optional[float]
    earnings_growth: Optional[float]
    
    # Dividends
    dividend_yield: Optional[float]
    payout_ratio: Optional[float]
    ex_dividend_date: Optional[str]
    
    # Financial health
    debt_to_equity: Optional[float]
    current_ratio: Optional[float]
    quick_ratio: Optional[float]
    free_cashflow: Optional[float]
    
    # Analyst info
    target_mean_price: Optional[float]
    target_high_price: Optional[float]
    target_low_price: Optional[float]
    recommendation_mean: Optional[float]
    recommendation_key: Optional[str]
    number_of_analyst_opinions: Optional[int]


class HistoricalPriceRead(BaseModel):
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int