<template>
  <div class="flex flex-col h-full bg-gray-50">
    <!-- Topbar -->
    <div
      class="flex items-center justify-between px-5 py-3 bg-white border-b border-gray-200"
    >
      <div class="flex items-center gap-2">
        <i class="ti ti-activity text-blue-500 text-base"></i>
        <span class="text-sm font-medium text-gray-800">Débit réseau</span>
      </div>
      <div class="flex items-center gap-3">
        <div class="flex gap-1">
          <button
            v-for="p in periods"
            :key="p.value"
            class="text-xs px-3 py-1 rounded-full border transition-colors"
            :class="
              activePeriod === p.value
                ? 'bg-blue-50 text-blue-700 border-blue-300'
                : 'border-gray-200 text-gray-500 hover:bg-gray-50'
            "
            @click="activePeriod = p.value"
          >
            {{ p.label }}
          </button>
        </div>
        <span class="text-xs text-gray-400">Màj : {{ store.interval }}s</span>
      </div>
    </div>

    <!-- Contenu -->
    <div class="flex-1 p-4 flex flex-col gap-3 overflow-auto">
      <!-- KPI row -->
      <div class="grid grid-cols-4 gap-3">
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
          value-class="text-gray-800"
        />
        <KpiCard
          label="Total transféré"
          :value="totalTransferred"
          unit="Mo"
          sub="depuis démarrage"
          icon="ti-database"
          value-class="text-gray-800"
        />
      </div>

      <!-- Grand graphique -->
      <div class="flex-1 bg-white border border-gray-200 rounded-lg p-4">
        <div class="flex items-center justify-between mb-3">
          <span
            class="text-xs font-medium text-gray-500 flex items-center gap-1"
          >
            <i class="ti ti-chart-line"></i>
            Débit en temps réel — toutes les interfaces
          </span>
          <div class="flex gap-4 text-xs text-gray-400">
            <span v-for="(iface, idx) in monitoredInterfaces" :key="iface.name">
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

      <!-- Cartes par interface -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div
          v-for="iface in monitoredInterfaces"
          :key="iface.name"
          class="bg-white border border-gray-200 rounded-lg p-4"
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
                    ? 'bg-green-50 text-green-700'
                    : 'bg-blue-50 text-blue-700'
                "
              >
                {{ iface.name }}
              </span>
              <span class="text-xs text-gray-400">{{
                iface.name.includes("w") ? "Wi-Fi" : "Filaire"
              }}</span>
            </div>
          </div>

          <!-- Download / Upload -->
          <div class="space-y-2">
            <div>
              <div class="flex justify-between text-xs mb-1">
                <span class="text-gray-500"
                  ><i class="ti ti-arrow-down text-xs"></i> Download</span
                >
                <span class="font-medium text-blue-600">
                  {{
                    (store.bandwidth[iface.name]?.download_Mbps || 0).toFixed(1)
                  }}
                  Mbps
                </span>
              </div>
              <div class="h-1.5 bg-gray-100 rounded-full overflow-hidden">
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
                <span class="text-gray-500"
                  ><i class="ti ti-arrow-up text-xs"></i> Upload</span
                >
                <span class="font-medium text-blue-600">
                  {{
                    (store.bandwidth[iface.name]?.upload_Mbps || 0).toFixed(1)
                  }}
                  Mbps
                </span>
              </div>
              <div class="h-1.5 bg-gray-100 rounded-full overflow-hidden">
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
            <div class="pt-2 border-t border-gray-100 grid grid-cols-2 gap-2">
              <div class="text-xs">
                <div class="text-gray-400">Total reçu</div>
                <div class="font-medium text-gray-700">
                  {{ formatBytes(totals[iface.name]?.received) || "0 Mo" }}
                </div>
              </div>
              <div class="text-xs">
                <div class="text-gray-400">Total envoyé</div>
                <div class="font-medium text-gray-700">
                  {{ formatBytes(totals[iface.name]?.sent) || "0 Mo" }}
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

// ── KPI globaux ──────────────────────────────────────
const peakDownload = computed(() => {
  let max = 0;
  monitoredInterfaces.value.forEach((iface) => {
    const hist = store.history[iface.name];
    if (hist && hist.download.length) {
      max = Math.max(max, ...hist.download);
    }
  });
  return max;
});

const peakAgo = computed(() => 0); // simplifié

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

// Fonction d'affichage en Mo
function formatBytes(bytes) {
  if (bytes === undefined || bytes === null) return "0 Mo";
  return (bytes / 1_048_576).toFixed(2) + " Mo";
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
  },
  stroke: { curve: "smooth", width: 2 },
  colors: colors,
  xaxis: {
    categories:
      store.history[monitoredInterfaces.value[0]?.name]?.timestamps || [],
    labels: { style: { fontSize: "10px", colors: "#9CA3AF" } },
    axisBorder: { show: false },
    axisTicks: { show: false },
  },
  yaxis: {
    labels: {
      style: { fontSize: "10px", colors: "#9CA3AF" },
      formatter: (v) => v.toFixed(0) + "M",
    },
  },
  grid: { borderColor: "#F3F4F6", strokeDashArray: 4 },
  legend: { show: false },
  tooltip: { theme: "light", y: { formatter: (v) => v.toFixed(2) + " Mbps" } },
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

// ── Sélecteur de période ─────────────────────────────
const periods = [
  { label: "1 min", value: "1m" },
  { label: "1 h", value: "1h" },
  { label: "24 h", value: "24h" },
];
const activePeriod = ref("1m");

// ── Vitesse max selon interface ──────────────────────
function maxSpeed(ifaceName) {
  return ifaceName.includes("w") ? 300 : 1000;
}
</script>
