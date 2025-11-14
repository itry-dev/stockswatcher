<template>
    <section class="space-y-6">
        <AddWatch ref="addWatchRef" @add="handleAdd" />
        <EditWatch 
            :is-open="editDialogOpen" 
            :watch="watchToEdit" 
            @save="handleEditSave" 
            @cancel="handleEditCancel" 
            ref="editWatchRef"
        />

        <div v-if="info" class="bg-blue-900/30 border border-blue-700 rounded p-3 text-sm">
            <div class="flex gap-6 items-center justify-between">
                <div class="flex gap-6 flex-wrap">
                    <div>
                        <span class="font-medium text-gray-300">Last Update:</span>
                        <span class="ml-2 text-gray-100">{{ formatDateTime(info.last_update) }}</span>
                    </div>
                    <div>
                        <span class="font-medium text-gray-300">Next Update:</span>
                        <span class="ml-2 text-gray-100">{{ formatDateTime(info.next_update) }}</span>
                    </div>
                    <div>
                        <span class="font-medium text-gray-300">Markets:</span>
                        <span v-if="Object.keys(info.markets).length === 0" class="ml-2 px-2 py-1 rounded text-xs font-semibold" :class="getMarketStatusClass(info.market_status)">
                            {{ formatMarketStatus(info.market_status) }}
                        </span>
                        <span v-else class="ml-2 inline-flex gap-2 flex-wrap">
                            <span v-for="(status, market) in info.markets" :key="market" 
                                  class="px-2 py-1 rounded text-xs font-semibold" 
                                  :class="getMarketStatusClass(status)"
                                  :title="`${market}: ${formatMarketStatus(status)}`">
                                {{ market }}: {{ formatMarketStatus(status) }}
                            </span>
                        </span>
                    </div>
                </div>
                <button 
                    @click="handleRefreshNow"
                    :disabled="isRefreshing"
                    class="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded transition-colors whitespace-nowrap"
                >
                    {{ isRefreshing ? 'Refreshing...' : 'Refresh Now' }}
                </button>
            </div>
        </div>

        <table class="w-full bg-gray-800 shadow-xl rounded overflow-hidden">
            <thead class="bg-gray-700">
                <tr>
                    <th class="text-left p-2 text-gray-300">Ticker</th>
                    <th class="text-left p-2 text-gray-300">Levels</th>
                    <th class="text-left p-2 text-gray-300">Price</th>
                    <th class="text-left p-2 text-gray-300">Open %</th>
                    <th class="text-left p-2 text-gray-300">Nearest</th>
                    <th class="text-left p-2 text-gray-300">Distance %</th>
                    <th class="text-left p-2 text-gray-300">Near</th>
                    <th class="text-left p-2 text-gray-300">Actions</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="w in watches" :key="w.ticker" class="border-t border-gray-700 hover:bg-gray-700/50">
                    <td class="p-2">
                        <button 
                            @click="router.push(`/stock/${w.ticker}`)" 
                            class="text-blue-400 hover:text-blue-300 hover:underline font-medium"
                        >
                            {{ w.ticker }}
                        </button>
                    </td>
                    <td class="p-2">{{ w.levels.join(', ') }}</td>
                    <td class="p-2">
                        <div class="flex items-center gap-1">
                            <span>{{ statusMap[w.ticker]?.price?.toFixed(2) ?? '-' }} {{ statusMap[w.ticker]?.currency ?? '' }}</span>                            
                        </div>
                    </td>
                    <td class="p-2">
                        <span v-if="statusMap[w.ticker]?.price_change_pct !== null && statusMap[w.ticker]?.price_change_pct !== undefined" class="text-xs">
                        <span v-if="statusMap[w.ticker].price_change_pct! > 0" class="text-green-600">
                            ▲ {{ statusMap[w.ticker].price_change_pct!.toFixed(2) }}%
                        </span>
                        <span v-else-if="statusMap[w.ticker].price_change_pct! < 0" class="text-red-600">
                            ▼ {{ Math.abs(statusMap[w.ticker].price_change_pct!).toFixed(2) }}%
                        </span>
                    </span>
                    </td>
                    <td class="p-2">{{ statusMap[w.ticker]?.nearest_level?.toFixed(2) ?? '-' }}</td>
                    <td class="p-2">{{ ((statusMap[w.ticker]?.distance_pct ?? 0) * 100).toFixed(2) }}</td>
                    <td class="p-2">
                        <span v-if="statusMap[w.ticker]?.near" class="px-2 py-1 rounded text-white bg-green-600">Near</span>
                        <span v-else class="px-2 py-1 rounded bg-gray-700 text-gray-300">No</span>
                    </td>
                    <td class="p-2">
                        <div class="flex gap-2">
                            <button 
                                @click="handleEdit(w)"
                                class="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-sm transition-colors"
                            >
                                Edit
                            </button>
                            <button 
                                @click="handleDelete(w.ticker)"
                                class="px-3 py-1 bg-red-600 hover:bg-red-700 text-white rounded text-sm transition-colors"
                            >
                                Delete
                            </button>
                        </div>
                    </td>
                </tr>
            </tbody>
        </table>
    </section>
</template>


<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { listWatches, saveWatch, deleteWatch, getStatus, getInfo } from '../api'
import type { Watch, StatusRead, InfoRead, WatchCreate, WebSocketMessage } from '../types'
import AddWatch from './AddWatch.vue'
import EditWatch from './EditWatch.vue'
import { AxiosError } from 'axios'

