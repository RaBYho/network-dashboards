<template>
  <div class="flex flex-col h-full bg-gray-50">

    <!-- Topbar -->
    <div class="flex items-center justify-between px-5 py-3 bg-white border-b border-gray-200">
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
            :class="activePeriod === p.value
              ? 'bg-blue-50 text-blue-700 border-blue-300'
              : 'border-gray-200 text-gray-500 hover:bg-gray-50'"
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
          sub="eth0 + wlan0"
          icon="ti-arrow-down"
          value-class="text-blue-600"
        />
        <KpiCard
          label="Upload total"
          :value="store.totalUpload.toFixed(1)"
          unit="Mbps"
          sub="eth0 + wlan0"
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
          <span class="text-xs font-medium text-gray-500 flex items-center gap-1">
            <i class="ti ti-chart-line"></i>
            Débit en temps réel — eth0 &amp; wlan0
          </span>
          <div class="flex gap-4 text-xs text-gray-400">
            <span><span class="inline-block w-3 h-0.5 bg-blue-500 align-middle mr-1"></span>eth0 ↓</span>
            <span><span class="inline-block w-3 h-0.5 bg-blue-300 align-middle mr-1" style="border-top: 2px dashed #93C5FD"></span>eth0 ↑</span>
            <span><span class="inline-block w-3 h-0.5 bg-green-500 align-middle mr-1"></span>wlan0 ↓</span>
            <span><span class="inline-block w-3 h-0.5 bg-green-300 align-middle mr-1" style="border-top: 2px dashed #86EFAC"></span>wlan0 ↑</span>
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
      <div class="grid grid-cols-2 gap-3">

        <div class="bg-white border border-gray-200 rounded-lg p-4">
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center gap-2">
              <span class="w-2 h-2 rounded-full bg-green-500"></span>
              <span class="text-xs font-medium px-2 py-0.5 rounded-full bg-blue-50 text-blue-700">eth0</span>
              <span class="text-xs text-gray-400">Filaire</span>
            </div>
          </div>
          <div class="space-y-2">
            <div>
              <div class="flex justify-between text-xs mb-1">
                <span class="text-gray-500"><i class="ti ti-arrow-down text-xs"></i> Download</span>
                <span class="font-medium text-blue-600">{{ store.bandwidth.eth0.download_Mbps.toFixed(1) }} Mbps</span>
              </div>
              <div class="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                <div class="h-full bg-blue-500 rounded-full transition-all duration-500"
                  :style="`width: ${Math.min((store.bandwidth.eth0.download_Mbps / 1000) * 100, 100)}%`"></div>
              </div>
            </div>
            <div>
              <div class="flex justify-between text-xs mb-1">
                <span class="text-gray-500"><i class="ti ti-arrow-up text-xs"></i> Upload</span>
                <span class="font-medium text-blue-600">{{ store.bandwidth.eth0.upload_Mbps.toFixed(1) }} Mbps</span>
              </div>
              <div class="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                <div class="h-full bg-blue-300 rounded-full transition-all duration-500"
                  :style="`width: ${Math.min((store.bandwidth.eth0.upload_Mbps / 1000) * 100, 100)}%`"></div>
              </div>
            </div>
            <div class="pt-2 border-t border-gray-100 grid grid-cols-2 gap-2">
              <div class="text-xs">
                <div class="text-gray-400">Total reçu</div>
                <div class="font-medium text-gray-700">{{ eth0Received }} Mo</div>
              </div>
              <div class="text-xs">
                <div class="text-gray-400">Total envoyé</div>
                <div class="font-medium text-gray-700">{{ eth0Sent }} Mo</div>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white border border-gray-200 rounded-lg p-4">
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center gap-2">
              <span class="w-2 h-2 rounded-full bg-green-500"></span>
              <span class="text-xs font-medium px-2 py-0.5 rounded-full bg-green-50 text-green-700">wlan0</span>
              <span class="text-xs text-gray-400">Wi-Fi</span>
            </div>
          </div>
          <div class="space-y-2">
            <div>
              <div class="flex justify-between text-xs mb-1">
                <span class="text-gray-500"><i class="ti ti-arrow-down text-xs"></i> Download</span>
                <span class="font-medium text-green-600">{{ store.bandwidth.wlan0.download_Mbps.toFixed(1) }} Mbps</span>
              </div>
              <div class="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                <div class="h-full bg-green-500 rounded-full transition-all duration-500"
                  :style="`width: ${Math.min((store.bandwidth.wlan0.download_Mbps / 300) * 100, 100)}%`"></div>
              </div>
            </div>
            <div>
              <div class="flex justify-between text-xs mb-1">
                <span class="text-gray-500"><i class="ti ti-arrow-up text-xs"></i> Upload</span>
                <span class="font-medium text-green-600">{{ store.bandwidth.wlan0.upload_Mbps.toFixed(1) }} Mbps</span>
              </div>
              <div class="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                <div class="h-full bg-green-300 rounded-full transition-all duration-500"
                  :style="`width: ${Math.min((store.bandwidth.wlan0.upload_Mbps / 300) * 100, 100)}%`"></div>
              </div>
            </div>
            <div class="pt-2 border-t border-gray-100 grid grid-cols-2 gap-2">
              <div class="text-xs">
                <div class="text-gray-400">Total reçu</div>
                <div class="font-medium text-gray-700">{{ wlan0Received }} Mo</div>
              </div>
              <div class="text-xs">
                <div class="text-gray-400">Total envoyé</div>
                <div class="font-medium text-gray-700">{{ wlan0Sent }} Mo</div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useNetworkStore } from '../stores/networkStore'
