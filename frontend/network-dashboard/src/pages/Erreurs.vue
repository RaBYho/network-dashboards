<template>
  <div class="flex flex-col h-full bg-gray-50">
    <!-- Topbar -->
    <div
      class="flex items-center justify-between px-5 py-3 bg-white border-b border-gray-200"
    >
      <div class="flex items-center gap-2">
        <i class="ti ti-alert-triangle text-red-500 text-base"></i>
        <span class="text-sm font-medium text-gray-800"
          >Erreurs & anomalies</span
        >
      </div>
      <div class="flex items-center gap-2">
        <button
          class="text-xs px-3 py-1 rounded border border-gray-200 text-gray-500 hover:bg-gray-50 flex items-center gap-1"
          @click="exportCsv"
        >
          <i class="ti ti-download text-xs"></i> Export CSV
        </button>
        <button
          class="text-xs px-3 py-1 rounded border border-gray-200 text-gray-500 hover:bg-gray-50 flex items-center gap-1"
          @click="store.errors.splice(0)"
        >
          <i class="ti ti-trash text-xs"></i> Vider
        </button>
      </div>
    </div>

    <!-- Contenu -->
    <div class="flex-1 p-4 flex flex-col gap-3 overflow-auto">
      <!-- KPI row -->
      <div class="grid grid-cols-4 gap-3">
        <KpiCard
          label="Erreurs critiques"
          :value="criticalCount"
          unit=""
          sub="dernières 24h"
          icon="ti-circle-x"
          :value-class="criticalCount > 0 ? 'text-red-600' : 'text-green-600'"
        />
        <KpiCard
          label="Avertissements"
          :value="warnCount"
          unit=""
          sub="dernières 24h"
          icon="ti-alert-circle"
          :value-class="warnCount > 0 ? 'text-amber-500' : 'text-green-600'"
        />
        <KpiCard
          label="Paquets perdus"
          :value="totalPacketLoss"
          unit=""
          sub="total cumulé"
          icon="ti-packages"
          value-class="text-gray-800"
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

      <!-- Histogramme -->
      <div class="bg-white border border-gray-200 rounded-lg p-4">
        <div class="flex items-center justify-between mb-3">
          <span
            class="text-xs font-medium text-gray-500 flex items-center gap-1"
          >
            <i class="ti ti-chart-bar"></i>
            Fréquence des erreurs — dernière heure
          </span>
          <div class="flex gap-3 text-xs text-gray-400">
            <span
              ><span
                class="inline-block w-2 h-2 rounded-sm bg-red-500 align-middle mr-1"
              ></span
              >Critique</span
            >
            <span
              ><span
                class="inline-block w-2 h-2 rounded-sm bg-amber-400 align-middle mr-1"
              ></span
              >Avertissement</span
            >
          </div>
        </div>
        <apexchart
          type="bar"
          height="100"
          :options="histoOptions"
          :series="histoSeries"
        />
      </div>

      <!-- Journal -->
      <div class="flex-1 bg-white border border-gray-200 rounded-lg p-4">
        <div class="flex items-center justify-between mb-3">
          <span
            class="text-xs font-medium text-gray-500 flex items-center gap-1"
          >
            <i class="ti ti-list"></i> Journal des erreurs
          </span>
          <!-- Filtres -->
          <div class="flex items-center gap-2 flex-wrap">
            <button
              v-for="f in severityFilters"
              :key="f.value"
              class="text-xs px-3 py-1 rounded-full border transition-colors"
              :class="
                activeSeverity === f.value
                  ? f.activeClass
                  : 'border-gray-200 text-gray-500 hover:bg-gray-50'
              "
              @click="activeSeverity = f.value"
            >
              {{ f.label }}
            </button>
            <div class="w-px h-4 bg-gray-200"></div>
            <button
              v-for="f in ifaceFilters"
              :key="f.value"
              class="text-xs px-3 py-1 rounded-full border transition-colors"
              :class="
                activeIface === f.value
                  ? 'bg-gray-100 text-gray-700 border-gray-300'
                  : 'border-gray-200 text-gray-500 hover:bg-gray-50'
              "
              @click="activeIface = f.value"
            >
              {{ f.label }}
            </button>
            <div class="w-px h-4 bg-gray-200"></div>
            <input
              v-model="search"
              type="text"
              placeholder="Rechercher..."
              class="text-xs px-3 py-1 rounded border border-gray-200 bg-gray-50 text-gray-700 w-36 focus:outline-none focus:border-gray-300"
            />
          </div>
        </div>

        <!-- Table -->
        <div class="overflow-auto">
          <table class="w-full text-xs border-collapse">
            <thead>
              <tr class="border-b border-gray-100 bg-gray-50">
                <th class="text-left py-2 px-3 font-medium text-gray-400 w-32">
                  Horodatage
                </th>
                <th class="text-left py-2 px-3 font-medium text-gray-400 w-24">
                  Sévérité
                </th>
                <th class="text-left py-2 px-3 font-medium text-gray-400 w-20">
                  Interface
                </th>
                <th class="text-left py-2 px-3 font-medium text-gray-400">
                  Message
                </th>
                <th class="text-left py-2 px-3 font-medium text-gray-400 w-32">
                  Valeur
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="err in paginatedErrors"
                :key="err.id"
                class="border-b border-gray-50 hover:bg-gray-50 transition-colors"
              >
                <td class="py-2 px-3 font-mono text-gray-400">
                  {{ err.timestamp }}
                </td>
                <td class="py-2 px-3">
                  <span
                    class="px-2 py-0.5 rounded-full font-medium"
                    :class="severityClass(err.severity)"
                  >
                    {{ severityLabel(err.severity) }}
                  </span>
                </td>
                <td class="py-2 px-3">
                  <span
                    class="px-2 py-0.5 rounded-full"
                    :class="ifaceClass(err.iface)"
                  >
                    {{ err.iface }}
                  </span>
                </td>
                <td class="py-2 px-3 text-gray-700">{{ err.message }}</td>
                <td class="py-2 px-3 font-mono text-gray-400">
                  {{ err.value }}
                </td>
              </tr>
              <tr v-if="paginatedErrors.length === 0">
                <td colspan="5" class="py-8 text-center text-gray-400">
                  <i class="ti ti-check text-green-500 text-lg block mb-1"></i>
                  Aucune erreur trouvée
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div
          class="flex items-center justify-between pt-3 border-t border-gray-100 mt-2"
        >
          <span class="text-xs text-gray-400">
            Affichage {{ paginationStart }}–{{ paginationEnd }} sur
            {{ filteredErrors.length }} erreurs
          </span>
          <div class="flex gap-2">
            <button
              class="text-xs px-3 py-1 rounded border border-gray-200 text-gray-500 hover:bg-gray-50 disabled:opacity-40"
              :disabled="currentPage === 1"
              @click="currentPage--"
            >
              ← Préc.
            </button>
            <button
              class="text-xs px-3 py-1 rounded border border-gray-200 text-gray-500 hover:bg-gray-50 disabled:opacity-40"
              :disabled="currentPage >= totalPages"
              @click="currentPage++"
            >
              Suiv. →
            </button>
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
    activeClass: "bg-gray-100 text-gray-700 border-gray-300",
  },
  {
    value: "critical",
    label: "Critique",
    activeClass: "bg-red-50 text-red-700 border-red-300",
  },
  {
    value: "warn",
    label: "Avertissement",
    activeClass: "bg-amber-50 text-amber-700 border-amber-300",
  },
  {
    value: "info",
    label: "Info",
    activeClass: "bg-blue-50 text-blue-700 border-blue-300",
  },
];

