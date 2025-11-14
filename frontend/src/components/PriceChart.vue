<template>
  <div class="relative" style="height: 400px;">
    <div v-if="loading" class="text-center py-12">
      <div class="text-gray-400">Loading chart...</div>
    </div>
    <div v-else-if="error" class="text-red-400">{{ error }}</div>
    <Line v-else :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { Line } from 'vue-chartjs'
import type { TooltipItem } from 'chart.js'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import { getStockHistory } from '../api'
import type { HistoricalPrice } from '../types'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

const props = defineProps<{
  ticker: string
  period?: string
  interval?: string
}>()

const loading = ref(true)
const error = ref('')
const historyData = ref<HistoricalPrice[]>([])

const chartData = computed(() => ({
  labels: historyData.value.map(item => new Date(item.date).toLocaleDateString()),
  datasets: [
    {
      label: 'Close Price',
      data: historyData.value.map(item => item.close),
      borderColor: 'rgb(59, 130, 246)',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      fill: true,
      tension: 0.1
    }
  ]
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      mode: 'index' as const,
      intersect: false,
      backgroundColor: 'rgba(17, 24, 39, 0.9)',
      titleColor: '#f3f4f6',
      bodyColor: '#d1d5db',
      borderColor: '#374151',
      borderWidth: 1,
      callbacks: {
        label: (context: TooltipItem<'line'>) => {
          const value = context.parsed.y
          return value !== null ? `$${value.toFixed(2)}` : ''
        }
      }
    }
  },
  scales: {
    x: {
      grid: {
        color: 'rgba(75, 85, 99, 0.3)'
      },
      ticks: {
        color: '#9ca3af'
      }
    },
    y: {
      beginAtZero: false,
      grid: {
        color: 'rgba(75, 85, 99, 0.3)'
      },
      ticks: {
        color: '#9ca3af',
        callback: (value: number | string) => `$${value}`
      }
    }
  }
}

const loadHistory = async () => {
  loading.value = true
  error.value = ''
  try {
    historyData.value = await getStockHistory(
      props.ticker, 
      props.period || '1y', 
      props.interval || '1d'
    )
  } catch (err: unknown) {
    error.value = err instanceof Error && 'response' in err
      ? (err as any).response?.data?.detail || 'Failed to load chart data'
      : 'Failed to load chart data'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadHistory()
})
</script>
