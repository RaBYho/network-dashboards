import { defineStore } from "pinia";
import { ref, computed } from "vue";
import axios from "axios";

export const useNetworkStore = defineStore("network", () => {
  // ── Config ──────────────────────────────────────────
  const apiUrl = ref("http://localhost:8000");
  const interval = ref(2); // secondes
  const connected = ref(false);

  // ── Interfaces détectées ────────────────────────────
  const interfaces = ref([
    { name: "eth0", icon: "ti-network", up: true },
    { name: "wlan0", icon: "ti-wifi", up: true },
  ]);

  // ── Métriques temps réel ────────────────────────────
  const bandwidth = ref({
    eth0: { download_Mbps: 0, upload_Mbps: 0 },
    wlan0: { download_Mbps: 0, upload_Mbps: 0 },
  });

  const latency = ref({
    eth0: { avg_ms: 0, min_ms: 0, max_ms: 0, jitter_ms: 0, packet_loss_pct: 0 },
    wlan0: {
      avg_ms: 0,
      min_ms: 0,
      max_ms: 0,
      jitter_ms: 0,
      packet_loss_pct: 0,
    },
  });

  const errors = ref([]); // journal des erreurs

  // ── Historique pour les graphiques (60 points max) ──
  const history = ref({
    eth0: { download: [], upload: [], rtt: [], timestamps: [] },
    wlan0: { download: [], upload: [], rtt: [], timestamps: [] },
  });

  const MAX_POINTS = 60;

  function pushHistory(iface, bw, lat) {
    const h = history.value[iface];
    const now = new Date().toLocaleTimeString();
    h.download.push(bw.download_Mbps);
    h.upload.push(bw.upload_Mbps);
    h.rtt.push(lat.avg_ms);
    h.timestamps.push(now);
    if (h.download.length > MAX_POINTS) {
      h.download.shift();
      h.upload.shift();
      h.rtt.shift();
      h.timestamps.shift();
    }
  }

  // ── Seuils d'alerte ─────────────────────────────────
  const thresholds = ref({
    latency_ms: 50,
    packet_loss_pct: 10,
    jitter_ms: 20,
    error_rate_pct: 5,
  });

  // ── Paramètres ping ─────────────────────────────────
  const pingTargets = ref(["8.8.8.8", "1.1.1.1", "192.168.1.1"]);

  // ── Polling ─────────────────────────────────────────
  let _timer = null;

  async function fetchMetrics() {
    try {
      // Ces endpoints seront fournis par ton équipier
      const [bwEth, bwWlan, latEth, latWlan] = await Promise.all([
        axios.get(`${apiUrl.value}/api/bandwidth?interface=eth0`),
        axios.get(`${apiUrl.value}/api/bandwidth?interface=wlan0`),
        axios.get(`${apiUrl.value}/api/latency?host=8.8.8.8`),
        axios.get(`${apiUrl.value}/api/latency?host=8.8.8.8`),
      ]);

      bandwidth.value.eth0 = bwEth.data;
      bandwidth.value.wlan0 = bwWlan.data;
      latency.value.eth0 = latEth.data;
      latency.value.wlan0 = latWlan.data;

      pushHistory("eth0", bwEth.data, latEth.data);
      pushHistory("wlan0", bwWlan.data, latWlan.data);

      connected.value = true;
      checkThresholds();
    } catch {
      connected.value = false;
    }
  }

  function checkThresholds() {
    const now = new Date().toLocaleTimeString();
    for (const iface of ["eth0", "wlan0"]) {
      const lat = latency.value[iface];
      if (lat.avg_ms > thresholds.value.latency_ms) {
        addError(
          "warn",
          iface,
          "Latence élevée",
          `${lat.avg_ms}ms > seuil ${thresholds.value.latency_ms}ms`,
        );
      }
      if (lat.packet_loss_pct > thresholds.value.packet_loss_pct) {
        addError(
          "critical",
          iface,
          "Perte de paquets élevée",
          `${lat.packet_loss_pct}% > seuil ${thresholds.value.packet_loss_pct}%`,
        );
      }
    }
  }

  function addError(severity, iface, message, value) {
    errors.value.unshift({
      id: Date.now(),
      timestamp: new Date().toLocaleTimeString(),
      severity,
      iface,
      message,
      value,
    });
    if (errors.value.length > 200) errors.value.pop();
  }

  function startPolling() {
    fetchMetrics();
    _timer = setInterval(fetchMetrics, interval.value * 1000);
  }

  function stopPolling() {
    clearInterval(_timer);
  }

  function setInterval_(val) {
    interval.value = val;
    stopPolling();
    startPolling();
  }

  // ── Getters ─────────────────────────────────────────
  const totalDownload = computed(
    () =>
      bandwidth.value.eth0.download_Mbps + bandwidth.value.wlan0.download_Mbps,
  );
  const totalUpload = computed(
    () => bandwidth.value.eth0.upload_Mbps + bandwidth.value.wlan0.upload_Mbps,
  );

  return {
    apiUrl,
    interval,
    connected,
    interfaces,
    bandwidth,
    latency,
    errors,
    history,
    thresholds,
    pingTargets,
    totalDownload,
    totalUpload,
    startPolling,
    stopPolling,
    setInterval_,
    addError,
    fetchMetrics,
  };
});
