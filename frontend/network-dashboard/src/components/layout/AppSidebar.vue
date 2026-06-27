<template>
  <aside
    class="w-48 h-screen shrink-0 border-r border-gray-200 bg-gray-50 flex flex-col"
  >
    <!-- Logo -->
    <div class="px-4 py-4 border-b border-gray-200">
      <div class="flex items-center gap-2">
        <i class="ti ti-activity text-blue-500 text-lg"></i>
        <span class="text-sm font-semibold text-gray-800">NetDash</span>
      </div>
    </div>

    <!-- Navigation principale -->
    <nav class="flex-1 py-3 overflow-y-auto">
      <div class="px-4 mb-1">
        <span class="text-xs font-medium text-gray-400 tracking-wider uppercase"
          >Navigation</span
        >
      </div>

      <RouterLink
        v-for="item in mainLinks"
        :key="item.path"
        :to="item.path"
        class="flex items-center gap-2 px-4 py-2 text-sm text-gray-600 cursor-pointer transition-colors hover:bg-gray-100 hover:text-gray-900"
        :class="
          $route.path === item.path
            ? 'bg-white text-gray-900 font-medium border-r-2 border-blue-500 [&_i]:text-blue-500'
            : ''
        "
      >
        <i :class="`ti ${item.icon} text-base`"></i>
        <span>{{ item.label }}</span>
      </RouterLink>

      <div class="mx-4 my-2 border-t border-gray-200"></div>

      <!-- Interfaces -->
      <div class="px-4 mb-1 mt-2">
        <span class="text-xs font-medium text-gray-400 tracking-wider uppercase"
          >Interfaces</span
        >
      </div>

      <RouterLink
        v-for="iface in networkStore.interfaces"
        :key="iface.name"
        :to="`/interface/${iface.name}`"
        class="flex items-center gap-2 px-4 py-2 text-sm text-gray-600 cursor-pointer transition-colors hover:bg-gray-100 hover:text-gray-900"
        :class="
          $route.path === `/interface/${iface.name}`
            ? 'bg-white text-gray-900 font-medium border-r-2 border-blue-500 [&_i]:text-blue-500'
            : ''
        "
      >
        <i :class="`ti ${iface.icon} text-base`"></i>
        <span>{{ iface.name }}</span>
        <span
          class="ml-auto w-2 h-2 rounded-full"
          :class="iface.up ? 'bg-green-500' : 'bg-gray-400'"
        ></span>
      </RouterLink>

      <div class="mx-4 my-2 border-t border-gray-200"></div>

      <!-- Paramètres -->
      <RouterLink
        to="/parametres"
        class="flex items-center gap-2 px-4 py-2 text-sm text-gray-600 cursor-pointer transition-colors hover:bg-gray-100 hover:text-gray-900"
        :class="
          $route.path === '/parametres'
            ? 'bg-white text-gray-900 font-medium border-r-2 border-blue-500 [&_i]:text-blue-500'
            : ''
        "
      >
        <i class="ti ti-settings text-base"></i>
        <span>Paramètres</span>
      </RouterLink>
    </nav>

    <!-- Statut en bas -->
    <div class="px-4 py-3 border-t border-gray-200">
      <div class="flex items-center gap-2">
        <span
          class="w-2 h-2 rounded-full"
          :class="networkStore.connected ? 'bg-green-500' : 'bg-red-500'"
        ></span>
        <span class="text-xs text-gray-500">
          {{ networkStore.connected ? "Connecté" : "Déconnecté" }}
        </span>
      </div>
      <div class="text-xs text-gray-400 mt-1">
        Màj : {{ networkStore.interval }}s
      </div>
    </div>
  </aside>
</template>

<script setup>
import { useNetworkStore } from "../../stores/networkStore";

const networkStore = useNetworkStore();

const mainLinks = [
  { path: "/", label: "Vue globale", icon: "ti-layout-dashboard" },
  { path: "/debit", label: "Débit", icon: "ti-activity" },
  { path: "/latence", label: "Latence", icon: "ti-clock" },
  { path: "/erreurs", label: "Erreurs", icon: "ti-alert-triangle" },
];
</script>
