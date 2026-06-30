<template>
  <button 
    class="lg:hidden fixed top-3 left-3 z-50 p-2 rounded-md bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700"
    @click="open = !open"
  >
    <i class="ti ti-menu text-gray-600 dark:text-gray-300"></i>
  </button>

  <div v-if="open" class="lg:hidden fixed inset-0 bg-black/50 z-40" @click="open = false" />

  <aside
    :class="[
      'w-48 h-screen shrink-0 border-r border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 flex flex-col',
      'fixed lg:relative inset-y-0 left-0 z-50 transition-transform duration-300',
      open ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
    ]"
  >
    <div class="px-4 py-4 border-b border-gray-200 dark:border-gray-700">
      <div class="flex items-center gap-2">
        <i class="ti ti-activity text-blue-500 text-lg"></i>
        <span class="text-sm font-semibold text-gray-800 dark:text-gray-100">NetDash</span>
      </div>
    </div>

    <nav class="flex-1 py-3 overflow-y-auto">
      <div class="px-4 mb-1">
        <span class="text-xs font-medium text-gray-400 dark:text-gray-500 tracking-wider uppercase">Navigation</span>
      </div>

      <RouterLink
        v-for="item in mainLinks"
        :key="item.path"
        :to="item.path"
        @click="open = false"
        class="flex items-center gap-2 px-4 py-2 text-sm text-gray-600 dark:text-gray-300 cursor-pointer transition-colors hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-100"
        :class="$route.path === item.path ? 'bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 font-medium border-r-2 border-blue-500 [&_i]:text-blue-500' : ''"
      >
        <i :class="`ti ${item.icon} text-base`"></i>
        <span>{{ item.label }}</span>
      </RouterLink>

      <div class="mx-4 my-2 border-t border-gray-200 dark:border-gray-700"></div>

      <div class="px-4 mb-1 mt-2">
        <span class="text-xs font-medium text-gray-400 dark:text-gray-500 tracking-wider uppercase">Interfaces</span>
      </div>

      <RouterLink
        v-for="iface in networkStore.interfaces.filter(i => i.monitored)"
        :key="iface.name"
        :to="`/interface/${iface.name}`"
        @click="open = false"
        class="flex items-center gap-2 px-4 py-2 text-sm text-gray-600 dark:text-gray-300 cursor-pointer transition-colors hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-100"
        :class="$route.path === `/interface/${iface.name}` ? 'bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 font-medium border-r-2 border-blue-500 [&_i]:text-blue-500' : ''"
      >
        <i :class="`ti ${iface.icon} text-base`"></i>
        <span>{{ iface.name }}</span>
        <span class="ml-auto w-2 h-2 rounded-full" :class="iface.up ? 'bg-green-500' : 'bg-gray-400'"></span>
      </RouterLink>

      <div class="mx-4 my-2 border-t border-gray-200 dark:border-gray-700"></div>

      <RouterLink
        to="/parametres"
        @click="open = false"
        class="flex items-center gap-2 px-4 py-2 text-sm text-gray-600 dark:text-gray-300 cursor-pointer transition-colors hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-100"
        :class="$route.path === '/parametres' ? 'bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 font-medium border-r-2 border-blue-500 [&_i]:text-blue-500' : ''"
      >
        <i class="ti ti-settings text-base"></i>
        <span>Paramètres</span>
      </RouterLink>
    </nav>

    <div class="px-4 py-3 border-t border-gray-200 dark:border-gray-700">
      <div class="flex items-center gap-2">
        <span class="relative flex h-2 w-2">
          <span class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75" :class="networkStore.connected ? 'bg-green-400' : 'bg-red-400'"></span>
          <span class="relative inline-flex rounded-full h-2 w-2" :class="networkStore.connected ? 'bg-green-500' : 'bg-red-500'"></span>
        </span>
        <span class="text-xs text-gray-500 dark:text-gray-400">
          {{ networkStore.connected ? "Connecté" : "Déconnecté" }}
        </span>
      </div>
      <div class="text-xs text-gray-400 dark:text-gray-500 mt-1">Màj : {{ networkStore.interval }}s</div>
    </div>
  </aside>
</template>

<script setup>
import { ref } from 'vue'
import { useNetworkStore } from '../../stores/networkStore'
const networkStore = useNetworkStore()
const open = ref(false)

const mainLinks = [
  { path: '/', label: 'Vue globale', icon: 'ti-layout-dashboard' },
  { path: '/debit', label: 'Débit', icon: 'ti-activity' },
  { path: '/latence', label: 'Latence', icon: 'ti-clock' },
  { path: '/erreurs', label: 'Erreurs', icon: 'ti-alert-triangle' },
]
</script>