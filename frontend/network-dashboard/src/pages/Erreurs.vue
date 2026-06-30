<template>
  <div class="flex flex-col h-full bg-gray-50 dark:bg-gray-900">
    <!-- Topbar -->
    <div
      class="flex items-center justify-between px-5 py-3 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700"
    >
      <div class="flex items-center gap-2">
        <i class="ti ti-alert-triangle text-red-500 text-base"></i>
        <span class="text-sm font-medium text-gray-800 dark:text-gray-100"
          >Erreurs & anomalies</span
        >
      </div>
      <div class="flex items-center gap-2">
        <button
          class="text-xs px-3 py-1 rounded border border-gray-200 dark:border-gray-600 text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center gap-1 transition-colors"
          @click="exportCsv"
        >
          <i class="ti ti-download text-xs"></i> Export CSV
        </button>
        <button
          class="text-xs px-3 py-1 rounded border border-gray-200 dark:border-gray-600 text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center gap-1 transition-colors"
          @click="store.errors.splice(0)"
        >
          <i class="ti ti-trash text-xs"></i> Vider
        </button>
      </div>
    </div>

    <!-- Contenu -->
    <div class="flex-1 p-4 flex flex-col gap-4 overflow-auto">
      <!-- Section KPI -->
      <div>
        <h2 class="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">
          Résumé des erreurs
        </h2>
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
          <KpiCard
            label="Erreurs critiques"
            :value="criticalCount"
            unit=""
            sub="depuis le début"
            icon="ti-circle-x"
            :value-class="criticalCount > 0 ? 'text-red-600' : 'text-green-600'"
          />
          <KpiCard
            label="Avertissements"
            :value="warnCount"
            unit=""
            sub="depuis le début"
            icon="ti-alert-circle"
            :value-class="warnCount > 0 ? 'text-amber-500' : 'text-green-600'"
          />
          <KpiCard
            label="Paquets perdus"
            :value="totalPacketLoss"
            unit=""
            sub="total cumulé"
            icon="ti-packages"
            value-class="text-gray-800 dark:text-gray-100"
          />
          <KpiCard
            label="Taux d'erreur"
            :value="avgErrorRate"
            unit="%"
            sub="toutes interfaces"
            icon="ti-check"
            :value-class="
              parseFloat(avgErrorRate) > store.thresholds.error_rate_pct
                ? 'text-red-600'
                : 'text-green-600'
            "
          />
        </div>
      </div>

      <!-- Section Histogramme -->
      <div>
        <h2 class="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">
          Fréquence des erreurs (dernière heure)
        </h2>
        <div
          class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4"
        >
          <apexchart
            type="bar"
            height="100"
            :options="histoOptions"
            :series="histoSeries"
          />
        </div>
      </div>

      <!-- Section Journal -->
      <div class="flex-1 flex flex-col min-h-0">
        <h2 class="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">
          Journal des erreurs
        </h2>
        <div
          class="flex-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 flex flex-col min-h-0"
        >
          <!-- Filtres -->
          <div class="flex items-center justify-between mb-3 flex-wrap gap-2">
            <span
              class="text-xs font-medium text-gray-500 dark:text-gray-400 flex items-center gap-1"
            >
              <i class="ti ti-list"></i> {{ filteredErrors.length }} entrée(s)
            </span>
            <div class="flex items-center gap-2 flex-wrap">
              <button
                v-for="f in severityFilters"
                :key="f.value"
                class="text-xs px-3 py-1 rounded-full border transition-colors"
                :class="
                  activeSeverity === f.value
                    ? f.activeClass
                    : 'border-gray-200 dark:border-gray-600 text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700'
                "
                @click="activeSeverity = f.value"
              >
                {{ f.label }}
              </button>
              <div class="w-px h-4 bg-gray-200 dark:bg-gray-600"></div>
              <button
                v-for="f in ifaceFilters"
                :key="f.value"
                class="text-xs px-3 py-1 rounded-full border transition-colors"
                :class="
                  activeIface === f.value
                    ? 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200 border-gray-300 dark:border-gray-500'
                    : 'border-gray-200 dark:border-gray-600 text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700'
                "
                @click="activeIface = f.value"
              >
                {{ f.label }}
              </button>
              <div class="w-px h-4 bg-gray-200 dark:bg-gray-600"></div>
              <div class="relative">
                <i
                  class="ti ti-search text-xs text-gray-400 absolute left-2 top-1/2 -translate-y-1/2"
                ></i>
                <input
                  v-model="search"
                  type="text"
                  placeholder="Rechercher..."
                  class="text-xs pl-7 pr-7 py-1.5 rounded border border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-900 text-gray-700 dark:text-gray-200 w-40 focus:outline-none focus:border-blue-300 dark:focus:border-blue-600"
                />
                <button
                  v-if="search"
                  @click="search = ''"
                  class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                >
                  <i class="ti ti-x text-xs"></i>
                </button>
              </div>
            </div>
          </div>

          <!-- Tableau -->
          <div class="flex-1 overflow-auto min-h-0">
            <table class="w-full text-xs border-collapse">
              <thead>
                <tr
                  class="border-b border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 sticky top-0"
                >
                  <th
                    class="text-left py-2 px-3 font-medium text-gray-400 dark:text-gray-500 w-32"
                  >
                    Horodatage
                  </th>
                  <th
                    class="text-left py-2 px-3 font-medium text-gray-400 dark:text-gray-500 w-24"
                  >
                    Sévérité
                  </th>
                  <th
                    class="text-left py-2 px-3 font-medium text-gray-400 dark:text-gray-500 w-20"
                  >
                    Interface
                  </th>
                  <th
                    class="text-left py-2 px-3 font-medium text-gray-400 dark:text-gray-500"
                  >
                    Message
                  </th>
                  <th
                    class="text-left py-2 px-3 font-medium text-gray-400 dark:text-gray-500 w-32"
                  >
                    Valeur
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="err in paginatedErrors"
                  :key="err.id"
                  class="border-b border-gray-50 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  <td
                    class="py-2 px-3 font-mono text-gray-400 dark:text-gray-500"
                  >
                    {{ err.timestamp }}
                  </td>
                  <td class="py-2 px-3">
                    <span
                      class="px-2 py-0.5 rounded-full font-medium"
                      :class="severityClass(err.severity)"
                      >{{ severityLabel(err.severity) }}</span
                    >
                  </td>
                  <td class="py-2 px-3">
                    <span
                      class="px-2 py-0.5 rounded-full"
                      :class="ifaceClass(err.iface)"
                      >{{ err.iface }}</span
                    >
                  </td>
                  <td class="py-2 px-3 text-gray-700 dark:text-gray-200">
                    {{ err.message }}
                  </td>
                  <td
                    class="py-2 px-3 font-mono text-gray-400 dark:text-gray-500"
                  >
                    {{ err.value }}
                  </td>
                </tr>
                <tr v-if="paginatedErrors.length === 0">
                  <td
                    colspan="5"
                    class="py-8 text-center text-gray-400 dark:text-gray-500"
                  >
                    <i
                      class="ti ti-check text-green-500 text-lg block mb-1"
                    ></i>
                    Aucune erreur trouvée
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Pagination -->
          <div
            class="flex items-center justify-between pt-3 border-t border-gray-100 dark:border-gray-700 mt-2"
          >
            <span class="text-xs text-gray-400 dark:text-gray-500">
              Affichage {{ paginationStart }}–{{ paginationEnd }} sur
              {{ filteredErrors.length }} erreurs
            </span>
            <div class="flex gap-2 items-center">
              <button
                class="text-xs px-2 py-1 rounded border border-gray-200 dark:border-gray-600 text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-40"
                :disabled="currentPage === 1"
                @click="currentPage = 1"
              >
                «
              </button>
              <button
                class="text-xs px-3 py-1 rounded border border-gray-200 dark:border-gray-600 text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-40"
                :disabled="currentPage === 1"
                @click="currentPage--"
              >
                ← Préc.
              </button>
              <span class="text-xs text-gray-400 dark:text-gray-500"
                >{{ currentPage }} / {{ totalPages }}</span
              >
              <button
                class="text-xs px-3 py-1 rounded border border-gray-200 dark:border-gray-600 text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-40"
                :disabled="currentPage >= totalPages"
                @click="currentPage++"
              >
                Suiv. →
              </button>
              <button
                class="text-xs px-2 py-1 rounded border border-gray-200 dark:border-gray-600 text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-40"
                :disabled="currentPage >= totalPages"
                @click="currentPage = totalPages"
              >
                »
              </button>
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

