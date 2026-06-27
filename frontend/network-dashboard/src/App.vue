<template>
  <div class="flex h-screen bg-gray-50 overflow-hidden">
    <AppSidebar />
    <main class="flex-1 overflow-auto">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import AppSidebar from './components/layout/AppSidebar.vue'
import { useNetworkStore } from './stores/networkStore'

const networkStore = useNetworkStore()
onMounted(() => networkStore.startPolling())
onUnmounted(() => networkStore.stopPolling())
</script>