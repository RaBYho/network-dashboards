<template>
  <div
    class="bg-white border border-gray-200 rounded-lg p-3 transition-shadow duration-200 hover:shadow-md"
  >
    <div class="text-xs text-gray-400 mb-1 flex items-center gap-1">
      <i :class="`ti ${icon} text-sm`"></i>
      {{ label }}
    </div>
    <div
      class="text-xl font-medium tabular-nums transition-all duration-500"
      :class="valueClass"
    >
      <transition name="num" mode="out-in">
        <span :key="value">{{ value }}</span>
      </transition>
      <span class="text-xs text-gray-400 ml-1">{{ unit }}</span>
    </div>
    <div class="text-xs text-gray-400 mt-1">{{ sub }}</div>
  </div>
</template>

<script setup>
defineProps({
  label: { type: String, default: "" },
  value: { type: [String, Number], default: 0 },
  unit: { type: String, default: "" },
  sub: { type: String, default: "" },
  icon: { type: String, default: "ti-chart-bar" },
  valueClass: { type: String, default: "text-gray-800" },
});
</script>
<style scoped>
.num-enter-active,
.num-leave-active {
  transition:
    opacity 0.3s ease,
    transform 0.3s ease;
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
