<template>
  <div class="flex h-screen bg-gray-50 dark:bg-gray-900 overflow-hidden">
    <AppSidebar />
    <main class="flex-1 overflow-auto lg:pl-0">
      <RouterView v-slot="{ Component }">
        <transition name="page" mode="out-in">
          <component :is="Component" />
        </transition>
      </RouterView>
    </main>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from "vue";
import AppSidebar from "./components/layout/AppSidebar.vue";
import { useNetworkStore } from "./stores/networkStore";

const networkStore = useNetworkStore();
onMounted(async () => {
  await networkStore.fetchInterfaces(); // ✅ attendre la réponse
  networkStore.startPolling(); // ✅ puis démarrer le polling
});
onUnmounted(() => {
  networkStore.stopPolling();
});
</script>
<style>
.page-enter-active,
.page-leave-active {
  transition:
    opacity 0.2s ease,
    transform 0.2s ease;
}
.page-enter-from {
  opacity: 0;
  transform: translateY(6px);
}
.page-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>
