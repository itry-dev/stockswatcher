from typing import Optional, Tuple
from .models import PriceCache, Watch
from .schemas import StatusRead
from .config import settings


class StockService:
    """Service for stock-related business logic calculations"""
    
    def __init__(self, repo, provider):
        """Initialize with repository and data provider dependencies"""
        self.repo = repo
        self.provider = provider
    
    def get_price(self, ticker: str, force_update: bool = False) -> Optional[Tuple[PriceCache, bool]]:
        """
        Get price from cache or fetch from provider.
        
        Args:
            ticker: Stock ticker symbol
            force_update: If True, always fetch fresh data from provider
            
        Returns:
            Tuple of (PriceCache, was_fetched) where was_fetched indicates if new data was retrieved
        """
        was_fetched = False
        
        # If force_update or no cached price, fetch from provider
        if force_update or not self.repo.get_price(ticker):
            try:
                # Fetch new price
                price, asof, currency, exchange, timezone_name, market_state, open_price = self.provider.get_last(ticker)
                
                # Update cache with open_price for daily % change calculation
                self.repo.set_price(ticker, price, asof, currency, exchange, timezone_name, market_state, open_price)
                was_fetched = True
            except Exception as e:
                raise Exception(f"Failed to fetch price for {ticker}: {e}")
        
        pc = self.repo.get_price(ticker)
        return (pc, was_fetched)
    
    @staticmethod
    def calculate_price_change_pct(current_price: float, open_price: Optional[float]) -> Optional[float]:
        """Calculate percentage change between current price and market opening price"""
        if open_price and open_price > 0:
            return ((current_price - open_price) / open_price) * 100
        return None
    
    @staticmethod
    def calculate_distance_to_level(price: float, level: float) -> float:
        """Calculate percentage distance from price to a level"""
        return abs(price - level) / level
    
    @staticmethod
    def is_near_level(price: float, level: float, threshold: Optional[float] = None) -> bool:
        """Check if price is near a level within threshold"""
        if threshold is None:
            threshold = settings.NEAR_LEVEL_PCT
        distance = StockService.calculate_distance_to_level(price, level)
        return distance <= threshold
    
    @staticmethod
    def find_nearest_level(price: float, levels: list[float]) -> Optional[float]:
        """Find the nearest level to the current price"""
        if not levels:
            return None
        return min(levels, key=lambda L: abs(price - L))
    
    @staticmethod
    def create_status_read(
        ticker: str,
        price_cache: PriceCache,
        levels: list[float]
    ) -> StatusRead:
        """Create a StatusRead object with all calculations"""
        # Calculate price change from market open
        price_change_pct = StockService.calculate_price_change_pct(
            price_cache.price,
            price_cache.open_price
        )
        
        # Find nearest level and calculate distance
        nearest_level = StockService.find_nearest_level(price_cache.price, levels)
        
        if nearest_level is not None:
            distance_pct = StockService.calculate_distance_to_level(price_cache.price, nearest_level)
            near = distance_pct <= settings.NEAR_LEVEL_PCT
        else:
            distance_pct = 0.0
            near = False
        
        return StatusRead(
            ticker=ticker,
            price=price_cache.price,
            currency=price_cache.currency,
            nearest_level=nearest_level,
            distance_pct=distance_pct,
            near=near,
            open_price=price_cache.open_price,
            price_change_pct=price_change_pct
        )
    
    @staticmethod
    def create_status_dict(
        ticker: str,
        price: float,
        currency: str,
        open_price: Optional[float],
        levels: list[float]
    ) -> dict:
        """Create a status dictionary for WebSocket broadcast"""
        # Calculate price change from market open
        price_change_pct = StockService.calculate_price_change_pct(price, open_price)
        
        # Find nearest level and calculate distance
        nearest_level = StockService.find_nearest_level(price, levels)
        
        if nearest_level is not None:
            distance_pct = StockService.calculate_distance_to_level(price, nearest_level)
            near = distance_pct <= settings.NEAR_LEVEL_PCT
        else:
            distance_pct = 0.0
            near = False
        
        return {
            "ticker": ticker,
            "price": price,
            "currency": currency,
            "nearest_level": nearest_level,
            "distance_pct": distance_pct,
            "near": near,
            "open_price": open_price,
            "price_change_pct": price_change_pct,
        }