const router = useRouter()
const watches = ref<Watch[]>([])
const statusMap = ref<Record<string, StatusRead>>({})
const addWatchRef = ref<InstanceType<typeof AddWatch> | null>(null)
const editWatchRef = ref<InstanceType<typeof EditWatch> | null>(null)
const info = ref<InfoRead | null>(null)
const isRefreshing = ref(false)
const editDialogOpen = ref(false)
const watchToEdit = ref<Watch | null>(null)
let ws: WebSocket | null = null


function connectWS() {
    const url = (import.meta.env.VITE_API_BASE || 'http://localhost:8000').replace(/^http/, 'ws') + '/ws'
    ws = new WebSocket(url)
    ws.onopen = () => console.log('WS connected')
    ws.onmessage = (ev) => {
        console.log('Time is', new Date().toLocaleTimeString())
        console.log('WS message', ev.data)
        try {
            const msg = JSON.parse(ev.data) as WebSocketMessage
            if (msg?.type === 'status') {
                for (const s of msg.data) {
                    statusMap.value[s.ticker] = s
                }
                // Update info after receiving status
                loadInfo()
            }
        } 
        catch {}
    }
    ws.onerror = (err) => {
        console.error('WS error', err)
    }
    ws.onclose = () => {
        console.log('WS disconnected, will retry in 1.5s')
        ws = null
        setTimeout(connectWS, 1500) // semplice auto-retry
    }
}

function handleVisibilityChange() {
    if (document.visibilityState === 'visible') {
        console.log('Page visible again, reconnecting WS if needed')
        if (!ws || ws.readyState !== WebSocket.OPEN) {
            ws?.close()
            connectWS()
        }
        // Also reload status when page becomes visible again
        loadStatus()
        loadInfo()
    }
}


async function load() {
    watches.value = await listWatches()
    await loadStatus()
    await loadInfo()
}

async function loadStatus() {
    try {
        const statuses = await getStatus()
        for (const s of statuses) {
            statusMap.value[s.ticker] = s
        }
    } catch (error) {
        console.error('Failed to load status:', error)
    }
}

async function loadInfo() {
    try {
        info.value = await getInfo()
    } catch (error) {
        console.error('Failed to load info:', error)
    }
}

function formatDateTime(dt: string | null) {
    if (!dt) return 'Not yet'
    const date = new Date(dt)
    return date.toLocaleString()
}

function formatMarketStatus(status: string): string {
    switch (status) {
        case 'open':
            return '🟢 Open'
        case 'closed':
            return '🔴 Closed'
        case 'pre-market':
            return '🟡 Pre-Market'
        case 'after-hours':
            return '🟠 After-Hours'
        default:
            return status
    }
}

function getMarketStatusClass(status: string): string {
    switch (status) {
        case 'open':
            return 'bg-green-600 text-white'
        case 'closed':
            return 'bg-red-600 text-white'
        case 'pre-market':
            return 'bg-yellow-600 text-black'
        case 'after-hours':
            return 'bg-orange-600 text-white'
        default:
            return 'bg-gray-600 text-white'
    }
}


async function handleAdd(payload: WatchCreate) {
    try {
        await saveWatch(payload)
        await load()
    } catch (error: unknown) {
        let message = 'Unknown error'
        if (error instanceof AxiosError){
            if (error.response && error.response.data && error.response.data.detail) {
                message = error.response.data.detail
            } else {
                message = `Error: ${error.message}`
            }
        } else {
            if (error instanceof Error) message = 'Error: unknown error'
        }
        
        console.log(error)
        addWatchRef.value?.setError(message)
    }
}

async function handleRefreshNow() {
    isRefreshing.value = true
    try {
        await loadStatus()
        await loadInfo()
    } catch (error) {
        console.error('Failed to refresh:', error)
    } finally {
        isRefreshing.value = false
    }
}

async function handleDelete(ticker: string) {
    if (!confirm(`Are you sure you want to delete watch for ${ticker}?`)) {
        return
    }
    
    try {
        await deleteWatch(ticker)
        await load()
    } catch (error: unknown) {
        const message = error instanceof Error ? error.message : 'Failed to delete watch'
        console.error(message)
        alert(message)
    }
}

function handleEdit(watch: Watch) {
    watchToEdit.value = watch
    editDialogOpen.value = true
}

async function handleEditSave(payload: WatchCreate) {
    try {
        await saveWatch(payload)
        editDialogOpen.value = false
        watchToEdit.value = null
        await load()
    } catch (error: unknown) {
        let message = 'Unknown error'
        if (error instanceof AxiosError){
            if (error.response && error.response.data && error.response.data.detail) {
                message = error.response.data.detail
            } else {
                message = `Error: ${error.message}`
            }
        } else {
            if (error instanceof Error) message = 'Error: unknown error'
        }
        
        console.log(error)
        editWatchRef.value?.setError(message)
    }
}

function handleEditCancel() {
    editDialogOpen.value = false
    watchToEdit.value = null
}



onMounted(() => {
    load()
    connectWS()
    // Reconnect WebSocket when page becomes visible (e.g., after sleep/wake)
    document.addEventListener('visibilitychange', handleVisibilityChange)
})

onBeforeUnmount(() => {
    ws?.close()
    document.removeEventListener('visibilitychange', handleVisibilityChange)
})
</script>