// ── Filtres ──────────────────────────────────────────
const activeSeverity = ref("all");
const activeIface = ref("all");
const search = ref("");
const currentPage = ref(1);
const perPage = 8;

const severityFilters = [
  {
    value: "all",
    label: "Tous",
    activeClass:
      "bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200 border-gray-300 dark:border-gray-500",
  },
  {
    value: "critical",
    label: "Critique",
    activeClass:
      "bg-red-50 dark:bg-red-900 text-red-700 dark:text-red-300 border-red-300 dark:border-red-700",
  },
  {
    value: "warn",
    label: "Avertissement",
    activeClass:
      "bg-amber-50 dark:bg-amber-900 text-amber-700 dark:text-amber-300 border-amber-300 dark:border-amber-700",
  },
  {
    value: "info",
    label: "Info",
    activeClass:
      "bg-blue-50 dark:bg-blue-900 text-blue-700 dark:text-blue-300 border-blue-300 dark:border-blue-700",
  },
];

const ifaceFilters = computed(() => {
  const filters = [{ value: "all", label: "Toutes" }];
  store.interfaces
    .filter((i) => i.monitored)
    .forEach((iface) => {
      filters.push({ value: iface.name, label: iface.name });
    });
  return filters;
});

// ── Erreurs filtrées ─────────────────────────────────
const filteredErrors = computed(() => {
  return store.errors.filter((e) => {
    const matchSev =
      activeSeverity.value === "all" || e.severity === activeSeverity.value;
    const matchIface =
      activeIface.value === "all" || e.iface === activeIface.value;
    const matchSearch =
      !search.value ||
      e.message.toLowerCase().includes(search.value.toLowerCase()) ||
      e.value.toLowerCase().includes(search.value.toLowerCase());
    return matchSev && matchIface && matchSearch;
  });
});

