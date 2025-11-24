from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from logging import getLogger
from .config import settings
from .repository import Repo
from .models import Watch
from .schemas import StatusRead, WatchCreate, InfoRead, StockDetailsRead, HistoricalPriceRead
from .data_provider import PriceProvider
from .telegram_notifier import Telegram
from .watcher import Watcher
from .ws import WSManager
from .stock_service import StockService
from .utils import get_aggregated_market_status

logger = getLogger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    scheduler.start()
    yield
    # Shutdown
    scheduler.shutdown()


app = FastAPI(title="Stocks Watcher", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5273","http://localhost:5183"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

repo = Repo(settings.MONGODB_URL, settings.MONGODB_DB_NAME)
provider = PriceProvider(settings.TICKER_MAP)
notifier = Telegram(settings.TELEGRAM_BOT_TOKEN, settings.TELEGRAM_CHAT_ID)
ws_manager = WSManager()
stock_service = StockService(repo, provider)
watcher = Watcher(repo, provider, notifier, ws_manager, stock_service)

scheduler = AsyncIOScheduler()
scheduler.add_job(watcher.tick_async, trigger=IntervalTrigger(minutes=settings.CHECK_INTERVAL_MINUTES))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            # opzionale: ricezione messaggi dal client
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

@app.get("/watches")
def list_watches():
    return repo.list_watches()


@app.post("/watches")
def upsert_watch(payload: WatchCreate):
    # Validate ticker exists on Yahoo Finance
    if not provider.validate_ticker(payload.ticker):
        raise HTTPException(status_code=400, detail=f"Ticker '{payload.ticker}' not found on Yahoo Finance")
    
    return repo.upsert_watch(Watch(ticker=payload.ticker, levels=payload.levels, enabled=payload.enabled))


@app.delete("/watches/{ticker}")
def delete_watch(ticker: str):
    """Delete a watch by ticker"""
    result = repo.delete_watch(ticker)
    if not result:
        raise HTTPException(status_code=404, detail=f"Watch '{ticker}' not found")
    return {"message": f"Watch '{ticker}' deleted successfully"}


@app.get("/status", response_model=list[StatusRead])
def status(forceRefresh: bool = False):
    out = []
    fetched_any = False
    
    for w in repo.list_watches():
        try:
            pc, was_fetched = stock_service.get_price(w.ticker, force_update=forceRefresh)
            if not pc:
                continue
            
            if was_fetched:
                fetched_any = True
            
            # Use StockService to create status with all calculations
            status_read = StockService.create_status_read(w.ticker, pc, w.levels)
            out.append(status_read)
        except Exception as e:
            logger.error(str(e))
            continue
    
    # Update last_update if we fetched any new prices
    if fetched_any:
        watcher.last_update = datetime.now(timezone.utc)
    
    return out


@app.get("/info", response_model=InfoRead)
def info():
    last_update = watcher.last_update
    next_update = datetime.now(timezone.utc) + timedelta(minutes=settings.CHECK_INTERVAL_MINUTES)
    if last_update:
        next_update = last_update + timedelta(minutes=settings.CHECK_INTERVAL_MINUTES)
    
    # Get timezone, exchange, and market state data from watched tickers
    ticker_data = []
    for w in repo.list_watches():
        pc = repo.get_price(w.ticker)
        if pc and pc.timezone:
            print(f"[INFO] Ticker {w.ticker}: exchange={pc.exchange}, timezone={pc.timezone}, market_state={pc.market_state}")
            ticker_data.append((pc.timezone, pc.exchange, pc.market_state))
    
    # Get aggregated market status using real-time data from Yahoo Finance
    market_info = get_aggregated_market_status(ticker_data)
    print(f"[INFO] Market info: {market_info}")
    
    return InfoRead(
        last_update=last_update,
        next_update=next_update,
        check_interval_minutes=settings.CHECK_INTERVAL_MINUTES,
        market_status=market_info['overall'],
        markets=market_info['markets']
    )


@app.get("/stocks/{ticker}/details", response_model=StockDetailsRead)
def get_stock_details(ticker: str):
    """Get comprehensive financial details for a stock"""
    try:
        details = provider.get_stock_details(ticker)
        return StockDetailsRead(**details)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/stocks/{ticker}/history", response_model=list[HistoricalPriceRead])
def get_stock_history(ticker: str, period: str = "1y", interval: str = "1d"):
    """
    Get historical price data for charting
    period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
    interval: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
    """
    try:
        history = provider.get_historical_prices(ticker, period, interval)
        return [HistoricalPriceRead(**item) for item in history]
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))