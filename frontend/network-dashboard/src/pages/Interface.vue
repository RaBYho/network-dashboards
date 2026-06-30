<template>
  <div class="flex flex-col h-full bg-gray-50 dark:bg-gray-900">
    <!-- Topbar -->
    <div
      class="flex items-center justify-between px-5 py-3 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700"
    >
      <div class="flex items-center gap-2">
        <i :class="`ti ${ifaceIcon} text-blue-500 text-base`"></i>
        <span class="text-sm font-medium text-gray-800 dark:text-gray-100"
          >Interface — {{ ifaceName }}</span
        >
        <span
          class="w-2 h-2 rounded-full"
          :class="isUp ? 'bg-green-500' : 'bg-red-500'"
        ></span>
        <span
          class="text-xs px-2 py-0.5 rounded-full"
          :class="
            isUp
              ? 'bg-green-50 dark:bg-green-900 text-green-700 dark:text-green-300'
              : 'bg-red-50 dark:bg-red-900 text-red-600 dark:text-red-300'
          "
        >
          {{ isUp ? "UP" : "DOWN" }}
        </span>
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
          Métriques de {{ ifaceName }}
        </h2>
        <div class="grid grid-cols-2 lg:grid-cols-5 gap-3">
          <KpiCard
            label="Download"
            :value="bw.download_Mbps.toFixed(1)"
            unit="Mbps"
            :sub="`${(bw.download_Mbps / 8).toFixed(2)} Mo/s`"
            icon="ti-arrow-down"
            value-class="text-blue-600"
          />
          <KpiCard
            label="Upload"
            :value="bw.upload_Mbps.toFixed(1)"
            unit="Mbps"
            :sub="`${(bw.upload_Mbps / 8).toFixed(2)} Mo/s`"
            icon="ti-arrow-up"
            value-class="text-blue-600"
          />
          <KpiCard
            label="Latence"
            :value="lat.avg_ms.toFixed(0)"
            unit="ms"
            :sub="`jitter ${lat.jitter_ms.toFixed(1)}ms`"
            icon="ti-clock"
            :value-class="
              lat.avg_ms > store.thresholds.latency_ms
                ? 'text-amber-500'
                : 'text-green-600'
            "
          />
          <KpiCard
            label="Perte paquets"
            :value="lat.packet_loss_pct.toFixed(1)"
            unit="%"
            sub="via ping"
            icon="ti-alert-triangle"
            :value-class="
              lat.packet_loss_pct > store.thresholds.packet_loss_pct
                ? 'text-red-600'
                : 'text-green-600'
            "
          />
          <KpiCard
            label="Connexions"
            :value="connexions"
            unit=""
            sub="actives"
            icon="ti-users"
            value-class="text-gray-800 dark:text-gray-100"
          />
        </div>
      </div>

      <!-- Section Graphique + Infos -->
      <div>
        <h2 class="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">
          Débit & latence
        </h2>
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-3">
          <div
            class="lg:col-span-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4"
          >
            <div class="flex items-center justify-between mb-3">
              <span
                class="text-xs font-medium text-gray-500 dark:text-gray-400 flex items-center gap-1"
              >
                <i class="ti ti-chart-line"></i> {{ ifaceName }}
              </span>
              <div
                class="flex gap-4 text-xs text-gray-400 dark:text-gray-500 flex-wrap"
              >
                <span
                  ><span
                    class="inline-block w-3 h-0.5 bg-blue-500 align-middle mr-1"
                  ></span
                  >Download</span
                >
                <span
                  ><span
                    class="inline-block w-3 h-0.5 bg-blue-300 align-middle mr-1"
                    style="border-top: 2px dashed #93c5fd"
                  ></span
                  >Upload</span
                >
                <span
                  ><span
                    class="inline-block w-3 h-0.5 bg-purple-500 align-middle mr-1"
                  ></span
                  >RTT</span
                >
              </div>
            </div>
            <apexchart
              type="line"
              height="200"
              :options="chartOptions"
              :series="series"
            />
          </div>

          <!-- Informations interface -->
          <div
            class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4"
          >
            <div
              class="text-xs font-medium text-gray-500 dark:text-gray-400 flex items-center gap-1 mb-3"
            >
              <i class="ti ti-info-circle"></i> Informations
            </div>
            <table class="w-full text-xs">
              <tbody>
                <tr
                  v-for="info in ifaceInfos"
                  :key="info.label"
                  class="border-b border-gray-100 dark:border-gray-700 last:border-none"
                >
                  <td class="py-2 text-gray-400 dark:text-gray-500 w-28">
                    {{ info.label }}
                  </td>
                  <td
                    class="py-2 font-mono font-medium text-gray-700 dark:text-gray-200"
                  >
                    {{ info.value }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Section Bas : Trafic, Erreurs, TCP -->
      <div>
        <h2 class="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">
          Détails et santé
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          <!-- Trafic cumulé -->
          <div
            class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4"
          >
            <div
              class="text-xs font-medium text-gray-500 dark:text-gray-400 flex items-center gap-1 mb-3"
            >
              <i class="ti ti-database"></i> Trafic cumulé
            </div>
            <div class="text-xs">
              <div
                class="flex justify-between py-2 border-b border-gray-100 dark:border-gray-700"
              >
                <span class="text-gray-500 dark:text-gray-400">Total reçu</span>
                <span class="font-medium text-gray-700 dark:text-gray-200">{{
                  formatBytes(totals.received)
                }}</span>
              </div>
              <div
                class="flex justify-between py-2 border-b border-gray-100 dark:border-gray-700"
              >
                <span class="text-gray-500 dark:text-gray-400"
                  >Total envoyé</span
                >
                <span class="font-medium text-gray-700 dark:text-gray-200">{{
                  formatBytes(totals.sent)
                }}</span>
              </div>
              <div
                class="flex justify-between py-2 border-b border-gray-100 dark:border-gray-700"
              >
                <span class="text-gray-500 dark:text-gray-400"
                  >Paquets reçus</span
                >
                <span class="font-medium text-gray-700 dark:text-gray-200">{{
                  (hist.download.length * 1000).toLocaleString()
                }}</span>
              </div>
              <div class="flex justify-between py-2">
                <span class="text-gray-500 dark:text-gray-400"
                  >Paquets envoyés</span
                >
                <span class="font-medium text-gray-700 dark:text-gray-200">{{
                  (hist.upload.length * 300).toLocaleString()
                }}</span>
              </div>
            </div>
            <div class="mt-3">
              <UsageBar
                :label="`Utilisation (${bw.download_Mbps.toFixed(1)} / ${maxSpeed} Mbps)`"
                :value="parseFloat(usagePct)"
              />
            </div>
          </div>

          <!-- Compteurs d'erreurs -->
          <div
            class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4"
          >
            <div
              class="text-xs font-medium text-gray-500 dark:text-gray-400 flex items-center gap-1 mb-3"
            >
              <i class="ti ti-alert-circle"></i> Compteurs d'erreurs
            </div>
            <div
              v-for="e in errorStats"
              :key="e.label"
              class="flex justify-between items-center py-2 border-b border-gray-100 dark:border-gray-700 last:border-none text-xs"
            >
              <span class="text-gray-500 dark:text-gray-400">{{
                e.label
              }}</span>
              <span
                class="font-medium"
                :class="e.val > 0 ? 'text-red-500' : 'text-green-600'"
                >{{ e.val }}</span
              >
            </div>
          </div>

          <!-- Connexions TCP (hauteur fixe + scroll) -->
          <div
            class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4"
          >
            <div
              class="text-xs font-medium text-gray-500 dark:text-gray-400 flex items-center gap-1 mb-3"
            >
              <i class="ti ti-plug"></i> Connexions TCP
            </div>
            <div class="max-h-40 overflow-y-auto">
              <div
                v-for="c in tcpStates"
                :key="c.state"
                class="flex justify-between items-center py-2 border-b border-gray-100 dark:border-gray-700 last:border-none text-xs"
              >
                <span class="text-gray-500 dark:text-gray-400">{{
                  c.state
                }}</span>
                <span
                  class="px-2 py-0.5 rounded-full font-medium"
                  :class="c.class"
                  >{{ c.count }}</span
                >
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
import { useRoute } from "vue-router";
import { useNetworkStore } from "../stores/networkStore";
import KpiCard from "../components/layout/KpiCard.vue";
import UsageBar from "../components/layout/UsageBar.vue";

const store = useNetworkStore();
const route = useRoute();
const isDark = computed(() =>
  document.documentElement.classList.contains("dark"),
);

// ── Interface courante ───────────────────────────────
const ifaceName = computed(() => route.params.name);
const ifaceIcon = computed(() =>
  ifaceName.value?.includes("w") ? "ti-wifi" : "ti-network",
);
const isUp = computed(
  () => store.interfaces.find((i) => i.name === ifaceName.value)?.up ?? false,
);

// ── Données du store ────────────────────────────────
const bw = computed(
  () =>
    store.bandwidth[ifaceName.value] ?? { download_Mbps: 0, upload_Mbps: 0 },
);
const lat = computed(
  () =>
    store.latency[ifaceName.value] ?? {
      avg_ms: 0,
      min_ms: 0,
      max_ms: 0,
      jitter_ms: 0,
      packet_loss_pct: 0,
    },
);
const hist = computed(
  () =>
    store.history[ifaceName.value] ?? {
      download: [],
      upload: [],
      rtt: [],
      timestamps: [],
    },
);

// ── Totaux cumulés dynamiques ────────────────────────
const totals = computed(() => store.getInterfaceTotal(ifaceName.value));

function formatBytes(bytes) {
  if (bytes === undefined || bytes === null) return "0 Mo";
  return (bytes / 1_048_576).toFixed(2) + " Mo";
}

// ── Périodes ─────────────────────────────────────────
const periods = [
  { label: "1 min", value: "1m" },
  { label: "1 h", value: "1h" },
  { label: "24 h", value: "24h" },
];
const activePeriod = ref("1m");

// ── KPI divers ───────────────────────────────────────
const connexions = computed(() => store.connections["global"]?.total || 0);
const maxSpeed = computed(() => (ifaceName.value?.includes("w") ? 300 : 1000));
const usagePct = computed(() =>
  Math.min(((bw.value.download_Mbps / maxSpeed.value) * 100).toFixed(1), 100),
);

// ── Informations interface (dynamiques) ──────────────
const ifaceInfos = computed(() => {
  const iface = store.interfaces.find((i) => i.name === ifaceName.value) || {};
  return [
    { label: "Adresse IP", value: iface.ipv4 || "—" },
    { label: "Masque", value: iface.netmask || "—" },
    { label: "Passerelle", value: iface.gateway || "—" },
    { label: "Adresse MAC", value: iface.mac || "—" },
    { label: "MTU", value: iface.mtu ? `${iface.mtu} octets` : "—" },
    {
      label: "Vitesse max",
      value: ifaceName.value?.includes("w") ? "300 Mbps" : "1000 Mbps",
    },
    {
      label: "Type",
      value: ifaceName.value?.includes("w") ? "Wi-Fi" : "Filaire",
    },
  ];
});

// ── Compteurs d'erreurs ──────────────────────────────
const ifaceErrors = computed(() =>
  store.errors.filter((e) => e.iface === ifaceName.value),
);
const errorStats = computed(() => [
  {
    label: "Erreurs entrant",
    val: ifaceErrors.value.filter((e) => e.severity === "critical").length,
  },
  {
    label: "Erreurs sortant",
    val: ifaceErrors.value.filter((e) => e.severity === "warn").length,
  },
  {
    label: "Paquets perdus ↓",
    val: Math.floor(lat.value.packet_loss_pct * 10),
  },
  { label: "Paquets perdus ↑", val: Math.floor(lat.value.packet_loss_pct * 5) },
  { label: "Taux d'erreur", val: `${lat.value.packet_loss_pct.toFixed(2)}%` },
]);

// ── Connexions TCP (dynamiques depuis le store) ──────
const tcpStates = computed(() => {
  const globalConn = store.connections["global"];
  if (!globalConn || !globalConn.states) return [];
  const states = globalConn.states;
  const classMap = {
    ESTABLISHED:
      "bg-green-50 dark:bg-green-900 text-green-700 dark:text-green-300",
    TIME_WAIT:
      "bg-amber-50 dark:bg-amber-900 text-amber-700 dark:text-amber-300",
    CLOSE_WAIT:
      "bg-amber-50 dark:bg-amber-900 text-amber-700 dark:text-amber-300",
    LISTEN: "bg-green-50 dark:bg-green-900 text-green-700 dark:text-green-300",
    FIN_WAIT: "bg-red-50 dark:bg-red-900 text-red-700 dark:text-red-300",
  };
  return Object.entries(states).map(([state, count]) => ({
    state,
    count,
    class:
      classMap[state] ||
      "bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400",
  }));
});

// ── Options ApexCharts ───────────────────────────────
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
  stroke: { curve: "smooth", width: [2, 1.5, 2], dashArray: [0, 5, 0] },
  colors: ["#3B82F6", "#93C5FD", "#8B5CF6"],
  xaxis: {
    categories: hist.value.timestamps,
    labels: { style: { fontSize: "10px" } },
    axisBorder: { show: false },
    axisTicks: { show: false },
  },
  yaxis: [
    {
      seriesName: "Download",
      labels: {
        style: { fontSize: "10px" },
        formatter: (v) => v.toFixed(0) + "M",
      },
    },
    { seriesName: "Upload", show: false },
    {
      seriesName: "RTT",
      opposite: true,
      labels: {
        style: { fontSize: "10px" },
        formatter: (v) => v.toFixed(0) + "ms",
      },
    },
  ],
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
  tooltip: { theme: isDark.value ? "dark" : "light" },
}));

const series = computed(() => [
  { name: "Download", data: hist.value.download },
  { name: "Upload", data: hist.value.upload },
  { name: "RTT", data: hist.value.rtt },
]);
</script>
