from .models import Watch, PriceCache
from typing import List, Optional
from datetime import datetime, timezone
from pymongo import MongoClient
from bson import ObjectId


class Repo:
    def __init__(self, mongodb_url: str, mongodb_db_name: str = "stockswatcher"):
        # MongoDB for watches and price cache
        self.mongo_client = MongoClient(mongodb_url)
        self.mongo_db = self.mongo_client[mongodb_db_name]
        self.watches_collection = self.mongo_db.watches
        self.prices_collection = self.mongo_db.prices
        # Create indexes
        self.watches_collection.create_index("ticker", unique=True)
        self.prices_collection.create_index("ticker", unique=True)


    # Watch CRUD - MongoDB only
    def upsert_watch(self, watch: Watch) -> Watch:
        watch_dict = {
            "ticker": watch.ticker,
            "levels": watch.levels,
            "enabled": watch.enabled,
            "last_alert_hash": watch.last_alert_hash,
            "updated_at": datetime.utcnow()
        }
        result = self.watches_collection.update_one(
            {"ticker": watch.ticker},
            {"$set": watch_dict},
            upsert=True
        )
        # Fetch the updated document
        doc = self.watches_collection.find_one({"ticker": watch.ticker})
        return self._mongo_to_watch(doc)


    def list_watches(self) -> List[Watch]:
        docs = self.watches_collection.find()
        return [self._mongo_to_watch(doc) for doc in docs]


    def delete_watch(self, ticker: str) -> bool:
        """Delete a watch by ticker. Returns True if deleted, False if not found."""
        result = self.watches_collection.delete_one({"ticker": ticker})
        return result.deleted_count > 0


    def update_last_alert(self, ticker: str, alert_hash: Optional[str]):
        self.watches_collection.update_one(
            {"ticker": ticker},
            {"$set": {"last_alert_hash": alert_hash, "updated_at": datetime.now(timezone.utc)}}
        )

    def _mongo_to_watch(self, doc: dict) -> Watch:
        """Convert MongoDB document to Watch model"""
        return Watch(
            ticker=doc.get("ticker"),
            levels=doc.get("levels", []),
            enabled=doc.get("enabled", True),
            last_alert_hash=doc.get("last_alert_hash"),
            updated_at=doc.get("updated_at", datetime.now(timezone.utc))
        )


    # Price cache - MongoDB
    def set_price(self, ticker: str, price: float, asof: datetime, currency: str = 'USD', exchange: str = 'Unknown', timezone: str = 'America/New_York', market_state: str | None = None, open_price: float | None = None):
        self.prices_collection.update_one(
            {"ticker": ticker},
            {"$set": {"price": price, "asof": asof, "currency": currency, "exchange": exchange, "timezone": timezone, "market_state": market_state, "open_price": open_price}},
            upsert=True
        )


    def get_price(self, ticker: str) -> Optional[PriceCache]:
        doc = self.prices_collection.find_one({"ticker": ticker})
        if not doc:
            return None
        return PriceCache(
            ticker=doc.get("ticker"),
            price=doc.get("price"),
            asof=doc.get("asof"),
            currency=doc.get("currency", "USD"),
            exchange=doc.get("exchange", "Unknown"),
            timezone=doc.get("timezone", "America/New_York"),
            market_state=doc.get("market_state"),
            open_price=doc.get("open_price")
        )