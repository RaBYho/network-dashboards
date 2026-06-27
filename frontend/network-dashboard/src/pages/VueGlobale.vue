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
          sub="eth0 + wlan0"
          icon="ti-arrow-down"
          value-class="text-blue-600"
        />
        <KpiCard
          label="Débit montant"
          :value="store.totalUpload.toFixed(1)"
          unit="Mbps"
          sub="eth0 + wlan0"
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
          sub="eth0 + wlan0"
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
        <!-- Graphique débit -->
        <div class="col-span-2 bg-white border border-gray-200 rounded-lg p-3">
          <div class="flex items-center justify-between mb-2">
            <span
              class="text-xs font-medium text-gray-500 flex items-center gap-1"
            >
              <i class="ti ti-chart-line"></i> Débit temps réel
            </span>
            <div class="flex gap-3 text-xs text-gray-400">
              <span
                ><span
                  class="inline-block w-3 h-0.5 bg-blue-500 align-middle mr-1"
                ></span
                >eth0 ↓</span
              >
              <span
                ><span
                  class="inline-block w-3 h-0.5 bg-green-500 align-middle mr-1"
                ></span
                >wlan0 ↓</span
              >
            </div>
          </div>
          <apexchart
            type="line"
            height="160"
            :options="bandwidthChartOptions"
            :series="bandwidthSeries"
          />
        </div>

        <!-- Graphique latence -->
        <div class="bg-white border border-gray-200 rounded-lg p-3">
          <div class="flex items-center justify-between mb-2">
            <span
              class="text-xs font-medium text-gray-500 flex items-center gap-1"
            >
              <i class="ti ti-clock"></i> Latence RTT
            </span>
            <div class="flex gap-3 text-xs text-gray-400">
              <span
                ><span
                  class="inline-block w-3 h-0.5 bg-purple-500 align-middle mr-1"
                ></span
                >eth0</span
              >
              <span
                ><span
                  class="inline-block w-3 h-0.5 bg-green-500 align-middle mr-1"
                ></span
                >wlan0</span
              >
            </div>
          </div>
          <apexchart
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
          <div
            v-for="iface in ifaceUsage"
            :key="iface.name"
            class="mb-3 last:mb-0"
          >
            <div class="flex justify-between text-xs mb-1">
              <span class="text-gray-500">{{ iface.name }}</span>
              <span class="font-medium text-gray-700">{{ iface.pct }}%</span>
            </div>
            <div class="h-1.5 bg-gray-100 rounded-full overflow-hidden">
              <div
                class="h-full rounded-full transition-all duration-500"
                :class="iface.color"
                :style="`width: ${iface.pct}%`"
              ></div>
            </div>
          </div>
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

        <!-- Disponibilité -->
        <div class="bg-white border border-gray-200 rounded-lg p-3">
          <div
            class="text-xs font-medium text-gray-500 flex items-center gap-1 mb-2"
          >
            <i class="ti ti-server"></i> Disponibilité
          </div>
          <div class="text-center py-2">
            <div class="text-3xl font-medium text-green-600">
              99.8<span class="text-sm">%</span>
            </div>
            <div class="text-xs text-gray-400 mt-1">dernières 24h</div>
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
import { computed } from "vue";
import { useNetworkStore } from "../stores/networkStore";
import KpiCard from "../components/layout/KpiCard.vue";

const store = useNetworkStore();

// ── Métriques calculées ──────────────────────────────
const avgLatency = computed(
  () => (store.latency.eth0.avg_ms + store.latency.wlan0.avg_ms) / 2,
);
const avgPacketLoss = computed(
  () =>
    (store.latency.eth0.packet_loss_pct + store.latency.wlan0.packet_loss_pct) /
    2,
);

// ── Utilisation réseau (% par rapport à 1000 Mbps max) ──
const ifaceUsage = computed(() => [
  {
    name: "eth0",
    pct: Math.min(
      ((store.bandwidth.eth0.download_Mbps / 1000) * 100).toFixed(1),
      100,
    ),
    color: "bg-blue-500",
  },
  {
    name: "wlan0",
    pct: Math.min(
      ((store.bandwidth.wlan0.download_Mbps / 300) * 100).toFixed(1),
      100,
    ),
    color: "bg-green-500",
  },
]);

// ── Métriques clés ───────────────────────────────────
const keyMetrics = computed(() => [
  {
    label: "RTT min (eth0)",
    value: `${store.latency.eth0.min_ms} ms`,
    class: "text-gray-700",
  },
  {
    label: "RTT max (eth0)",
    value: `${store.latency.eth0.max_ms} ms`,
    class: "text-gray-700",
  },
  {
    label: "Jitter (eth0)",
    value: `${store.latency.eth0.jitter_ms} ms`,
    class: "text-gray-700",
  },
  {
    label: "Jitter (wlan0)",
    value: `${store.latency.wlan0.jitter_ms} ms`,
    class:
      store.latency.wlan0.jitter_ms > store.thresholds.jitter_ms
        ? "text-amber-500"
        : "text-gray-700",
  },
  { label: "Taux d'erreur", value: "0.8%", class: "text-green-600" },
  { label: "Connexions", value: "142", class: "text-gray-700" },
]);

const disponibilite = [
  { label: "Temps en ligne", value: "23h 57m", dot: "bg-green-500" },
  { label: "Interruptions", value: "1", dot: "bg-red-500" },
  { label: "Tps de réponse", value: "21 ms", dot: "bg-green-500" },
];

// ── Options ApexCharts — Débit ───────────────────────
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
  colors: ["#3B82F6", "#22C55E"],
  xaxis: {
    categories: store.history.eth0.timestamps,
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

const bandwidthSeries = computed(() => [
  { name: "eth0 ↓", data: store.history.eth0.download },
  { name: "wlan0 ↓", data: store.history.wlan0.download },
]);

// ── Options ApexCharts — Latence ─────────────────────
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
  colors: ["#8B5CF6", "#22C55E"],
  xaxis: {
    categories: store.history.eth0.timestamps,
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

const latencySeries = computed(() => [
  { name: "eth0", data: store.history.eth0.rtt },
  { name: "wlan0", data: store.history.wlan0.rtt },
]);
</script>
