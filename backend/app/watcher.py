from datetime import datetime, timezone
from .repository import Repo
from .data_provider import PriceProvider
from .telegram_notifier import Telegram
from .config import settings
from .utils import pct_diff, format_alert
from .stock_service import StockService
from logging import getLogger
logger = getLogger("watcher")

class Watcher:
    def __init__(self, repo: Repo, provider: PriceProvider, notifier: Telegram, ws_manager=None, stock_service=None):
        self.repo = repo
        self.provider = provider
        self.notifier = notifier
        self.ws_manager = ws_manager
        self.stock_service = stock_service or StockService(repo, provider)
        self.last_update = None


    async def tick_async(self):
        # versione async per poter fare broadcast WS
        # if it's saturday or sunday, skip
        
        if datetime.now(timezone.utc).weekday() >= 5:
            logger.info("Skipping tick on weekend")
            return

        watches = [w for w in self.repo.list_watches() if w.enabled]
        logger.info("Tick: %d watches", len(watches))

        status_push = []
        for w in watches:
            try:
                # Use stock_service to update price (force fresh data)
                pc, _ = self.stock_service.get_price(w.ticker, force_update=True)
                if not pc:
                    continue
                
                # Use StockService to create status dictionary
                status_dict = StockService.create_status_dict(
                    ticker=w.ticker,
                    price=pc.price,
                    currency=pc.currency,
                    open_price=pc.open_price,
                    levels=w.levels
                )
                status_push.append(status_dict)
                
                # Check if near level for alerts
                if status_dict["nearest_level"] is not None and status_dict["near"]:
                    text = format_alert(
                        w.ticker,
                        pc.price,
                        status_dict["nearest_level"],
                        status_dict["distance_pct"]
                    )
                    current_hash = self.notifier._hash(text)
                    if current_hash != w.last_alert_hash:
                        self.notifier.send(text)
                        self.repo.update_last_alert(w.ticker, current_hash)
                else:
                    if w.last_alert_hash:
                        self.repo.update_last_alert(w.ticker, None)
                        
            except Exception as e:
                logger.error(f"Error processing ticker {w.ticker}: {e}")
        
        self.last_update = datetime.utcnow()
                        
        if self.ws_manager and status_push:
            await self.ws_manager.broadcast({"type": "status", "data": status_push})
            logger.info("Broadcasted %d statuses via WS", len(status_push))