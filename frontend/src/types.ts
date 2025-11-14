// API Types matching backend schemas

export interface Watch {
  ticker: string
  levels: number[]
  enabled: boolean
  last_alert_hash: string | null
  updated_at: string
}

export interface WatchCreate {
  ticker: string
  levels: number[]
  enabled: boolean
}

export interface StatusRead {
  ticker: string
  price: number
  currency: string
  nearest_level: number | null
  distance_pct: number
  near: boolean
  open_price: number | null
  price_change_pct: number | null
}

export interface InfoRead {
  last_update: string | null
  next_update: string | null
  check_interval_minutes: number
  market_status: 'open' | 'closed' | 'pre-market' | 'after-hours'
  markets: Record<string, string>  // Exchange name -> status
}

export interface StockDetails {
  ticker: string
  name: string | null
  currency: string
  current_price: number | null
  
  // Market data
  market_cap: number | null
  volume: number | null
  avg_volume: number | null
  fifty_two_week_high: number | null
  fifty_two_week_low: number | null
  fifty_two_week_change: number | null
  beta: number | null
  
  // Valuation
  pe_ratio: number | null
  forward_pe: number | null
  peg_ratio: number | null
  price_to_book: number | null
  price_to_sales: number | null
  enterprise_value: number | null
  
  // Profitability
  profit_margin: number | null
  operating_margin: number | null
  roe: number | null
  roa: number | null
  
  // Growth
  revenue_growth: number | null
  earnings_growth: number | null
  
  // Dividends
  dividend_yield: number | null
  payout_ratio: number | null
  ex_dividend_date: string | null
  
  // Financial health
  debt_to_equity: number | null
  current_ratio: number | null
  quick_ratio: number | null
  free_cashflow: number | null
  
  // Analyst info
  target_mean_price: number | null
  target_high_price: number | null
  target_low_price: number | null
  recommendation_mean: number | null
  recommendation_key: string | null
  number_of_analyst_opinions: number | null
}

export interface HistoricalPrice {
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export interface WebSocketMessage {
  type: 'status'
  data: StatusRead[]
}
