<template>
  <div
    class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 transition-shadow duration-200 hover:shadow-md"
    :class="{ 'animate-pulse': loading }"
  >
    <template v-if="loading">
      <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-16 mb-2"></div>
      <div class="h-5 bg-gray-200 dark:bg-gray-700 rounded w-24 mb-1"></div>
      <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-20"></div>
    </template>
    <template v-else>
      <div class="text-xs text-gray-400 dark:text-gray-500 mb-1 flex items-center gap-1">
        <i :class="`ti ${icon} text-sm`"></i>
        {{ label }}
      </div>
      <div class="text-xl font-medium tabular-nums transition-all duration-500" :class="valueClass">
        <transition name="num" mode="out-in">
          <span :key="value">{{ value }}</span>
        </transition>
        <span class="text-xs text-gray-400 dark:text-gray-500 ml-1">{{ unit }}</span>
      </div>
      <div class="text-xs text-gray-400 dark:text-gray-500 mt-1">{{ sub }}</div>
    </template>
  </div>
</template>

<script setup>
defineProps({
  label: { type: String, default: '' },
  value: { type: [String, Number], default: 0 },
  unit: { type: String, default: '' },
  sub: { type: String, default: '' },
  icon: { type: String, default: 'ti-chart-bar' },
  valueClass: { type: String, default: 'text-gray-800 dark:text-gray-100' },
  loading: { type: Boolean, default: false }
})
</script>

<style scoped>
.num-enter-active,
.num-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.num-enter-from {
  opacity: 0;
  transform: translateY(4px);
}
.num-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>