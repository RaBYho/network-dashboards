<template>
  <div class="flex flex-col h-full bg-gray-50 dark:bg-gray-900">
    <!-- Topbar -->
    <div
      class="flex items-center justify-between px-5 py-3 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700"
    >
      <div class="flex items-center gap-2">
        <i class="ti ti-activity text-blue-500 text-base"></i>
        <span class="text-sm font-medium text-gray-800 dark:text-gray-100"
          >Débit réseau</span
        >
      </div>
      <div class="flex items-center gap-3">
        <div class="flex gap-1">
          <button
            v-for="p in periods"
            :key="p.value"
            class="text-xs px-3 py-1 rounded-full border transition-colors"
            :class="
              activePeriod === p.value
                ? 'bg-blue-50 dark:bg-blue-900 text-blue-700 dark:text-blue-300 border-blue-300 dark:border-blue-700'
                : 'border-gray-200 dark:border-gray-600 text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700'
            "
            @click="activePeriod = p.value"
          >
            {{ p.label }}
          </button>
        </div>
        <span class="text-xs text-gray-400 dark:text-gray-500"
          >Màj : {{ store.interval }}s</span
        >
      </div>
    </div>

    <!-- Contenu -->
    <div class="flex-1 p-4 flex flex-col gap-4 overflow-auto">
      <!-- Section KPI -->
      <div>
        <h2 class="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">
          Résumé du débit
        </h2>
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
          <KpiCard
            label="Download total"
            :value="store.totalDownload.toFixed(1)"
            unit="Mbps"
            sub="toutes interfaces"
            icon="ti-arrow-down"
            value-class="text-blue-600"
          />
          <KpiCard
            label="Upload total"
            :value="store.totalUpload.toFixed(1)"
            unit="Mbps"
            sub="toutes interfaces"
            icon="ti-arrow-up"
            value-class="text-blue-600"
          />
          <KpiCard
            label="Pic download"
            :value="peakDownload.toFixed(1)"
            unit="Mbps"
            :sub="`il y a ${peakAgo}s`"
            icon="ti-trending-up"
            value-class="text-gray-800 dark:text-gray-100"
          />
          <KpiCard
            label="Total transféré"
            :value="totalTransferred"
            unit="Mo"
            sub="depuis démarrage"
            icon="ti-database"
            value-class="text-gray-800 dark:text-gray-100"
          />
        </div>
      </div>

      <!-- Section Graphique -->
      <div>
        <h2 class="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">
          Débit en temps réel
        </h2>
        <div
          class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4"
        >
          <div class="flex items-center justify-between mb-3">
            <span
              class="text-xs font-medium text-gray-500 dark:text-gray-400 flex items-center gap-1"
            >
              <i class="ti ti-chart-line"></i> Toutes les interfaces
            </span>
            <div
              class="flex gap-4 text-xs text-gray-400 dark:text-gray-500 flex-wrap"
            >
              <span
                v-for="(iface, idx) in monitoredInterfaces"
                :key="iface.name"
              >
                <span
                  class="inline-block w-3 h-0.5 align-middle mr-1"
                  :style="{ backgroundColor: colors[idx % colors.length] }"
                ></span>
                {{ iface.name }} ↓
              </span>
            </div>
          </div>
          <apexchart
            type="line"
            height="220"
            :options="chartOptions"
            :series="series"
          />
        </div>
      </div>

      <!-- Section Cartes par interface -->
      <div>
        <h2 class="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">
          Détail par interface
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div
            v-for="iface in monitoredInterfaces"
            :key="iface.name"
            class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4"
          >
            <!-- En-tête -->
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center gap-2">
                <span
                  class="w-2 h-2 rounded-full"
                  :class="iface.up ? 'bg-green-500' : 'bg-red-500'"
                ></span>
                <span
                  class="text-xs font-medium px-2 py-0.5 rounded-full"
                  :class="
                    iface.name.includes('w')
                      ? 'bg-green-50 dark:bg-green-900 text-green-700 dark:text-green-300'
                      : 'bg-blue-50 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
                  "
                >
                  {{ iface.name }}
                </span>
                <span class="text-xs text-gray-400 dark:text-gray-500">{{
                  iface.name.includes("w") ? "Wi-Fi" : "Filaire"
                }}</span>
              </div>
            </div>

            <!-- Download / Upload -->
            <div class="space-y-3">
              <div>
                <div class="flex justify-between text-xs mb-1">
                  <span class="text-gray-500 dark:text-gray-400"
                    ><i class="ti ti-arrow-down text-xs"></i> Download</span
                  >
                  <span class="font-medium text-blue-600 dark:text-blue-400">
                    {{
                      (store.bandwidth[iface.name]?.download_Mbps || 0).toFixed(
                        1,
                      )
                    }}
                    Mbps
                  </span>
                </div>
                <div
                  class="h-1.5 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden"
                >
                  <div
                    class="h-full rounded-full transition-all duration-500"
                    :class="
                      iface.name.includes('w') ? 'bg-green-500' : 'bg-blue-500'
                    "
                    :style="`width: ${Math.min(((store.bandwidth[iface.name]?.download_Mbps || 0) / maxSpeed(iface.name)) * 100, 100)}%`"
                  ></div>
                </div>
              </div>
              <div>
                <div class="flex justify-between text-xs mb-1">
                  <span class="text-gray-500 dark:text-gray-400"
                    ><i class="ti ti-arrow-up text-xs"></i> Upload</span
                  >
                  <span class="font-medium text-blue-600 dark:text-blue-400">
                    {{
                      (store.bandwidth[iface.name]?.upload_Mbps || 0).toFixed(1)
                    }}
                    Mbps
                  </span>
                </div>
                <div
                  class="h-1.5 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden"
                >
                  <div
                    class="h-full rounded-full transition-all duration-500"
                    :class="
                      iface.name.includes('w') ? 'bg-green-300' : 'bg-blue-300'
                    "
                    :style="`width: ${Math.min(((store.bandwidth[iface.name]?.upload_Mbps || 0) / maxSpeed(iface.name)) * 100, 100)}%`"
                  ></div>
                </div>
              </div>

              <!-- Totaux cumulés -->
              <div
                class="pt-2 border-t border-gray-100 dark:border-gray-700 grid grid-cols-2 gap-2"
              >
                <div class="text-xs">
                  <div class="text-gray-400 dark:text-gray-500">Total reçu</div>
                  <div class="font-medium text-gray-700 dark:text-gray-200">
                    {{ formatBytes(totals[iface.name]?.received) }}
                  </div>
                </div>
                <div class="text-xs">
                  <div class="text-gray-400 dark:text-gray-500">
                    Total envoyé
                  </div>
                  <div class="font-medium text-gray-700 dark:text-gray-200">
                    {{ formatBytes(totals[iface.name]?.sent) }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { useNetworkStore } from "../stores/networkStore";
import KpiCard from "../components/layout/KpiCard.vue";

const store = useNetworkStore();

const isDark = computed(() =>
  document.documentElement.classList.contains("dark"),
);

// ── Palette de couleurs ──────────────────────────────
const colors = [
  "#3B82F6",
  "#22C55E",
  "#8B5CF6",
  "#F59E0B",
  "#EF4444",
  "#EC4899",
];

// ── Interfaces surveillées ───────────────────────────
const monitoredInterfaces = computed(() =>
  store.interfaces.filter((i) => i.monitored),
);

// ── KPI calculés ─────────────────────────────────────
const peakDownload = computed(() => {
  let max = 0;
  monitoredInterfaces.value.forEach((iface) => {
    const hist = store.history[iface.name];
    if (hist && hist.download.length) max = Math.max(max, ...hist.download);
  });
  return max;
});

const peakAgo = computed(() => 0);

const totalTransferred = computed(() => {
  let sum = 0;
  monitoredInterfaces.value.forEach((iface) => {
    const hist = store.history[iface.name];
    if (hist) {
      sum += (hist.download || []).reduce((a, b) => a + b, 0);
      sum += (hist.upload || []).reduce((a, b) => a + b, 0);
    }
  });
  return ((sum * store.interval) / 8).toFixed(0);
});

// ── Totaux cumulés par interface (dynamique) ─────────
const totals = computed(() => {
  const result = {};
  monitoredInterfaces.value.forEach((iface) => {
    result[iface.name] = store.getInterfaceTotal(iface.name);
  });
  return result;
});

function formatBytes(bytes) {
  if (bytes === undefined || bytes === null) return "0 Mo";
  return (bytes / 1_048_576).toFixed(2) + " Mo";
}

function maxSpeed(ifaceName) {
  return ifaceName.includes("w") ? 300 : 1000;
}

// ── Options graphique ────────────────────────────────
const chartOptions = computed(() => ({
  chart: {
    toolbar: { show: false },
    animations: {
      enabled: true,
      easing: "linear",
      dynamicAnimation: { speed: 1000 },
    },
    background: "transparent",
    foreColor: isDark.value ? "#9CA3AF" : "#6B7280",
  },
  stroke: { curve: "smooth", width: 2 },
  colors: colors,
  xaxis: {
    categories:
      store.history[monitoredInterfaces.value[0]?.name]?.timestamps || [],
    labels: { style: { fontSize: "10px" } },
    axisBorder: { show: false },
    axisTicks: { show: false },
  },
  yaxis: {
    labels: {
      style: { fontSize: "10px" },
      formatter: (v) => v.toFixed(0) + "M",
    },
  },
  grid: {
    borderColor: isDark.value ? "#374151" : "#F3F4F6",
    strokeDashArray: 4,
  },
  legend: { show: false },
  tooltip: {
    theme: isDark.value ? "dark" : "light",
    y: { formatter: (v) => v.toFixed(2) + " Mbps" },
  },
}));

const series = computed(() => {
  const result = [];
  monitoredInterfaces.value.forEach((iface) => {
    const hist = store.history[iface.name] || { download: [], upload: [] };
    result.push({ name: `${iface.name} ↓`, data: hist.download });
    result.push({ name: `${iface.name} ↑`, data: hist.upload, dashArray: 5 });
  });
  return result;
});

const periods = [
  { label: "1 min", value: "1m" },
  { label: "1 h", value: "1h" },
  { label: "24 h", value: "24h" },
];
const activePeriod = ref("1m");
</script>
