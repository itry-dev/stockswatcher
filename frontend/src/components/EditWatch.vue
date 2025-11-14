<template>
    <section 
        v-if="isOpen"
        class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
        @click.self="handleCancel"
    >
        <div class="bg-gray-800 shadow-xl rounded p-6 space-y-4 border border-gray-700 w-full max-w-md">
            <div class="flex justify-between items-center">
                <h2 class="text-lg font-semibold text-gray-100">Edit Watch</h2>
                <button 
                    @click="handleCancel"
                    class="text-gray-400 hover:text-gray-200 text-2xl leading-none"
                >
                    ×
                </button>
            </div>

            <div v-if="errorMessage" class="p-3 bg-red-900/30 border border-red-700 text-red-400 rounded">
                {{ errorMessage }}
            </div>

            <div class="space-y-3">
                <div>
                    <label class="block text-sm font-medium mb-1 text-gray-300">Ticker</label>
                    <input 
                        v-model="form.ticker" 
                        disabled
                        class="border border-gray-600 bg-gray-600 text-gray-400 rounded px-3 py-2 w-full cursor-not-allowed" 
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

                <div class="flex gap-2 pt-2">
                    <button 
                        @click="handleSave" 
                        class="flex-1 px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700 transition"
                    >
                        Save
                    </button>
                    <button 
                        @click="handleCancel"
                        class="flex-1 px-4 py-2 rounded bg-gray-600 text-white hover:bg-gray-700 transition"
                    >
                        Cancel
                    </button>
                </div>
            </div>
        </div>
    </section>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { Watch } from '../types'

const props = defineProps<{
    isOpen: boolean
    watch: Watch | null
}>()

const emit = defineEmits<{
    save: [payload: { ticker: string; levels: number[]; enabled: boolean }]
    cancel: []
}>()

const form = ref({
    ticker: '',
    levels: ''
})

const errorMessage = ref('')

// Watch for changes to the watch prop to populate the form
watch(() => props.watch, (newWatch) => {
    if (newWatch) {
        form.value.ticker = newWatch.ticker
        form.value.levels = newWatch.levels.join(', ')
        errorMessage.value = ''
    }
}, { immediate: true })

function handleSave() {
    errorMessage.value = ''

    const levels = form.value.levels
        .split(',')
        .map(s => parseFloat(s.trim()))
        .filter(n => !Number.isNaN(n))

    emit('save', {
        ticker: form.value.ticker,
        levels,
        enabled: props.watch?.enabled ?? true
    })
}

function handleCancel() {
    errorMessage.value = ''
    emit('cancel')
}

function setError(message: string) {
    errorMessage.value = message
}

defineExpose({ setError })
</script>