import KpiCard from '../components/layout/KpiCard.vue'

const store = useNetworkStore()

// ── Sélecteur de période ─────────────────────────────
const periods = [
  { label: '1 min', value: '1m' },
  { label: '1 h',   value: '1h' },
  { label: '24 h',  value: '24h' },
]
const activePeriod = ref('1m')

// ── KPI calculés ─────────────────────────────────────
const peakDownload = computed(() => {
  const all = [
    ...store.history.eth0.download,
    ...store.history.wlan0.download,
  ]
  return all.length ? Math.max(...all) : 0
})

const peakAgo = computed(() => {
  const all = [...store.history.eth0.download]
  if (!all.length) return 0
  const idx = all.indexOf(Math.max(...all))
  return all.length - 1 - idx
})

const totalTransferred = computed(() => {
  const dl = [...store.history.eth0.download, ...store.history.wlan0.download]
  const ul = [...store.history.eth0.upload,   ...store.history.wlan0.upload]
  const sum = [...dl, ...ul].reduce((a, b) => a + b, 0)
  return (sum * store.interval / 8).toFixed(0)
})

// Totaux cumulés par interface (simulés depuis l'historique)
const eth0Received  = computed(() => (store.history.eth0.download.reduce((a, b) => a + b, 0) * store.interval / 8).toFixed(0))
const eth0Sent      = computed(() => (store.history.eth0.upload.reduce((a, b)   => a + b, 0) * store.interval / 8).toFixed(0))
const wlan0Received = computed(() => (store.history.wlan0.download.reduce((a, b) => a + b, 0) * store.interval / 8).toFixed(0))
const wlan0Sent     = computed(() => (store.history.wlan0.upload.reduce((a, b)   => a + b, 0) * store.interval / 8).toFixed(0))

// ── Options ApexCharts ───────────────────────────────
const chartOptions = computed(() => ({
  chart: {
    toolbar: { show: false },
    animations: { enabled: true, easing: 'linear', dynamicAnimation: { speed: 1000 } },
    background: 'transparent',
  },
  stroke: {
    curve: 'smooth',
    width: [2, 1.5, 2, 1.5],
    dashArray: [0, 5, 0, 5],
  },
  colors: ['#3B82F6', '#93C5FD', '#22C55E', '#86EFAC'],
  xaxis: {
    categories: store.history.eth0.timestamps,
    labels: { style: { fontSize: '10px', colors: '#9CA3AF' } },
    axisBorder: { show: false },
    axisTicks:  { show: false },
  },
  yaxis: {
    labels: {
      style: { fontSize: '10px', colors: '#9CA3AF' },
      formatter: v => v.toFixed(0) + 'M',
    },
  },
  grid:    { borderColor: '#F3F4F6', strokeDashArray: 4 },
  legend:  { show: false },
  tooltip: {
    theme: 'light',
    y: { formatter: v => v.toFixed(2) + ' Mbps' },
  },
  annotations: activePeriod.value !== '1m' ? {} : {},
}))

const series = computed(() => [
  { name: 'eth0 ↓',  data: store.history.eth0.download  },
  { name: 'eth0 ↑',  data: store.history.eth0.upload    },
  { name: 'wlan0 ↓', data: store.history.wlan0.download },
  { name: 'wlan0 ↑', data: store.history.wlan0.upload   },
])
</script>