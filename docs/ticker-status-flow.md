# Ticker Status Flow - Frontend to Server

```mermaid
flowchart TD
    Start([User Opens App]) --> Mount[WatchTable Component Mounted]
    
    Mount --> LoadWatches[GET /watches<br/>Fetch all watch configurations]
    Mount --> LoadStatus[GET /status<br/>Fetch current prices from cache]
    Mount --> LoadInfo[GET /info<br/>Fetch last/next update times]
    Mount --> ConnectWS[Connect WebSocket<br/>ws://server/ws]
    
    LoadWatches --> DisplayTable[Display Watch Table<br/>with tickers and levels]
    LoadStatus --> UpdatePrices[Update statusMap<br/>with cached prices]
    LoadInfo --> DisplayInfo[Display Last/Next Update times]
    
    UpdatePrices --> DisplayTable
    DisplayInfo --> DisplayTable
    
    ConnectWS --> WSReady[WebSocket Connected]
    
    %% Scheduler Flow
    Scheduler[APScheduler<br/>Every N minutes] --> TickStart[watcher.tick_async()]
    
    TickStart --> FetchYahoo[For each enabled watch:<br/>GET Yahoo Finance API<br/>fetch price + currency]
    
    FetchYahoo --> SaveMongo[Save to MongoDB:<br/>prices collection<br/>ticker, price, asof, currency]
    
    SaveMongo --> CalcStatus[Calculate Status:<br/>nearest_level<br/>distance_pct<br/>near flag]
    
    CalcStatus --> CheckAlert{Price near<br/>target level?}
    
    CheckAlert -->|Yes| SendTelegram[Send Telegram Alert<br/>if configured and not duplicate]
    CheckAlert -->|No| ClearAlert[Clear alert hash<br/>if exists]
    
    SendTelegram --> BroadcastWS
    ClearAlert --> BroadcastWS
    
    BroadcastWS[Broadcast via WebSocket:<br/>type: 'status'<br/>data: array of statuses] --> UpdateLastUpdate[Update watcher.last_update<br/>timestamp]
    
    %% WebSocket Reception
    WSReady --> WSMessage{WebSocket<br/>Message Received}
    
    UpdateLastUpdate -.->|Broadcast| WSMessage
    
    WSMessage -->|type: 'status'| UpdateUI[Update Frontend:<br/>statusMap with new prices<br/>Refresh info times]
    
    UpdateUI --> DisplayTable
    
    %% User Add Watch Flow
    UserAdd([User Adds Watch]) --> ValidateTicker[POST /watches<br/>Validate ticker on Yahoo Finance]
    
    ValidateTicker -->|Valid| SaveWatch[Save to MongoDB:<br/>watches collection<br/>ticker, levels, enabled]
    ValidateTicker -->|Invalid| ShowError[Display Error:<br/>Ticker not found]
    
    SaveWatch --> ReloadData[Reload:<br/>GET /watches<br/>GET /status<br/>GET /info]
    
    ReloadData --> DisplayTable
    
    %% Legend
    classDef frontend fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef backend fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef database fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef external fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    
    class Mount,DisplayTable,UpdateUI,UpdatePrices,DisplayInfo,UserAdd,ShowError,ReloadData frontend
    class LoadWatches,LoadStatus,LoadInfo,ConnectWS,WSReady,ValidateTicker,SaveWatch,TickStart,CalcStatus,CheckAlert,SendTelegram,ClearAlert,BroadcastWS,UpdateLastUpdate backend
    class SaveMongo,FetchYahoo database
    class Scheduler external
```

## Flow Description

### Initial Load (Component Mount)
1. **Frontend** makes three parallel REST calls:
   - `GET /watches` - Fetches ticker configurations from MongoDB
   - `GET /status` - Fetches cached prices from MongoDB
   - `GET /info` - Fetches last/next update timestamps
2. **WebSocket** connection established for real-time updates
3. **Display** renders table with available data

### Scheduled Updates (Backend)
1. **APScheduler** triggers `watcher.tick_async()` every N minutes
2. **For each enabled watch**:
   - Fetch current price and currency from Yahoo Finance API
   - Save to MongoDB prices collection
   - Calculate nearest level and distance percentage
   - Check if price is near target level
3. **If near**: Send Telegram alert (if configured and not duplicate)
4. **Broadcast** status updates via WebSocket to all connected clients
5. **Update** last_update timestamp

> **Note**: Telegram notifications are optional and require `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` to be configured in environment variables. The system works without Telegram credentials.

### Real-time Updates (WebSocket)
1. **WebSocket** receives broadcast message
2. **Frontend** updates `statusMap` with new price data
3. **Refresh** info panel with updated times
4. **Table** re-renders with new prices

### Add Watch Flow (User Action)
1. **User** submits ticker via AddWatch component
2. **Backend** validates ticker exists on Yahoo Finance
3. **If valid**: Save to MongoDB watches collection
4. **Frontend** reloads all data (watches, status, info)
5. **If invalid**: Display error message

## Data Storage

### MongoDB Collections
- **watches**: ticker, levels, enabled, last_alert_hash, updated_at
- **prices**: ticker, price, asof, currency

## Real-time Communication
- **WebSocket**: Bidirectional connection for instant price updates
- **REST API**: Initial data load and user actions
