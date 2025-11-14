import axios from 'axios'
import type { Watch, WatchCreate, StatusRead, InfoRead, StockDetails, HistoricalPrice } from './types'

const api = axios.create({ baseURL: import.meta.env.VITE_API_BASE || 'http://localhost:8000' })

export const listWatches = (): Promise<Watch[]> => 
  api.get<Watch[]>('/watches').then(r => r.data)

export const saveWatch = (payload: WatchCreate): Promise<Watch> => 
  api.post<Watch>('/watches', payload).then(r => r.data)

export const deleteWatch = (ticker: string): Promise<{ message: string }> => 
  api.delete<{ message: string }>(`/watches/${ticker}`).then(r => r.data)

export const getStatus = (): Promise<StatusRead[]> => 
  api.get<StatusRead[]>('/status').then(r => r.data)

export const getInfo = (): Promise<InfoRead> => 
  api.get<InfoRead>('/info').then(r => r.data)

export const getStockDetails = (ticker: string): Promise<StockDetails> => 
  api.get<StockDetails>(`/stocks/${ticker}/details`).then(r => r.data)

export const getStockHistory = (ticker: string, period: string = '1y', interval: string = '1d'): Promise<HistoricalPrice[]> => 
  api.get<HistoricalPrice[]>(`/stocks/${ticker}/history`, { params: { period, interval } }).then(r => r.data)