<template>
  <div class="flex flex-col h-full bg-gray-50">
    <!-- Topbar -->
    <div
      class="flex items-center justify-between px-5 py-3 bg-white border-b border-gray-200"
    >
      <div class="flex items-center gap-2">
        <i class="ti ti-clock text-purple-500 text-base"></i>
        <span class="text-sm font-medium text-gray-800">Latence & RTT</span>
      </div>
      <div class="flex items-center gap-3">
        <div class="flex gap-1">
          <button
            v-for="p in periods"
            :key="p.value"
            class="text-xs px-3 py-1 rounded-full border transition-colors"
            :class="
              activePeriod === p.value
                ? 'bg-purple-50 text-purple-700 border-purple-300'
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
          label="RTT moyen — eth0"
          :value="store.latency.eth0.avg_ms.toFixed(0)"
          unit="ms"
          sub="via 8.8.8.8"
          icon="ti-clock"
          :value-class="
            store.latency.eth0.avg_ms > store.thresholds.latency_ms
              ? 'text-amber-500'
              : 'text-green-600'
          "
        />
        <KpiCard
          label="RTT moyen — wlan0"
          :value="store.latency.wlan0.avg_ms.toFixed(0)"
          unit="ms"
          sub="via 8.8.8.8"
          icon="ti-clock"
          :value-class="
            store.latency.wlan0.avg_ms > store.thresholds.latency_ms
              ? 'text-amber-500'
              : 'text-green-600'
          "
        />
        <KpiCard
          label="Jitter — eth0"
          :value="store.latency.eth0.jitter_ms.toFixed(1)"
          unit="ms"
          sub="écart type RTT"
          icon="ti-wave-sine"
          :value-class="
            store.latency.eth0.jitter_ms > store.thresholds.jitter_ms
              ? 'text-amber-500'
              : 'text-green-600'
          "
        />
        <KpiCard
          label="Jitter — wlan0"
          :value="store.latency.wlan0.jitter_ms.toFixed(1)"
          unit="ms"
          sub="écart type RTT"
          icon="ti-wave-sine"
          :value-class="
            store.latency.wlan0.jitter_ms > store.thresholds.jitter_ms
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

      <!-- Grand graphique -->
      <div class="flex-1 bg-white border border-gray-200 rounded-lg p-4">
        <div class="flex items-center justify-between mb-3">
          <span
            class="text-xs font-medium text-gray-500 flex items-center gap-1"
          >
            <i class="ti ti-chart-line"></i>
            Variation RTT — eth0 &amp; wlan0
          </span>
          <div class="flex gap-4 text-xs text-gray-400">
            <span
              ><span
                class="inline-block w-3 h-0.5 bg-purple-500 align-middle mr-1"
              ></span
              >eth0 RTT</span
            >
            <span
              ><span
                class="inline-block w-3 h-0.5 bg-purple-200 align-middle mr-1"
              ></span
              >eth0 jitter</span
            >
            <span
              ><span
                class="inline-block w-3 h-0.5 bg-green-500 align-middle mr-1"
              ></span
              >wlan0 RTT</span
            >
            <span
              ><span
                class="inline-block w-3 h-0.5 bg-green-200 align-middle mr-1"
              ></span
              >wlan0 jitter</span
            >
            <span
              ><span
                class="inline-block w-3 h-0.5 bg-red-400 align-middle mr-1"
                style="border-top: 2px dashed #f87171"
              ></span
              >seuil</span
            >
          </div>
        </div>
        <apexchart
          type="line"
          height="220"
          :options="chartOptions"
          :series="series"
        />
      </div>

      <!-- Cartes cibles ping par interface -->
      <div class="grid grid-cols-2 gap-3">
        <!-- eth0 -->
        <div class="bg-white border border-gray-200 rounded-lg p-4">
          <div class="flex items-center gap-2 mb-3">
            <span class="w-2 h-2 rounded-full bg-green-500"></span>
            <span
              class="text-xs font-medium px-2 py-0.5 rounded-full bg-purple-50 text-purple-700"
              >eth0</span
            >
            <span class="text-xs text-gray-400">Cibles ping</span>
          </div>
          <div
            v-for="target in pingTargetsEth0"
            :key="target.host"
            class="flex items-center justify-between py-2 border-b border-gray-100 last:border-none"
          >
            <span class="text-xs font-mono text-gray-500">{{
              target.host
            }}</span>
            <span class="text-xs font-medium text-purple-700"
              >{{ target.rtt }} ms</span
            >
            <span
              class="text-xs px-2 py-0.5 rounded-full"
              :class="target.badgeClass"
            >
              {{ target.label }}
            </span>
          </div>
          <div
            class="flex items-center justify-between pt-2 mt-1 border-t border-gray-100"
          >
            <span class="text-xs text-gray-400">Jitter moy.</span>
            <span class="text-xs font-medium text-gray-700">
              {{ store.latency.eth0.jitter_ms.toFixed(1) }} ms
            </span>
            <span
              class="text-xs px-2 py-0.5 rounded-full"
              :class="
                store.latency.eth0.jitter_ms > store.thresholds.jitter_ms
                  ? 'bg-amber-50 text-amber-700'
                  : 'bg-green-50 text-green-700'
              "
            >
              {{
                store.latency.eth0.jitter_ms > store.thresholds.jitter_ms
                  ? "Variable"
                  : "Stable"
              }}
            </span>
          </div>
        </div>

        <!-- wlan0 -->
        <div class="bg-white border border-gray-200 rounded-lg p-4">
          <div class="flex items-center gap-2 mb-3">
            <span
              class="w-2 h-2 rounded-full"
              :class="
                store.latency.wlan0.avg_ms > store.thresholds.latency_ms
                  ? 'bg-amber-500'
                  : 'bg-green-500'
              "
            ></span>
            <span
              class="text-xs font-medium px-2 py-0.5 rounded-full bg-green-50 text-green-700"
              >wlan0</span
            >
            <span class="text-xs text-gray-400">Cibles ping</span>
          </div>
          <div
            v-for="target in pingTargetsWlan0"
            :key="target.host"
            class="flex items-center justify-between py-2 border-b border-gray-100 last:border-none"
          >
            <span class="text-xs font-mono text-gray-500">{{
              target.host
            }}</span>
            <span class="text-xs font-medium text-green-700"
              >{{ target.rtt }} ms</span
            >
            <span
              class="text-xs px-2 py-0.5 rounded-full"
              :class="target.badgeClass"
            >
              {{ target.label }}
            </span>
          </div>
          <div
            class="flex items-center justify-between pt-2 mt-1 border-t border-gray-100"
          >
            <span class="text-xs text-gray-400">Jitter moy.</span>
            <span class="text-xs font-medium text-gray-700">
              {{ store.latency.wlan0.jitter_ms.toFixed(1) }} ms
            </span>
            <span
              class="text-xs px-2 py-0.5 rounded-full"
              :class="
                store.latency.wlan0.jitter_ms > store.thresholds.jitter_ms
                  ? 'bg-amber-50 text-amber-700'
                  : 'bg-green-50 text-green-700'
              "
            >
              {{
                store.latency.wlan0.jitter_ms > store.thresholds.jitter_ms
                  ? "Variable"
                  : "Stable"
              }}
            </span>
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