// ── Pagination ───────────────────────────────────────
const totalPages = computed(() =>
  Math.max(1, Math.ceil(filteredErrors.value.length / perPage)),
);
const paginationStart = computed(() =>
  filteredErrors.value.length === 0 ? 0 : (currentPage.value - 1) * perPage + 1,
);
const paginationEnd = computed(() =>
  Math.min(currentPage.value * perPage, filteredErrors.value.length),
);
const paginatedErrors = computed(() =>
  filteredErrors.value.slice(
    (currentPage.value - 1) * perPage,
    currentPage.value * perPage,
  ),
);

// ── KPI ──────────────────────────────────────────────
const criticalCount = computed(
  () => store.errors.filter((e) => e.severity === "critical").length,
);
const warnCount = computed(
  () => store.errors.filter((e) => e.severity === "warn").length,
);

const monitoredInterfaces = computed(() =>
  store.interfaces.filter((i) => i.monitored).map((i) => i.name),
);

const totalPacketLoss = computed(() => {
  const sum = monitoredInterfaces.value.reduce((acc, name) => {
    const lat = store.latency[name];
    return acc + (lat ? lat.packet_loss_pct : 0);
  }, 0);
  return Math.round(sum * 10);
});

const avgErrorRate = computed(() => {
  if (monitoredInterfaces.value.length === 0) return "0.0";
  const sum = monitoredInterfaces.value.reduce((acc, name) => {
    const lat = store.latency[name];
    return acc + (lat ? lat.packet_loss_pct : 0);
  }, 0);
  return (sum / monitoredInterfaces.value.length).toFixed(1);
});

// ── Helpers badge ────────────────────────────────────
function severityClass(s) {
  if (s === "critical")
    return "bg-red-50 dark:bg-red-900 text-red-700 dark:text-red-300";
  if (s === "warn")
    return "bg-amber-50 dark:bg-amber-900 text-amber-700 dark:text-amber-300";
  return "bg-blue-50 dark:bg-blue-900 text-blue-700 dark:text-blue-300";
}
function severityLabel(s) {
  if (s === "critical") return "Critique";
  if (s === "warn") return "Avertiss.";
  return "Info";
}
function ifaceClass(i) {
  if (i && i.includes("w"))
    return "bg-green-50 dark:bg-green-900 text-green-700 dark:text-green-300";
  if (i && i.includes("e"))
    return "bg-purple-50 dark:bg-purple-900 text-purple-700 dark:text-purple-300";
  return "bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400";
}

// ── Histogramme ──────────────────────────────────────
const histoOptions = computed(() => ({
  chart: {
    toolbar: { show: false },
    background: "transparent",
    stacked: true,
    foreColor: isDark.value ? "#9CA3AF" : "#6B7280",
  },
  plotOptions: { bar: { columnWidth: "70%", borderRadius: 2 } },
  colors: ["#EF4444", "#FBBF24"],
  xaxis: {
    categories: [
      "-60m",
      "-55m",
      "-50m",
      "-45m",
      "-40m",
      "-35m",
      "-30m",
      "-25m",
      "-20m",
      "-15m",
      "-10m",
      "-5m",
      "now",
    ],
    labels: { style: { fontSize: "9px" } },
    axisBorder: { show: false },
    axisTicks: { show: false },
  },
  yaxis: { labels: { style: { fontSize: "9px" } } },
  grid: {
    borderColor: isDark.value ? "#374151" : "#F3F4F6",
    strokeDashArray: 4,
  },
  legend: { show: false },
  tooltip: { theme: isDark.value ? "dark" : "light" },
  dataLabels: { enabled: false },
}));

const histoSeries = computed(() => {
  const critBuckets = Array(13).fill(0);
  const warnBuckets = Array(13).fill(0);
  const now = Date.now();
  store.errors.forEach((e) => {
    const diff = now - new Date(`1970-01-01 ${e.timestamp}`).getTime();
    const bucket = Math.min(12, Math.floor(Math.abs(diff) / (5 * 60 * 1000)));
    const idx = 12 - bucket;
    if (idx >= 0) {
      if (e.severity === "critical") critBuckets[idx]++;
      if (e.severity === "warn") warnBuckets[idx]++;
    }
  });
  return [
    { name: "Critique", data: critBuckets },
    { name: "Avertissement", data: warnBuckets },
  ];
});

// ── Export CSV ───────────────────────────────────────
function exportCsv() {
  const headers = ["Horodatage", "Sévérité", "Interface", "Message", "Valeur"];
  const rows = store.errors.map((e) =>
    [e.timestamp, e.severity, e.iface, e.message, e.value].join(","),
  );
  const csv = [headers.join(","), ...rows].join("\n");
  const blob = new Blob([csv], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `erreurs_${new Date().toISOString().slice(0, 10)}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}
</script>
