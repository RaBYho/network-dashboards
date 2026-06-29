<template>
  <div class="flex flex-col h-full bg-gray-50">
    <!-- Topbar -->
    <div
      class="flex items-center justify-between px-5 py-3 bg-white border-b border-gray-200"
    >
      <div class="flex items-center gap-2">
        <i class="ti ti-layout-dashboard text-blue-500 text-base"></i>
        <span class="text-sm font-medium text-gray-800">Vue globale</span>
      </div>
      <div class="flex items-center gap-2">
        <span
          class="text-xs px-2 py-1 rounded-full"
          :class="
            store.connected
              ? 'bg-green-50 text-green-700'
              : 'bg-red-50 text-red-600'
          "
        >
          <span
            class="inline-block w-1.5 h-1.5 rounded-full mr-1 align-middle"
            :class="store.connected ? 'bg-green-500' : 'bg-red-500'"
          ></span>
          {{ store.connected ? "Connecté" : "Déconnecté" }}
        </span>
        <span class="text-xs text-gray-400">Màj : {{ store.interval }}s</span>
      </div>
    </div>

    <!-- Contenu -->
    <div class="flex-1 p-4 flex flex-col gap-3 overflow-auto">
      <!-- KPI row -->
      <div class="grid grid-cols-4 gap-3">
        <KpiCard
          label="Débit descendant"
          :value="store.totalDownload.toFixed(1)"
          unit="Mbps"
          sub="toutes interfaces"
          icon="ti-arrow-down"
          value-class="text-blue-600"
        />
        <KpiCard
          label="Débit montant"
          :value="store.totalUpload.toFixed(1)"
          unit="Mbps"
          sub="toutes interfaces"
          icon="ti-arrow-up"
          value-class="text-blue-600"
        />
        <KpiCard
          label="Latence moy."
          :value="avgLatency.toFixed(0)"
          unit="ms"
          sub="via 8.8.8.8"
          icon="ti-clock"
          :value-class="
            avgLatency > store.thresholds.latency_ms
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
      </div>

      <!-- Graphiques ligne 1 -->
      <div class="grid grid-cols-3 gap-3">
        <div class="col-span-2 bg-white border border-gray-200 rounded-lg p-3">
          <div class="flex items-center justify-between mb-2">
            <span
              class="text-xs font-medium text-gray-500 flex items-center gap-1"
            >
              <i class="ti ti-chart-line"></i> Débit temps réel
            </span>
            <div class="flex gap-3 text-xs text-gray-400">
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
            ref="bandwidthChart"
            type="line"
            height="160"
            :options="bandwidthChartOptions"
            :series="bandwidthSeries"
          />
        </div>

        <div class="bg-white border border-gray-200 rounded-lg p-3">
          <div class="flex items-center justify-between mb-2">
            <span
              class="text-xs font-medium text-gray-500 flex items-center gap-1"
            >
              <i class="ti ti-clock"></i> Latence RTT
            </span>
            <div class="flex gap-3 text-xs text-gray-400">
              <span
                v-for="(iface, idx) in monitoredInterfaces"
                :key="iface.name"
              >
                <span
                  class="inline-block w-3 h-0.5 align-middle mr-1"
                  :style="{ backgroundColor: colors[idx % colors.length] }"
                ></span>
                {{ iface.name }}
              </span>
            </div>
          </div>
          <apexchart
            ref="latencyChart"
            type="line"
            height="160"
            :options="latencyChartOptions"
            :series="latencySeries"
          />
        </div>
      </div>

      <!-- Ligne du bas -->
      <div class="grid grid-cols-3 gap-3">
        <!-- Utilisation réseau -->
        <div class="bg-white border border-gray-200 rounded-lg p-3">
          <div
            class="text-xs font-medium text-gray-500 flex items-center gap-1 mb-3"
          >
            <i class="ti ti-gauge"></i> Utilisation réseau
          </div>
          <UsageBar
            v-for="iface in ifaceUsage"
            :key="iface.name"
            :label="iface.name"
            :value="parseFloat(iface.pct)"
            :color="iface.name.includes('w') ? 'green' : 'blue'"
            class="mb-3 last:mb-0"
          />
        </div>

        <!-- Métriques clés -->
        <div class="bg-white border border-gray-200 rounded-lg p-3">
          <div
            class="text-xs font-medium text-gray-500 flex items-center gap-1 mb-2"
          >
            <i class="ti ti-list"></i> Métriques clés
          </div>
          <div
            v-for="m in keyMetrics"
            :key="m.label"
            class="flex justify-between items-center py-1.5 border-b border-gray-100 last:border-none text-xs"
          >
            <span class="text-gray-500">{{ m.label }}</span>
            <span class="font-medium" :class="m.class">{{ m.value }}</span>
          </div>
        </div>

        <!-- Disponibilité dynamique -->
        <div class="bg-white border border-gray-200 rounded-lg p-3">
          <div
            class="text-xs font-medium text-gray-500 flex items-center gap-1 mb-2"
          >
            <i class="ti ti-server"></i> Disponibilité
          </div>
          <div class="text-center py-2">
            <div
              class="text-3xl font-medium"
              :class="uptimePercent >= 99 ? 'text-green-600' : 'text-amber-500'"
            >
              {{ uptimePercent.toFixed(1) }}<span class="text-sm">%</span>
            </div>
            <div class="text-xs text-gray-400 mt-1">{{ uptimePeriod }}</div>
          </div>
          <div
            v-for="d in disponibilite"
            :key="d.label"
            class="flex justify-between items-center py-1.5 border-b border-gray-100 last:border-none text-xs"
          >
            <span class="text-gray-500">
              <span
                class="inline-block w-1.5 h-1.5 rounded-full mr-1 align-middle"
                :class="d.dot"
              ></span>
              {{ d.label }}
            </span>
            <span class="font-medium text-gray-700">{{ d.value }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from "vue";
import { useNetworkStore } from "../stores/networkStore";
import KpiCard from "../components/layout/KpiCard.vue";
import UsageBar from "../components/layout/UsageBar.vue";

const store = useNetworkStore();
const bandwidthChart = ref(null);
const latencyChart = ref(null);

// Couleurs pour les graphiques
const colors = [
  "#3B82F6",
  "#22C55E",
  "#8B5CF6",
  "#F59E0B",
  "#EF4444",
  "#EC4899",
];

// Interfaces surveillées
const monitoredInterfaces = computed(() =>
  store.interfaces.filter((i) => i.monitored),
);

// ── Métriques calculées (agrégation sur toutes les interfaces) ──
const avgLatency = computed(() => {
  const latencies = monitoredInterfaces.value.map(
    (i) => store.latency[i.name]?.avg_ms || 0,
  );
  return latencies.length
    ? latencies.reduce((a, b) => a + b, 0) / latencies.length
    : 0;
});

const avgPacketLoss = computed(() => {
  const losses = monitoredInterfaces.value.map(
    (i) => store.latency[i.name]?.packet_loss_pct || 0,
  );
  return losses.length ? losses.reduce((a, b) => a + b, 0) / losses.length : 0;
});

// Utilisation réseau (pourcentage par rapport à 1000 Mbps ou 300 Mbps)
const ifaceUsage = computed(() =>
  monitoredInterfaces.value.map((iface) => {
    const bw = store.bandwidth[iface.name] || { download_Mbps: 0 };
    const max = iface.name.includes("w") ? 300 : 1000;
    return {
      name: iface.name,
      pct: Math.min(((bw.download_Mbps / max) * 100).toFixed(1), 100),
    };
  }),
);

// Métriques clés (une sélection pour la première interface surveillée)
const keyMetrics = computed(() => {
  const firstIface = monitoredInterfaces.value[0];
  if (!firstIface) return [];
  const lat = store.latency[firstIface.name] || {};
  return [
    {
      label: `RTT min (${firstIface.name})`,
      value: `${(lat.min_ms || 0).toFixed(0)} ms`,
      class: "text-gray-700",
    },
    {
      label: `RTT max (${firstIface.name})`,
      value: `${(lat.max_ms || 0).toFixed(0)} ms`,
      class: "text-gray-700",
    },
    {
      label: `Jitter (${firstIface.name})`,
      value: `${(lat.jitter_ms || 0).toFixed(1)} ms`,
      class:
        (lat.jitter_ms || 0) > store.thresholds.jitter_ms
          ? "text-amber-500"
          : "text-gray-700",
    },
    {
      label: "Taux d'erreur",
      value: `${(lat.packet_loss_pct || 0).toFixed(1)}%`,
      class: "text-green-600",
    },
    { label: "Connexions", value: "142", class: "text-gray-700" }, // Peut rester statique si pas de source
  ];
});

// ── Disponibilité dynamique ──────────────────────────
const connectionHistory = ref([]); // stocke les derniers statuts (true/false)
const MAX_HISTORY = 100;
const disconnectionCount = ref(0);
const lastConnectedTime = ref(Date.now());
const onlineDuration = ref(0);
let onlineTimer = null;

// Pourcentage de temps disponible sur les derniers échantillons
const uptimePercent = computed(() => {
  if (connectionHistory.value.length === 0) return 100;
  const successes = connectionHistory.value.filter(Boolean).length;
  return (successes / connectionHistory.value.length) * 100;
});

// Période d'analyse (basée sur l'intervalle et le nombre de points)
const uptimePeriod = computed(() => {
  const minutes = Math.round((MAX_HISTORY * store.interval) / 60);
  return `dernières ${minutes} min`;
});

// Durée en ligne formatée
const formatDuration = (seconds) => {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  return `${h > 0 ? h + "h " : ""}${m}m ${s}s`;
};

// Mise à jour de la durée en ligne
function updateOnlineDuration() {
  if (store.connected) {
    onlineDuration.value = Math.floor(
      (Date.now() - lastConnectedTime.value) / 1000,
    );
  } else {
    onlineDuration.value = 0;
  }
}

// Surveille les changements de connexion
watch(
  () => store.connected,
  (newVal, oldVal) => {
    // Ajouter le nouveau statut à l'historique
    connectionHistory.value.push(newVal);
    if (connectionHistory.value.length > MAX_HISTORY) {
      connectionHistory.value.shift();
    }

    // Détection d'une déconnexion
    if (oldVal === true && newVal === false) {
      disconnectionCount.value++;
    }

    // Mise à jour du temps de connexion
    if (newVal === true && oldVal === false) {
      lastConnectedTime.value = Date.now();
    }

    // Réinitialiser le timer de durée
    clearInterval(onlineTimer);
    if (newVal) {
      onlineTimer = setInterval(updateOnlineDuration, 1000);
    } else {
      onlineDuration.value = 0;
    }
  },
);

// À l'initialisation, on remplit l'historique avec l'état actuel
onMounted(() => {
  // Remplir avec l'état actuel (considérer qu'on vient de démarrer, donc 100% pour l'instant)
  connectionHistory.value = Array(MAX_HISTORY).fill(store.connected);
  if (store.connected) {
    onlineTimer = setInterval(updateOnlineDuration, 1000);
  }
});

onUnmounted(() => {
  clearInterval(onlineTimer);
});

// ── Données pour la section Disponibilité ────────────
const disponibilite = computed(() => [
  {
    label: "Temps en ligne",
    value: store.connected ? formatDuration(onlineDuration.value) : "0s",
    dot: "bg-green-500",
  },
  {
    label: "Interruptions",
    value: disconnectionCount.value,
    dot: "bg-red-500",
  },
  {
    label: "Tps de réponse",
    value: `${avgLatency.value.toFixed(0)} ms`,
    dot: "bg-green-500",
  },
]);

// ── Options ApexCharts – Débit ───────────────────────
const bandwidthChartOptions = computed(() => ({
  chart: {
    id: "bandwidth",
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
    labels: { show: false },
    axisBorder: { show: false },
    axisTicks: { show: false },
  },
  yaxis: {
    labels: {
      style: { fontSize: "10px" },
      formatter: (v) => v.toFixed(0) + "M",
    },
  },
  grid: { borderColor: "#F3F4F6", strokeDashArray: 4 },
  legend: { show: false },
  tooltip: { theme: "light", y: { formatter: (v) => v.toFixed(2) + " Mbps" } },
}));

const bandwidthSeries = computed(() => {
  return monitoredInterfaces.value.map((iface, idx) => ({
    name: `${iface.name} ↓`,
    data: store.history[iface.name]?.download || [],
  }));
});

// ── Options ApexCharts – Latence ─────────────────────
const latencyChartOptions = computed(() => ({
  chart: {
    id: "latency",
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
    labels: { show: false },
    axisBorder: { show: false },
    axisTicks: { show: false },
  },
  yaxis: {
    labels: {
      style: { fontSize: "10px" },
      formatter: (v) => v.toFixed(0) + "ms",
    },
  },
  annotations: {
    yaxis: [
      {
        y: store.thresholds.latency_ms,
        borderColor: "#EF4444",
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
  grid: { borderColor: "#F3F4F6", strokeDashArray: 4 },
  legend: { show: false },
  tooltip: { theme: "light", y: { formatter: (v) => v.toFixed(1) + " ms" } },
}));

const latencySeries = computed(() => {
  return monitoredInterfaces.value.map((iface) => ({
    name: `${iface.name} RTT`,
    data: store.history[iface.name]?.rtt || [],
  }));
});

// Mise à jour des graphiques sans reset
watch(
  () => store.history,
  () => {
    if (bandwidthChart.value) {
      bandwidthChart.value.updateSeries(
        monitoredInterfaces.value.map((iface) => ({
          name: `${iface.name} ↓`,
          data: store.history[iface.name]?.download || [],
        })),
        false,
        true,
      );
    }
    if (latencyChart.value) {
      latencyChart.value.updateSeries(
        monitoredInterfaces.value.map((iface) => ({
          name: `${iface.name} RTT`,
          data: store.history[iface.name]?.rtt || [],
        })),
        false,
        true,
      );
    }
  },
  { deep: true },
);
</script>
