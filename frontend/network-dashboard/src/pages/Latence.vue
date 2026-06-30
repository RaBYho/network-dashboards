<template>
  <div class="flex flex-col h-full bg-gray-50 dark:bg-gray-900">
    <!-- Topbar -->
    <div
      class="flex items-center justify-between px-5 py-3 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700"
    >
      <div class="flex items-center gap-2">
        <i class="ti ti-clock text-purple-500 text-base"></i>
        <span class="text-sm font-medium text-gray-800 dark:text-gray-100"
          >Latence & RTT</span
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
                ? 'bg-purple-50 dark:bg-purple-900 text-purple-700 dark:text-purple-300 border-purple-300 dark:border-purple-700'
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
          Indicateurs de latence
        </h2>
        <div class="grid grid-cols-2 lg:grid-cols-5 gap-3">
          <KpiCard
            v-if="monitoredInterfaces[0]"
            :label="`RTT moyen — ${monitoredInterfaces[0].name}`"
            :value="
              (store.latency[monitoredInterfaces[0].name]?.avg_ms || 0).toFixed(
                0,
              )
            "
            unit="ms"
            sub="via 8.8.8.8"
            icon="ti-clock"
            :value-class="
              (store.latency[monitoredInterfaces[0].name]?.avg_ms || 0) >
              store.thresholds.latency_ms
                ? 'text-amber-500'
                : 'text-green-600'
            "
          />
          <KpiCard
            v-if="monitoredInterfaces[1]"
            :label="`RTT moyen — ${monitoredInterfaces[1].name}`"
            :value="
              (store.latency[monitoredInterfaces[1].name]?.avg_ms || 0).toFixed(
                0,
              )
            "
            unit="ms"
            sub="via 8.8.8.8"
            icon="ti-clock"
            :value-class="
              (store.latency[monitoredInterfaces[1].name]?.avg_ms || 0) >
              store.thresholds.latency_ms
                ? 'text-amber-500'
                : 'text-green-600'
            "
          />
          <KpiCard
            v-if="monitoredInterfaces[0]"
            :label="`Jitter — ${monitoredInterfaces[0].name}`"
            :value="
              (
                store.latency[monitoredInterfaces[0].name]?.jitter_ms || 0
              ).toFixed(1)
            "
            unit="ms"
            sub="écart type RTT"
            icon="ti-wave-sine"
            :value-class="
              (store.latency[monitoredInterfaces[0].name]?.jitter_ms || 0) >
              store.thresholds.jitter_ms
                ? 'text-amber-500'
                : 'text-green-600'
            "
          />
          <KpiCard
            v-if="monitoredInterfaces[1]"
            :label="`Jitter — ${monitoredInterfaces[1].name}`"
            :value="
              (
                store.latency[monitoredInterfaces[1].name]?.jitter_ms || 0
              ).toFixed(1)
            "
            unit="ms"
            sub="écart type RTT"
            icon="ti-wave-sine"
            :value-class="
              (store.latency[monitoredInterfaces[1].name]?.jitter_ms || 0) >
              store.thresholds.jitter_ms
                ? 'text-amber-500'
                : 'text-green-600'
            "
          />
          <KpiCard
            label="Perte paquets"
            :value="avgPacketLoss.toFixed(1)"
            unit="%"
            sub="toutes interfaces"
            icon="ti-alert-triangle"
            :value-class="
              avgPacketLoss > store.thresholds.packet_loss_pct
                ? 'text-red-600'
                : 'text-green-600'
            "
          />
          <!-- Placeholder si moins de 2 interfaces -->
          <KpiCard
            v-if="monitoredInterfaces.length < 1"
            label="Aucune interface"
            value="0"
            unit="ms"
            sub="surveillée"
            icon="ti-clock"
          />
          <KpiCard
            v-if="monitoredInterfaces.length < 2"
            label="Aucune interface"
            value="0"
            unit="ms"
            sub="supplémentaire"
            icon="ti-clock"
          />
        </div>
      </div>

      <!-- Section Graphique -->
      <div>
        <h2 class="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">
          Variation RTT
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
                {{ iface.name }} RTT
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

      <!-- Section Cibles ping -->
      <div>
        <h2 class="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">
          Cibles de ping
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div
            v-for="iface in monitoredInterfaces"
            :key="iface.name"
            class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4"
          >
            <div class="flex items-center gap-2 mb-3">
              <span
                class="w-2 h-2 rounded-full"
                :class="iface.up ? 'bg-green-500' : 'bg-red-500'"
              ></span>
              <span
                class="text-xs font-medium px-2 py-0.5 rounded-full"
                :class="
                  iface.name.includes('w')
                    ? 'bg-green-50 dark:bg-green-900 text-green-700 dark:text-green-300'
                    : 'bg-purple-50 dark:bg-purple-900 text-purple-700 dark:text-purple-300'
                "
              >
                {{ iface.name }}
              </span>
              <span class="text-xs text-gray-400 dark:text-gray-500"
                >Cibles ping</span
              >
            </div>
            <div
              v-for="target in pingTargetsForInterface(iface.name)"
              :key="target.host"
              class="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-700 last:border-none"
            >
              <span
                class="text-xs font-mono text-gray-500 dark:text-gray-400"
                >{{ target.host }}</span
              >
              <span
                class="text-xs font-medium"
                :class="
                  iface.name.includes('w')
                    ? 'text-green-700 dark:text-green-400'
                    : 'text-purple-700 dark:text-purple-400'
                "
              >
                {{ target.rtt }} ms
              </span>
              <span
                class="text-xs px-2 py-0.5 rounded-full"
                :class="target.badgeClass"
                >{{ target.label }}</span
              >
            </div>
            <div
              class="flex items-center justify-between pt-2 mt-1 border-t border-gray-100 dark:border-gray-700"
            >
              <span class="text-xs text-gray-400 dark:text-gray-500"
                >Jitter moy.</span
              >
              <span
                class="text-xs font-medium text-gray-700 dark:text-gray-200"
              >
                {{ (store.latency[iface.name]?.jitter_ms || 0).toFixed(1) }} ms
              </span>
              <span
                class="text-xs px-2 py-0.5 rounded-full"
                :class="
                  (store.latency[iface.name]?.jitter_ms || 0) >
                  store.thresholds.jitter_ms
                    ? 'bg-amber-50 dark:bg-amber-900 text-amber-700 dark:text-amber-300'
                    : 'bg-green-50 dark:bg-green-900 text-green-700 dark:text-green-300'
                "
              >
                {{
                  (store.latency[iface.name]?.jitter_ms || 0) >
                  store.thresholds.jitter_ms
                    ? "Variable"
                    : "Stable"
                }}
              </span>
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

