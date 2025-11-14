from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Dict, List, Tuple


def normalize_market_state(yahoo_state: str | None) -> str:
    """
    Convert Yahoo Finance marketState to our standard format.
    Yahoo states: REGULAR, PRE, POST, CLOSED, PREPRE, POSTPOST
    Our states: open, pre-market, after-hours, closed
    """
    if not yahoo_state:
        return 'unknown'
    
    state_upper = yahoo_state.upper()
    
    if state_upper == 'REGULAR':
        return 'open'
    elif state_upper in ('PRE', 'PREPRE'):
        return 'pre-market'
    elif state_upper in ('POST', 'POSTPOST'):
        return 'after-hours'
    elif state_upper == 'CLOSED':
        return 'closed'
    else:
        return 'unknown'


def pct_diff(a: float, b: float) -> float:
    return abs(a - b) / b if b != 0 else 0.0


def format_alert(ticker: str, price: float, level: float, distance_pct: float) -> str:
    sign = "↑" if price >= level else "↓"
    return (
        f"<b>{ticker}</b> near level {level:.2f} {sign}"
        f"Price: {price:.2f} | Distance: {distance_pct*100:.2f}%"
    )


# Exchange to timezone and trading hours mapping
EXCHANGE_INFO = {
    # US Markets
    'NMS': {  # NASDAQ
        'timezone': 'America/New_York',
        'name': 'NASDAQ',
        'hours': {
            'pre_market': ('04:00', '09:30'),
            'regular': ('09:30', '16:00'),
            'after_hours': ('16:00', '20:00')
        }
    },
    'NYQ': {  # NYSE
        'timezone': 'America/New_York',
        'name': 'NYSE',
        'hours': {
            'pre_market': ('04:00', '09:30'),
            'regular': ('09:30', '16:00'),
            'after_hours': ('16:00', '20:00')
        }
    },
    # European Markets
    'MIL': {  # Borsa Italiana (Milano)
        'timezone': 'Europe/Rome',
        'name': 'Borsa Italiana',
        'hours': {
            'pre_market': ('08:00', '09:00'),
            'regular': ('09:00', '17:30'),
            'after_hours': ('17:30', '17:35')
        }
    },
    'LSE': {  # London Stock Exchange
        'timezone': 'Europe/London',
        'name': 'London Stock Exchange',
        'hours': {
            'pre_market': ('05:05', '08:00'),
            'regular': ('08:00', '16:30'),
            'after_hours': ('16:30', '16:35')
        }
    },
    'PAR': {  # Euronext Paris
        'timezone': 'Europe/Paris',
        'name': 'Euronext Paris',
        'hours': {
            'pre_market': ('07:15', '09:00'),
            'regular': ('09:00', '17:30'),
            'after_hours': ('17:30', '17:35')
        }
    },
    'FRA': {  # Frankfurt Stock Exchange
        'timezone': 'Europe/Berlin',
        'name': 'Frankfurt Stock Exchange',
        'hours': {
            'pre_market': ('08:00', '09:00'),
            'regular': ('09:00', '17:30'),
            'after_hours': ('17:30', '20:00')
        }
    },
    # Asian Markets
    'HKG': {  # Hong Kong Stock Exchange
        'timezone': 'Asia/Hong_Kong',
        'name': 'Hong Kong Stock Exchange',
        'hours': {
            'pre_market': ('09:00', '09:30'),
            'regular': ('09:30', '16:00'),
            'after_hours': None
        }
    },
    'JPX': {  # Tokyo Stock Exchange
        'timezone': 'Asia/Tokyo',
        'name': 'Tokyo Stock Exchange',
        'hours': {
            'pre_market': None,
            'regular': ('09:00', '15:00'),  # With lunch break 11:30-12:30
            'after_hours': None
        }
    },
}


def get_market_status_for_exchange(exchange: str) -> str:
    """
    Determine market status for a specific exchange.
    Returns: 'open', 'closed', 'pre-market', or 'after-hours'
    
    Note: Does not account for market holidays
    """
    # Default to US market if exchange not recognized
    exchange_data = EXCHANGE_INFO.get(exchange, EXCHANGE_INFO.get('NMS'))
    
    if not exchange_data:
        return 'unknown'
    
    # Get current time in the exchange's timezone
    tz = ZoneInfo(exchange_data['timezone'])
    now_local = datetime.now(tz)
    
    # Check if weekend
    if now_local.weekday() >= 5:  # Saturday=5, Sunday=6
        return 'closed'
    
    current_time = now_local.time()
    hours = exchange_data['hours']
    
    # Parse time strings
    def parse_time(time_str):
        return datetime.strptime(time_str, "%H:%M").time()
    
    # Check regular hours
    regular_start, regular_end = hours['regular']
    if parse_time(regular_start) <= current_time < parse_time(regular_end):
        return 'open'
    
    # Check pre-market
    if hours.get('pre_market'):
        pre_start, pre_end = hours['pre_market']
        if parse_time(pre_start) <= current_time < parse_time(pre_end):
            return 'pre-market'
    
    # Check after-hours
    if hours.get('after_hours'):
        after_start, after_end = hours['after_hours']
        if parse_time(after_start) <= current_time < parse_time(after_end):
            return 'after-hours'
    
    return 'closed'


