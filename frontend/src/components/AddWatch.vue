<template>
    <section class="bg-gray-800 shadow-xl rounded p-4 space-y-4 border border-gray-700">
        <h2 class="text-lg font-semibold text-gray-100">Add Watch</h2>

        <div v-if="errorMessage" class="p-3 bg-red-900/30 border border-red-700 text-red-400 rounded">
            {{ errorMessage }}
        </div>

        <div class="space-y-3">
            <div>
                <label class="block text-sm font-medium mb-1 text-gray-300">Ticker</label>
                <input 
                    v-model="form.ticker" 
                    class="border border-gray-600 bg-gray-700 text-gray-100 rounded px-3 py-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500" 
                    placeholder="TXN" 
                    @input="form.ticker = form.ticker.toUpperCase()"
                />
            </div>

            <div>
                <label class="block text-sm font-medium mb-1 text-gray-300">Price Levels (comma separated)</label>
                <input 
                    v-model="form.levels" 
                    class="border border-gray-600 bg-gray-700 text-gray-100 rounded px-3 py-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500" 
                    placeholder="180, 172" 
                />
            </div>

            <button 
                @click="handleAdd" 
                :disabled="!isValid"
                class="w-full px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700 transition disabled:bg-gray-600 disabled:cursor-not-allowed"
            >
                Save Watch
            </button>
        </div>
    </section>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const emit = defineEmits<{
    add: [payload: { ticker: string; levels: number[]; enabled: boolean }]
    error: [message: string]
}>()

const form = ref({
    ticker: '',
    levels: ''
})

const errorMessage = ref('')

const isValid = computed(() => {
    return form.value.ticker.trim() !== ''
})


function handleAdd() {
    if (!isValid.value) return

    errorMessage.value = ''

    const levels = form.value.levels
        .split(',')
        .map(s => parseFloat(s.trim()))
        .filter(n => !Number.isNaN(n))

    emit('add', {
        ticker: form.value.ticker.toUpperCase(),
        levels,
        enabled: true
    })

    // Reset form
    form.value.ticker = ''
    form.value.levels = ''
}

function setError(message: string) {
    errorMessage.value = message
}

defineExpose({ setError })
</script>
