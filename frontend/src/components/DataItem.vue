<template>
  <div>
    <div class="text-sm text-gray-400 mb-1">{{ label }}</div>
    <div class="text-lg font-semibold text-gray-100">{{ value }}</div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  label: string
  value: string | number
}>()
</script>