const periods = [
  { label: "1 min", value: "1m" },
  { label: "1 h", value: "1h" },
  { label: "24 h", value: "24h" },
];
const activePeriod = ref("1m");

const colors = [
  "#8B5CF6",
  "#22C55E",
  "#3B82F6",
  "#F59E0B",
  "#EF4444",
  "#EC4899",
];

const monitoredInterfaces = computed(() =>
  store.interfaces.filter((i) => i.monitored),
);

const avgPacketLoss = computed(() => {
  const interfaces = monitoredInterfaces.value;
  if (interfaces.length === 0) return 0;
  const sum = interfaces.reduce(
    (acc, iface) => acc + (store.latency[iface.name]?.packet_loss_pct || 0),
    0,
  );
  return sum / interfaces.length;
});

function qualityBadge(rtt) {
  if (rtt === 0)
    return {
      label: "—",
      badgeClass:
        "bg-gray-50 dark:bg-gray-700 text-gray-400 dark:text-gray-500",
    };
  if (rtt < 30)
    return {
      label: "Bon",
      badgeClass:
        "bg-green-50 dark:bg-green-900 text-green-700 dark:text-green-300",
    };
  if (rtt < 60)
    return {
      label: "Moyen",
      badgeClass:
        "bg-amber-50 dark:bg-amber-900 text-amber-700 dark:text-amber-300",
    };
  return {
    label: "Dégradé",
    badgeClass: "bg-red-50 dark:bg-red-900 text-red-700 dark:text-red-300",
  };
}

function pingTargetsForInterface(ifaceName) {
  const lat = store.latency[ifaceName] || { avg_ms: 0 };
  return store.pingTargets.map((host) => ({
    host,
    rtt: lat.avg_ms.toFixed(0),
    ...qualityBadge(lat.avg_ms),
  }));
}

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
      formatter: (v) => v.toFixed(0) + "ms",
    },
    min: 0,
  },
  annotations: {
    yaxis: [
      {
        y: store.thresholds.latency_ms,
        borderColor: "#F87171",
        strokeDashArray: 5,
        label: {
          text: `seuil ${store.thresholds.latency_ms}ms`,
          style: {
            fontSize: "10px",
            color: "#EF4444",
            background: "transparent",
          },
        },
      },
    ],
  },
  grid: {
    borderColor: isDark.value ? "#374151" : "#F3F4F6",
    strokeDashArray: 4,
  },
  legend: { show: false },
  tooltip: {
    theme: isDark.value ? "dark" : "light",
    y: { formatter: (v) => v.toFixed(1) + " ms" },
  },
}));

const series = computed(() => {
  const result = [];
  monitoredInterfaces.value.forEach((iface) => {
    const hist = store.history[iface.name] || { rtt: [] };
    result.push({ name: `${iface.name} RTT`, data: hist.rtt });
    result.push({
      name: `${iface.name} jitter`,
      data: hist.rtt.map((v) => v * 0.15),
      dashArray: 5,
    });
  });
  return result;
});
</script>
