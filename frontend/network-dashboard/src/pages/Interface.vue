<template>
  <div class="flex flex-col h-full bg-gray-50">
    <!-- Topbar -->
    <div
      class="flex items-center justify-between px-5 py-3 bg-white border-b border-gray-200"
    >
      <div class="flex items-center gap-2">
        <i :class="`ti ${ifaceIcon} text-blue-500 text-base`"></i>
        <span class="text-sm font-medium text-gray-800"
          >Interface — {{ ifaceName }}</span
        >
        <span
          class="w-2 h-2 rounded-full"
          :class="isUp ? 'bg-green-500' : 'bg-red-500'"
        ></span>
        <span
          class="text-xs px-2 py-0.5 rounded-full"
          :class="
            isUp ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-600'
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
      <div class="grid grid-cols-5 gap-3">
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
          value-class="text-gray-800"
        />
      </div>

      <!-- Graphique + Infos -->
      <div class="grid grid-cols-3 gap-3">
        <!-- Grand graphique débit + latence -->
        <div class="col-span-2 bg-white border border-gray-200 rounded-lg p-4">
          <div class="flex items-center justify-between mb-3">
            <span
              class="text-xs font-medium text-gray-500 flex items-center gap-1"
            >
              <i class="ti ti-chart-line"></i>
              Débit &amp; latence — {{ ifaceName }}
            </span>
            <div class="flex gap-4 text-xs text-gray-400">
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
        <div class="bg-white border border-gray-200 rounded-lg p-4">
          <div
            class="text-xs font-medium text-gray-500 flex items-center gap-1 mb-3"
          >
            <i class="ti ti-info-circle"></i> Informations
          </div>
          <table class="w-full text-xs">
            <tbody>
              <tr
                v-for="info in ifaceInfos"
                :key="info.label"
                class="border-b border-gray-100 last:border-none"
              >
                <td class="py-2 text-gray-400 w-28">{{ info.label }}</td>
                <td class="py-2 font-mono font-medium text-gray-700">
                  {{ info.value }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Ligne du bas -->
      <div class="grid grid-cols-3 gap-3">
        <!-- Trafic cumulé -->
        <div class="bg-white border border-gray-200 rounded-lg p-4">
          <div
            class="text-xs font-medium text-gray-500 flex items-center gap-1 mb-3"
          >
            <i class="ti ti-database"></i> Trafic cumulé
          </div>
          <div
            v-for="s in trafficStats"
            :key="s.label"
            class="flex justify-between items-center py-2 border-b border-gray-100 last:border-none text-xs"
          >
            <span class="text-gray-500">{{ s.label }}</span>
            <span class="font-medium text-gray-700">{{ s.value }}</span>
          </div>
          <div class="mt-3">
            <div class="flex justify-between text-xs mb-1">
              <span class="text-gray-400">
                Utilisation ({{ bw.download_Mbps.toFixed(1) }} /
                {{ maxSpeed }} Mbps)
              </span>
              <span class="font-medium text-gray-600">{{ usagePct }}%</span>
            </div>
            <div class="h-1.5 bg-gray-100 rounded-full overflow-hidden">
              <div
                class="h-full bg-blue-500 rounded-full transition-all duration-500"
                :style="`width: ${usagePct}%`"
              ></div>
            </div>
          </div>
        </div>

        <!-- Compteurs d'erreurs -->
        <div class="bg-white border border-gray-200 rounded-lg p-4">
          <div
            class="text-xs font-medium text-gray-500 flex items-center gap-1 mb-3"
          >
            <i class="ti ti-alert-circle"></i> Compteurs d'erreurs
          </div>
          <div
            v-for="e in errorStats"
            :key="e.label"
            class="flex justify-between items-center py-2 border-b border-gray-100 last:border-none text-xs"
          >
            <span class="text-gray-500">{{ e.label }}</span>
            <span
              class="font-medium"
              :class="e.val > 0 ? 'text-red-500' : 'text-green-600'"
            >
              {{ e.val }}
            </span>
          </div>
        </div>

        <!-- Connexions TCP -->
        <div class="bg-white border border-gray-200 rounded-lg p-4">
          <div
            class="text-xs font-medium text-gray-500 flex items-center gap-1 mb-3"
          >
            <i class="ti ti-plug"></i> Connexions TCP
          </div>
          <div
            v-for="c in tcpStates"
            :key="c.state"
            class="flex justify-between items-center py-2 border-b border-gray-100 last:border-none text-xs"
          >
            <span class="text-gray-500">{{ c.state }}</span>
            <span class="px-2 py-0.5 rounded-full font-medium" :class="c.class">
              {{ c.count }}
            </span>
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

const store = useNetworkStore();
const route = useRoute();

// ── Interface courante ───────────────────────────────
const ifaceName = computed(() => route.params.name);
const ifaceIcon = computed(() =>
  ifaceName.value === "wlan0" ? "ti-wifi" : "ti-network",
);
const isUp = computed(
  () => store.interfaces.find((i) => i.name === ifaceName.value)?.up ?? false,
);

// ── Données du store pour cette interface ────────────
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

// ── Sélecteur de période ─────────────────────────────
const periods = [
  { label: "1 min", value: "1m" },
  { label: "1 h", value: "1h" },
  { label: "24 h", value: "24h" },
];
const activePeriod = ref("1m");

// ── KPI divers ───────────────────────────────────────
const connexions = computed(
  () => store.errors.filter((e) => e.iface === ifaceName.value).length + 82,
);
const maxSpeed = computed(() => (ifaceName.value === "wlan0" ? 300 : 1000));
const usagePct = computed(() =>
  Math.min(((bw.value.download_Mbps / maxSpeed.value) * 100).toFixed(1), 100),
);

// ── Trafic cumulé ────────────────────────────────────
const totalReceived = computed(() =>
  (
    (hist.value.download.reduce((a, b) => a + b, 0) * store.interval) /
    8
  ).toFixed(0),
);
const totalSent = computed(() =>
  ((hist.value.upload.reduce((a, b) => a + b, 0) * store.interval) / 8).toFixed(
    0,
  ),
);
const totalPackets = computed(() =>
  (hist.value.download.length * 1000).toLocaleString(),
);

const trafficStats = computed(() => [
  { label: "Total reçu", value: `${totalReceived.value} Mo` },
  { label: "Total envoyé", value: `${totalSent.value} Mo` },
  { label: "Paquets reçus", value: totalPackets.value },
  {
    label: "Paquets envoyés",
    value: Math.floor(hist.value.upload.length * 300).toLocaleString(),
  },
]);

// ── Infos interface ──────────────────────────────────
const ifaceInfos = computed(() => {
  const isWlan = ifaceName.value === "wlan0";
  return [
    { label: "Adresse IP", value: isWlan ? "192.168.1.87" : "192.168.1.42" },
    { label: "Masque", value: "255.255.255.0" },
    { label: "Passerelle", value: "192.168.1.1" },
    {
      label: "Adresse MAC",
      value: isWlan ? "b8:27:eb:aa:bb:cc" : "a4:c3:f0:12:34:56",
    },
    { label: "MTU", value: "1500 octets" },
    { label: "Vitesse max", value: isWlan ? "300 Mbps" : "1000 Mbps" },
    { label: "Type", value: isWlan ? "Wi-Fi" : "Filaire" },
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

// ── Connexions TCP ───────────────────────────────────
const tcpStates = computed(() => [
  { state: "ESTABLISHED", count: 82, class: "bg-green-50 text-green-700" },
  { state: "TIME_WAIT", count: 11, class: "bg-amber-50 text-amber-700" },
  { state: "CLOSE_WAIT", count: 3, class: "bg-amber-50 text-amber-700" },
  { state: "LISTEN", count: 2, class: "bg-green-50 text-green-700" },
  { state: "FIN_WAIT", count: 0, class: "bg-red-50 text-red-700" },
]);

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
  },
  stroke: {
    curve: "smooth",
    width: [2, 1.5, 2],
    dashArray: [0, 5, 0],
  },
  colors: ["#3B82F6", "#93C5FD", "#8B5CF6"],
  xaxis: {
    categories: hist.value.timestamps,
    labels: { style: { fontSize: "10px", colors: "#9CA3AF" } },
    axisBorder: { show: false },
    axisTicks: { show: false },
  },
  yaxis: [
    {
      seriesName: "Download",
      labels: {
        style: { fontSize: "10px", colors: "#9CA3AF" },
        formatter: (v) => v.toFixed(0) + "M",
      },
    },
    {
      seriesName: "Upload",
      show: false,
    },
    {
      seriesName: "RTT",
      opposite: true,
      labels: {
        style: { fontSize: "10px", colors: "#9CA3AF" },
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
  grid: { borderColor: "#F3F4F6", strokeDashArray: 4 },
  legend: { show: false },
  tooltip: { theme: "light" },
}));

const series = computed(() => [
  { name: "Download", data: hist.value.download },
  { name: "Upload", data: hist.value.upload },
  { name: "RTT", data: hist.value.rtt },
]);
</script>
