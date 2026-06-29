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
      <!-- KPI row : dynamique basée sur les deux premières interfaces surveillées -->
      <div class="grid grid-cols-5 gap-3">
        <!-- RTT moyen – première interface surveillée -->
        <KpiCard
          v-if="monitoredInterfaces[0]"
          :label="`RTT moyen — ${monitoredInterfaces[0].name}`"
          :value="
            (store.latency[monitoredInterfaces[0].name]?.avg_ms || 0).toFixed(0)
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
        <!-- RTT moyen – deuxième interface surveillée (si existe) -->
        <KpiCard
          v-if="monitoredInterfaces[1]"
          :label="`RTT moyen — ${monitoredInterfaces[1].name}`"
          :value="
            (store.latency[monitoredInterfaces[1].name]?.avg_ms || 0).toFixed(0)
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
        <!-- Jitter – première interface -->
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
        <!-- Jitter – deuxième interface -->
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
        <!-- Perte de paquets moyenne -->
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
        <!-- Si moins de 2 interfaces, on affiche des placeholders -->
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

      <!-- Grand graphique -->
      <div class="flex-1 bg-white border border-gray-200 rounded-lg p-4">
        <div class="flex items-center justify-between mb-3">
          <span
            class="text-xs font-medium text-gray-500 flex items-center gap-1"
          >
            <i class="ti ti-chart-line"></i>
            Variation RTT — toutes les interfaces
          </span>
          <div class="flex gap-4 text-xs text-gray-400">
            <span v-for="(iface, idx) in monitoredInterfaces" :key="iface.name">
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

      <!-- Cartes cibles ping par interface -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div
          v-for="iface in monitoredInterfaces"
          :key="iface.name"
          class="bg-white border border-gray-200 rounded-lg p-4"
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
                  ? 'bg-green-50 text-green-700'
                  : 'bg-purple-50 text-purple-700'
              "
            >
              {{ iface.name }}
            </span>
            <span class="text-xs text-gray-400">Cibles ping</span>
          </div>
          <div
            v-for="target in pingTargetsForInterface(iface.name)"
            :key="target.host"
            class="flex items-center justify-between py-2 border-b border-gray-100 last:border-none"
          >
            <span class="text-xs font-mono text-gray-500">{{
              target.host
            }}</span>
            <span
              class="text-xs font-medium"
              :class="
                iface.name.includes('w') ? 'text-green-700' : 'text-purple-700'
              "
            >
              {{ target.rtt }} ms
            </span>
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
              {{ (store.latency[iface.name]?.jitter_ms || 0).toFixed(1) }} ms
            </span>
            <span
              class="text-xs px-2 py-0.5 rounded-full"
              :class="
                (store.latency[iface.name]?.jitter_ms || 0) >
                store.thresholds.jitter_ms
                  ? 'bg-amber-50 text-amber-700'
                  : 'bg-green-50 text-green-700'
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

// ── Palette de couleurs ──────────────────────────────
const colors = [
  "#8B5CF6",
  "#22C55E",
  "#3B82F6",
  "#F59E0B",
  "#EF4444",
  "#EC4899",
];

// ── Interfaces surveillées ───────────────────────────
const monitoredInterfaces = computed(() =>
  store.interfaces.filter((i) => i.monitored),
);

// ── Métriques agrégées ──────────────────────────────
const avgPacketLoss = computed(() => {
  const interfaces = monitoredInterfaces.value;
  if (interfaces.length === 0) return 0;
  const sum = interfaces.reduce(
    (acc, iface) => acc + (store.latency[iface.name]?.packet_loss_pct || 0),
    0,
  );
  return sum / interfaces.length;
});

// ── Badge qualité selon RTT ──────────────────────────
function qualityBadge(rtt) {
  if (rtt === 0) return { label: "—", badgeClass: "bg-gray-50 text-gray-400" };
  if (rtt < 30)
    return { label: "Bon", badgeClass: "bg-green-50 text-green-700" };
  if (rtt < 60)
    return { label: "Moyen", badgeClass: "bg-amber-50 text-amber-700" };
  return { label: "Dégradé", badgeClass: "bg-red-50 text-red-700" };
}

// ── Cibles ping pour une interface ───────────────────
function pingTargetsForInterface(ifaceName) {
  const lat = store.latency[ifaceName] || { avg_ms: 0 };
  return store.pingTargets.map((host) => ({
    host,
    rtt: lat.avg_ms.toFixed(0),
    ...qualityBadge(lat.avg_ms),
  }));
}

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
    width: 2,
  },
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

const series = computed(() => {
  const result = [];
  monitoredInterfaces.value.forEach((iface) => {
    const hist = store.history[iface.name] || { rtt: [] };
    result.push({ name: `${iface.name} RTT`, data: hist.rtt });
    // On peut aussi ajouter une série jitter approximative
    result.push({
      name: `${iface.name} jitter`,
      data: hist.rtt.map((v) => v * 0.15), // approximation, à adapter si jitter réel dispo
      dashArray: 5,
    });
  });
  return result;
});
</script>
