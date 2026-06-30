<template>
  <div>
    <div class="flex justify-between text-xs mb-1">
      <span class="text-gray-500 dark:text-gray-400">{{ label }}</span>
      <span class="font-medium text-gray-700 dark:text-gray-300"
        >{{ value }}%</span
      >
    </div>
    <div
      class="h-1.5 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden"
    >
      <div
        class="h-full rounded-full transition-all duration-700 ease-out"
        :class="[barColor, value > 80 ? 'animate-pulse' : '']"
        :style="`width: ${value}%`"
      ></div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  label: { type: String, default: "" },
  value: { type: Number, default: 0 },
  color: { type: String, default: "blue" },
});

const barColor = computed(() => {
  if (props.value > 80) return "bg-red-500";
  if (props.value > 60) return "bg-amber-500";
  return props.color === "green" ? "bg-green-500" : "bg-blue-500";
});
</script>