const ifaceFilters = computed(() => {
  const filters = [{ value: "all", label: "Toutes" }];
  // Ajouter les interfaces surveillées comme filtres
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

// ✅ Utiliser les interfaces surveillées pour agréger les pertes de paquets et le taux d'erreur
const monitoredInterfaces = computed(() =>
  store.interfaces.filter((i) => i.monitored).map((i) => i.name),
);

const totalPacketLoss = computed(() => {
  // Somme des paquets perdus (packet_loss_pct) pour toutes les interfaces surveillées
  // On peut considérer le taux de perte comme un indicateur ; on fait la somme des pourcentages pour avoir une idée du total
  // ou on prend la moyenne ? L'ancienne version faisait `(latency.eth0.packet_loss_pct + latency.wlan0.packet_loss_pct) * 10`
  // Nous allons faire la somme des pourcentages * 10 (arrondi) pour rester proche de l'ancien comportement
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
  if (s === "critical") return "bg-red-50 text-red-700";
  if (s === "warn") return "bg-amber-50 text-amber-700";
  return "bg-blue-50 text-blue-700";
}
function severityLabel(s) {
  if (s === "critical") return "Critique";
  if (s === "warn") return "Avertiss.";
  return "Info";
}
function ifaceClass(i) {
  // On peut utiliser les noms réels ; pour garder des couleurs cohérentes
  if (i && i.includes("w")) return "bg-green-50 text-green-700";
  if (i && i.includes("e")) return "bg-purple-50 text-purple-700";
  return "bg-gray-100 text-gray-500";
}

// ── Histogramme ──────────────────────────────────────
const histoOptions = computed(() => ({
  chart: {
    toolbar: { show: false },
    background: "transparent",
    stacked: true,
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
    labels: { style: { fontSize: "9px", colors: "#9CA3AF" } },
    axisBorder: { show: false },
    axisTicks: { show: false },
  },
  yaxis: {
    labels: { style: { fontSize: "9px", colors: "#9CA3AF" } },
  },
  grid: { borderColor: "#F3F4F6", strokeDashArray: 4 },
  legend: { show: false },
  tooltip: { theme: "light" },
  dataLabels: { enabled: false },
}));

const histoSeries = computed(() => {
  // Répartit les erreurs dans les 13 tranches de 5 minutes
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