def get_market_status_for_timezone(timezone_name: str, exchange: str = 'Unknown', market_state: str | None = None) -> Tuple[str, str]:
    """
    Determine market status using data from Yahoo Finance.
    Prioritizes marketState from Yahoo if available, falls back to timezone calculation.
    
    Args:
        timezone_name: Timezone from Yahoo (e.g., 'America/New_York')
        exchange: Exchange code (e.g., 'NMS', 'MIL')
        market_state: Yahoo's marketState if available (REGULAR, PRE, POST, CLOSED)
    
    Returns: (status, exchange_name)
    """
    # If Yahoo provides marketState, use it (most accurate)
    if market_state:
        status = normalize_market_state(market_state)
        exchange_name = EXCHANGE_INFO.get(exchange, {}).get('name', exchange)
        return status, exchange_name
    try:
        tz = ZoneInfo(timezone_name)
    except:
        # Fallback to US Eastern if timezone not recognized
        tz = ZoneInfo('America/New_York')
    
    now_local = datetime.now(tz)
    
    # Check if weekend
    if now_local.weekday() >= 5:  # Saturday=5, Sunday=6
        return 'closed', EXCHANGE_INFO.get(exchange, {}).get('name', exchange)
    
    current_time = now_local.time()
    
    # Try to get exchange info from our mapping
    exchange_data = EXCHANGE_INFO.get(exchange)
    
    if exchange_data and exchange_data['timezone'] == timezone_name:
        # We have specific hours for this exchange
        hours = exchange_data['hours']
        exchange_name = exchange_data['name']
        
        def parse_time(time_str):
            return datetime.strptime(time_str, "%H:%M").time()
        
        # Check regular hours
        regular_start, regular_end = hours['regular']
        if parse_time(regular_start) <= current_time < parse_time(regular_end):
            return 'open', exchange_name
        
        # Check pre-market
        if hours.get('pre_market'):
            pre_start, pre_end = hours['pre_market']
            if parse_time(pre_start) <= current_time < parse_time(pre_end):
                return 'pre-market', exchange_name
        
        # Check after-hours
        if hours.get('after_hours'):
            after_start, after_end = hours['after_hours']
            if parse_time(after_start) <= current_time < parse_time(after_end):
                return 'after-hours', exchange_name
        
        return 'closed', exchange_name
    else:
        # Generic market hours based on timezone (US, Europe, Asia patterns)
        # US markets (Eastern Time)
        if 'America/New_York' in timezone_name:
            if datetime.strptime('09:30', '%H:%M').time() <= current_time < datetime.strptime('16:00', '%H:%M').time():
                return 'open', exchange
            elif datetime.strptime('04:00', '%H:%M').time() <= current_time < datetime.strptime('09:30', '%H:%M').time():
                return 'pre-market', exchange
            elif datetime.strptime('16:00', '%H:%M').time() <= current_time < datetime.strptime('20:00', '%H:%M').time():
                return 'after-hours', exchange
        # European markets
        elif any(eu_tz in timezone_name for eu_tz in ['Europe/London', 'Europe/Paris', 'Europe/Rome', 'Europe/Berlin']):
            if datetime.strptime('09:00', '%H:%M').time() <= current_time < datetime.strptime('17:30', '%H:%M').time():
                return 'open', exchange
            elif datetime.strptime('08:00', '%H:%M').time() <= current_time < datetime.strptime('09:00', '%H:%M').time():
                return 'pre-market', exchange
        # Asian markets
        elif any(asia_tz in timezone_name for asia_tz in ['Asia/Tokyo', 'Asia/Hong_Kong', 'Asia/Shanghai']):
            if datetime.strptime('09:00', '%H:%M').time() <= current_time < datetime.strptime('15:30', '%H:%M').time():
                return 'open', exchange
        
        return 'closed', exchange


def get_market_status() -> str:
    """
    Deprecated: Use get_market_status_for_exchange instead.
    Determine if US stock market (NYSE/NASDAQ) is currently open.
    Returns: 'open', 'closed', 'pre-market', or 'after-hours'
    """
    return get_market_status_for_exchange('NMS')


def get_aggregated_market_status(ticker_data: List[Tuple[str, str, str | None]]) -> Dict[str, any]:
    """
    Get market status for multiple tickers with their timezone, exchange, and market state.
    Args:
        ticker_data: List of (timezone, exchange, market_state) tuples
    Returns:
        Dict with overall status and per-exchange breakdown
    """
    if not ticker_data:
        # Default to closed
        return {
            'overall': 'closed',
            'markets': {}
        }
    
    market_statuses = {}
    
    # Process each ticker's data
    for timezone_name, exchange, market_state in ticker_data:
        status, exchange_name = get_market_status_for_timezone(timezone_name, exchange, market_state)
        
        # Use exchange_name as key (human readable), update if we find a more active status
        if exchange_name not in market_statuses:
            market_statuses[exchange_name] = status
        elif market_statuses[exchange_name] == 'closed' and status != 'closed':
            # Update if current is closed but we found an active market
            market_statuses[exchange_name] = status
        elif market_statuses[exchange_name] == 'after-hours' and status in ('open', 'pre-market'):
            # Update after-hours if we find open or pre-market
            market_statuses[exchange_name] = status
        elif market_statuses[exchange_name] == 'pre-market' and status == 'open':
            # Update pre-market if we find open
            market_statuses[exchange_name] = status
    
    # Determine overall status
    # Priority: open > pre-market > after-hours > closed
    statuses = list(market_statuses.values())
    if 'open' in statuses:
        overall = 'open'
    elif 'pre-market' in statuses:
        overall = 'pre-market'
    elif 'after-hours' in statuses:
        overall = 'after-hours'
    else:
        overall = 'closed'
    
    return {
        'overall': overall,
        'markets': market_statuses
    }