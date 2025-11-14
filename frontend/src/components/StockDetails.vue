<template>
  <div class="min-h-screen bg-gray-900 py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-6 bg-gray-800 border-gray-700 border-b p-5">
        <button 
          @click="$router.push('/')" 
          class="text-blue-600 hover:text-blue-800 mb-4 flex items-center"
        >
          ← Back to Watchlist
        </button>
        <div class="flex items-center justify-between">
          <div>
            <div class="flex items-center gap-3">
              <h1 class="text-3xl font-bold text-gray-50">{{ details?.name || ticker }}</h1>
              <span 
                v-if="details?.recommendation_key" 
                :class="getRecommendationBadgeClass(details.recommendation_key)"
                class="px-3 py-1 rounded-full text-sm font-semibold"
              >
                {{ formatKeyToLabel(details.recommendation_key) }}
              </span>
            </div>
            <p class="text-gray-50">{{ ticker }}</p>
          </div>
          <div v-if="details" class="text-right">
            <div class="text-3xl font-bold text-gray-50">
              {{ formatCurrency(details.current_price, details.currency) }}
            </div>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <div class="text-gray-400">Loading stock details...</div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-red-900/30 border border-red-700 rounded-lg p-4">
        <p class="text-red-400">{{ error }}</p>
      </div>

      <!-- Content -->
      <div v-else-if="details" class="space-y-6">
        <!-- Price Chart -->
        <div class="bg-gray-800 rounded-lg shadow-xl p-6 border border-gray-700">
          <h2 class="text-xl font-semibold mb-4 text-gray-100">Price History</h2>
          <PriceChart :ticker="ticker" />
        </div>

        <!-- Market Data -->
        <div class="bg-gray-800 rounded-lg shadow-xl p-6 border border-gray-700">
          <h2 class="text-xl font-semibold mb-4 text-gray-100">Market Data</h2>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <DataItem label="Market Cap" :value="formatLargeNumber(details.market_cap)" />
            <DataItem label="Volume" :value="formatNumber(details.volume)" />
            <DataItem label="Avg Volume" :value="formatNumber(details.avg_volume)" />
            <DataItem label="Beta" :value="formatDecimal(details.beta, 2)" />
            <DataItem label="52W High" :value="formatCurrency(details.fifty_two_week_high, details.currency)" />
            <DataItem label="52W Low" :value="formatCurrency(details.fifty_two_week_low, details.currency)" />
            <DataItem label="52W Change" :value="formatPercent(details.fifty_two_week_change)" />
          </div>
        </div>

        <!-- Valuation -->
        <div class="bg-gray-800 rounded-lg shadow-xl p-6 border border-gray-700">
          <h2 class="text-xl font-semibold mb-4 text-gray-100">Valuation Metrics</h2>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <DataItem label="P/E Ratio" :value="formatDecimal(details.pe_ratio, 2)" />
            <DataItem label="Forward P/E" :value="formatDecimal(details.forward_pe, 2)" />
            <DataItem label="PEG Ratio" :value="formatDecimal(details.peg_ratio, 2)" />
            <DataItem label="Price/Book" :value="formatDecimal(details.price_to_book, 2)" />
            <DataItem label="Price/Sales" :value="formatDecimal(details.price_to_sales, 2)" />
            <DataItem label="Enterprise Value" :value="formatLargeNumber(details.enterprise_value)" />
          </div>
        </div>

        <!-- Profitability -->
        <div class="bg-gray-800 rounded-lg shadow-xl p-6 border border-gray-700">
          <h2 class="text-xl font-semibold mb-4 text-gray-100">Profitability</h2>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <DataItem label="Profit Margin" :value="formatPercent(details.profit_margin)" />
            <DataItem label="Operating Margin" :value="formatPercent(details.operating_margin)" />
            <DataItem label="ROE" :value="formatPercent(details.roe)" />
            <DataItem label="ROA" :value="formatPercent(details.roa)" />
          </div>
        </div>

        <!-- Growth -->
        <div class="bg-gray-800 rounded-lg shadow-xl p-6 border border-gray-700">
          <h2 class="text-xl font-semibold mb-4 text-gray-100">Growth</h2>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <DataItem label="Revenue Growth" :value="formatPercent(details.revenue_growth)" />
            <DataItem label="Earnings Growth" :value="formatPercent(details.earnings_growth)" />
          </div>
        </div>

        <!-- Dividends -->
        <div class="bg-gray-800 rounded-lg shadow-xl p-6 border border-gray-700">
          <h2 class="text-xl font-semibold mb-4 text-gray-100">Dividends</h2>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <DataItem label="Dividend Yield" :value="formatPercent(details.dividend_yield)" />
            <DataItem label="Payout Ratio" :value="formatPercent(details.payout_ratio)" />
            <DataItem label="Ex-Dividend Date" :value="details.ex_dividend_date" />
          </div>
        </div>

        <!-- Financial Health -->
        <div class="bg-gray-800 rounded-lg shadow-xl p-6 border border-gray-700">
          <h2 class="text-xl font-semibold mb-4 text-gray-100">Financial Health</h2>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <DataItem label="Debt/Equity" :value="formatDecimal(details.debt_to_equity, 2)" />
            <DataItem label="Current Ratio" :value="formatDecimal(details.current_ratio, 2)" />
            <DataItem label="Quick Ratio" :value="formatDecimal(details.quick_ratio, 2)" />
            <DataItem label="Free Cash Flow" :value="formatLargeNumber(details.free_cashflow)" />
          </div>
        </div>

        <!-- Analyst Ratings -->
        <div class="bg-gray-800 rounded-lg shadow-xl p-6 border border-gray-700">
          <h2 class="text-xl font-semibold mb-4 text-gray-100">Analyst Ratings</h2>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <DataItem label="Target Mean" :value="formatCurrency(details.target_mean_price, details.currency)" />
            <DataItem label="Target High" :value="formatCurrency(details.target_high_price, details.currency)" />
            <DataItem label="Target Low" :value="formatCurrency(details.target_low_price, details.currency)" />
            <DataItem label="Recommendation" :value="formatKeyToLabel(details.recommendation_key)" />
            <DataItem label="Analyst Opinions" :value="formatNumber(details.number_of_analyst_opinions)" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getStockDetails } from '../api'
import type { StockDetails } from '../types'
import { useFormatters } from '../composables/useFormatters'
import PriceChart from './PriceChart.vue'
import DataItem from './DataItem.vue'

const route = useRoute()
const ticker = ref(route.params.ticker as string)
const details = ref<StockDetails | null>(null)
const loading = ref(true)
const error = ref('')

const {
  formatKeyToLabel,
  formatCurrency,
  formatNumber,
  formatLargeNumber,
  formatPercent,
  formatDecimal
} = useFormatters()

const loadDetails = async () => {
  loading.value = true
  error.value = ''
  try {
    details.value = await getStockDetails(ticker.value)
    console.log(details.value)
  } catch (err: unknown) {
    error.value = err instanceof Error && 'response' in err
      ? (err as any).response?.data?.detail || 'Failed to load stock details'
      : 'Failed to load stock details'
  } finally {
    loading.value = false
  }
}

const getRecommendationBadgeClass = (key: string) => {
  const classes: Record<string, string> = {
    'strong_buy': 'bg-green-600 text-white',
    'buy': 'bg-green-500 text-white',
    'hold': 'bg-yellow-500 text-white',
    'sell': 'bg-orange-500 text-white',
    'strong_sell': 'bg-red-600 text-white'
  }
  return classes[key] || 'bg-gray-500 text-white'
}

onMounted(() => {
  loadDetails()
})
</script>
