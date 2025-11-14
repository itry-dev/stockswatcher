<template>
    <div class="min-h-screen bg-gray-900">
        <header class="bg-gray-800 shadow-lg border-b border-gray-700">
            <div class="max-w-7xl mx-auto py-4 px-4">
                <h1 class="text-2xl font-bold text-gray-100">📊 Stocks Watcher</h1>
            </div>
        </header>
        <main class="max-w-7xl mx-auto py-6 px-4">
            <router-view />
        </main>
    </div>
</template>

<script setup lang="ts">
// Router handles all routing now
</script>