// ── Sélecteur de période ─────────────────────────────
const periods = [
  { label: "1 min", value: "1m" },
  { label: "1 h", value: "1h" },
  { label: "24 h", value: "24h" },
];
const activePeriod = ref("1m");

// ── Métriques calculées ──────────────────────────────
const avgPacketLoss = computed(
  () =>
    (store.latency.eth0.packet_loss_pct + store.latency.wlan0.packet_loss_pct) /
    2,
);

// ── Badge qualité selon RTT ──────────────────────────
function qualityBadge(rtt) {
  if (rtt === 0) return { label: "—", badgeClass: "bg-gray-50 text-gray-400" };
  if (rtt < 30)
    return { label: "Bon", badgeClass: "bg-green-50 text-green-700" };
  if (rtt < 60)
    return { label: "Moyen", badgeClass: "bg-amber-50 text-amber-700" };
  return { label: "Dégradé", badgeClass: "bg-red-50 text-red-700" };
}

// ── Cibles ping (depuis le store + latence reçue) ────
const pingTargetsEth0 = computed(() =>
  store.pingTargets.map((host) => ({
    host,
    rtt: store.latency.eth0.avg_ms.toFixed(0),
    ...qualityBadge(store.latency.eth0.avg_ms),
  })),
);

const pingTargetsWlan0 = computed(() =>
  store.pingTargets.map((host) => ({
    host,
    rtt: store.latency.wlan0.avg_ms.toFixed(0),
    ...qualityBadge(store.latency.wlan0.avg_ms),
  })),
);

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
    width: [2, 1.5, 2, 1.5],
    dashArray: [0, 5, 0, 5],
  },
  colors: ["#8B5CF6", "#C4B5FD", "#22C55E", "#86EFAC"],
  xaxis: {
    categories: store.history.eth0.timestamps,
    labels: { style: { fontSize: "10px", colors: "#9CA3AF" } },
    axisBorder: { show: false },
    axisTicks: { show: false },
  },
  yaxis: {
    labels: {
      style: { fontSize: "10px", colors: "#9CA3AF" },
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
  grid: { borderColor: "#F3F4F6", strokeDashArray: 4 },
  legend: { show: false },
  tooltip: {
    theme: "light",
    y: { formatter: (v) => v.toFixed(1) + " ms" },
  },
}));

const series = computed(() => [
  { name: "eth0 RTT", data: store.history.eth0.rtt },
  { name: "eth0 jitter", data: store.history.eth0.rtt.map((v) => v * 0.15) },
  { name: "wlan0 RTT", data: store.history.wlan0.rtt },
  { name: "wlan0 jitter", data: store.history.wlan0.rtt.map((v) => v * 0.25) },
]);
</script>
