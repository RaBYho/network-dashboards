import { defineStore } from "pinia";
import { ref, computed } from "vue";
import axios from "axios";

export const useNetworkStore = defineStore("network", () => {
  const apiUrl = ref("http://localhost:8000");
  const interval = ref(2);
  const connected = ref(false);

  const interfaces = ref([]);

  async function fetchInterfaces() {
    try {
      const res = await axios.get(`${apiUrl.value}/api/interfaces`, {
        timeout: 8000,
      });
      interfaces.value = res.data.map((iface) => ({
        name: iface.name,
        icon:
          iface.name.toLowerCase().includes("wlan") ||
          iface.name.toLowerCase().includes("wi")
            ? "ti-wifi"
            : "ti-network",
        up: iface.up,
        mtu: iface.mtu,
        gateway: iface.gateway || "",
        monitored: iface.up,
        ipv4: iface.ipv4 || "",
        netmask: iface.netmask || "",
        mac: iface.mac || "",
        ipv6: iface.ipv6 || "",
      }));
    } catch {
      interfaces.value = [];
    }
  }

  // ── Refresh périodique (préserve monitored et les nouveaux champs) ──
  async function refreshInterfaces() {
    try {
      const res = await axios.get(`${apiUrl.value}/api/interfaces`, {
        timeout: 5000,
      });
      const freshList = res.data;
      const newInterfaces = freshList.map((iface) => {
        const existing = interfaces.value.find((i) => i.name === iface.name);
        return {
          name: iface.name,
          icon:
            iface.name.toLowerCase().includes("wlan") ||
            iface.name.toLowerCase().includes("wi")
              ? "ti-wifi"
              : "ti-network",
          up: iface.up,
          mtu: iface.mtu, // conservé
          gateway: iface.gateway || "", // conservé
          monitored: existing ? existing.monitored : iface.up,
          ipv4: iface.ipv4 || "",
          netmask: iface.netmask || "",
          mac: iface.mac || "",
          ipv6: iface.ipv6 || "",
        };
      });
      interfaces.value = newInterfaces;
    } catch {
      // silencieux
    }
  }

  let _interfaceTimer = null;
  function startInterfaceRefresh() {
    refreshInterfaces();
    if (_interfaceTimer) clearInterval(_interfaceTimer);
    _interfaceTimer = setInterval(refreshInterfaces, 10000);
  }
  function stopInterfaceRefresh() {
    clearInterval(_interfaceTimer);
    _interfaceTimer = null;
  }

  // ── Métriques temps réel ─────────────────────────────
  const bandwidth = ref({});
  const latency = ref({});

  const history = ref({});
  const MAX_POINTS = 60;

  function initHistory(ifaceName) {
    if (!history.value[ifaceName]) {
      history.value[ifaceName] = {
        download: [],
        upload: [],
        rtt: [],
        timestamps: [],
      };
    }
  }

  function pushHistory(ifaceName, bw, lat) {
    initHistory(ifaceName);
    const h = history.value[ifaceName];
    const now = new Date().toLocaleTimeString();
    h.download.push(Number(bw.download_Mbps) || 0);
    h.upload.push(Number(bw.upload_Mbps) || 0);
    h.rtt.push(Number(lat.avg_ms) || 0);
    h.timestamps.push(now);
    if (h.download.length > MAX_POINTS) {
      h.download.shift();
      h.upload.shift();
      h.rtt.shift();
      h.timestamps.shift();
    }
  }

  // ── Seuils & ping ──────────────────────────────────
  const thresholds = ref({
    latency_ms: 50,
    packet_loss_pct: 10,
    jitter_ms: 20,
    error_rate_pct: 5,
  });
  const pingTargets = ref(["8.8.8.8", "1.1.1.1", "192.168.1.1"]);
  const errors = ref([]);

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

  function checkThresholds() {
    for (const iface of getMonitoredInterfaces()) {
      const lat = latency.value[iface];
      if (!lat) continue;
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

  // ── Connexions TCP ──────────────────────────────────
  const connections = ref({});

  async function fetchConnections() {
    try {
      // Appeler l'API sans paramètre pour obtenir les stats globales
      const res = await axios.get(`${apiUrl.value}/api/connections`, {
        timeout: 5000,
      });
      if (res.data) {
        connections.value["global"] = {
          total: res.data.total || 0,
          states: res.data.states || {},
        };
      }
    } catch {
      // silencieux
    }
  }

  let _connectionsTimer = null;
  function startConnectionsRefresh() {
    fetchConnections();
    if (_connectionsTimer) clearInterval(_connectionsTimer);
    _connectionsTimer = setInterval(fetchConnections, 5000);
  }
  function stopConnectionsRefresh() {
    clearInterval(_connectionsTimer);
    _connectionsTimer = null;
  }

  // ── Polling principal ───────────────────────────────
  let _timer = null;

  function getMonitoredInterfaces() {
    return interfaces.value.filter((i) => i.monitored).map((i) => i.name);
  }

  async function fetchMetrics() {
    const monitored = getMonitoredInterfaces();
    if (monitored.length === 0) {
      connected.value = false;
      return;
    }

    const bandwidthPromises = monitored.map((iface) =>
      axios
        .get(`${apiUrl.value}/api/bandwidth?interface=${iface}`, {
          timeout: 8000,
        })
        .catch(() => null),
    );
    const latencyPromises = monitored.map((iface) =>
      axios
        .get(`${apiUrl.value}/api/latency?interface=${iface}&host=8.8.8.8`, {
          timeout: 8000,
        })
        .catch(() => null),
    );

    const bwResults = await Promise.allSettled(bandwidthPromises);
    const latResults = await Promise.allSettled(latencyPromises);

    let anySuccess = false;

    monitored.forEach((iface, idx) => {
      if (bwResults[idx].status === "fulfilled" && bwResults[idx].value) {
        const data = bwResults[idx].value.data;
        bandwidth.value[iface] = {
          download_Mbps: Number(data.download_Mbps) || 0,
          upload_Mbps: Number(data.upload_Mbps) || 0,
          bytes_recv: Number(data.bytes_recv) || 0,
          bytes_sent: Number(data.bytes_sent) || 0,
        };
        anySuccess = true;
      } else if (!bandwidth.value[iface]) {
        bandwidth.value[iface] = {
          download_Mbps: 0,
          upload_Mbps: 0,
          bytes_recv: 0,
          bytes_sent: 0,
        };
      }
    });

    monitored.forEach((iface, idx) => {
      if (latResults[idx].status === "fulfilled" && latResults[idx].value) {
        const data = latResults[idx].value.data;
        latency.value[iface] = {
          avg_ms: Number(data.avg_ms) || 0,
          min_ms: Number(data.min_ms) || 0,
          max_ms: Number(data.max_ms) || 0,
          jitter_ms: Number(data.jitter_ms) || 0,
          packet_loss_pct: Number(data.packet_loss_pct) || 0,
        };
        anySuccess = true;
      } else if (!latency.value[iface]) {
        latency.value[iface] = {
          avg_ms: 0,
          min_ms: 0,
          max_ms: 0,
          jitter_ms: 0,
          packet_loss_pct: 0,
        };
      }
    });

    monitored.forEach((iface) => {
      const bw = bandwidth.value[iface] || { download_Mbps: 0, upload_Mbps: 0 };
      const lat = latency.value[iface] || { avg_ms: 0 };
      pushHistory(iface, bw, lat);
    });

    if (!anySuccess) {
      monitored.forEach((iface) => {
        bandwidth.value[iface] = {
          download_Mbps: 0,
          upload_Mbps: 0,
          bytes_recv: bandwidth.value[iface]?.bytes_recv || 0,
          bytes_sent: bandwidth.value[iface]?.bytes_sent || 0,
        };
        latency.value[iface] = {
          avg_ms: 0,
          min_ms: 0,
          max_ms: 0,
          jitter_ms: 0,
          packet_loss_pct: 0,
        };
      });
    }

    connected.value = anySuccess;
    checkThresholds();

    if (anySuccess && !sessionStarted.value) {
      initSessionCounters();
    }
  }

  function startPolling() {
    fetchMetrics();
    if (_timer) clearInterval(_timer);
    _timer = setInterval(fetchMetrics, interval.value * 1000);
    startInterfaceRefresh();
    startConnectionsRefresh(); // ← ajouté
  }

  function stopPolling() {
    clearInterval(_timer);
    _timer = null;
    stopInterfaceRefresh();
    stopConnectionsRefresh(); // ← ajouté
  }

  function setInterval_(val) {
    interval.value = val;
    if (_timer) {
      stopPolling();
      startPolling();
    }
  }

  // ── Compteurs cumulatifs par session ───────────────
  const sessionCounters = ref({});
  const sessionStarted = ref(false);

  function initSessionCounters() {
    if (sessionStarted.value) return;
    const monitored = getMonitoredInterfaces();
    monitored.forEach((iface) => {
      const bw = bandwidth.value[iface];
      if (bw && bw.bytes_recv !== undefined) {
        sessionCounters.value[iface] = {
          bytes_recv: bw.bytes_recv,
          bytes_sent: bw.bytes_sent,
        };
      }
    });
    sessionStarted.value = true;
  }

  function resetSession() {
    sessionCounters.value = {};
    sessionStarted.value = false;
  }

  function getInterfaceTotal(ifaceName) {
    const bw = bandwidth.value[ifaceName];
    const session = sessionCounters.value[ifaceName];
    if (!bw || !session) return { received: 0, sent: 0 };
    return {
      received: bw.bytes_recv - session.bytes_recv,
      sent: bw.bytes_sent - session.bytes_sent,
    };
  }

  // ── Thème ───────────────────────────────────────────
  const theme = ref("light");
  function applyTheme(val) {
    theme.value = val;
    const root = document.documentElement;
    root.classList.remove("dark");
    if (val === "dark") {
      root.classList.add("dark");
      root.setAttribute("data-theme", "dark");
    } else if (val === "light") {
      root.setAttribute("data-theme", "light");
    } else {
      if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
        root.classList.add("dark");
        root.setAttribute("data-theme", "dark");
      } else {
        root.setAttribute("data-theme", "light");
      }
    }
  }

  // ── Getters globaux ────────────────────────────────
  const totalDownload = computed(() =>
    Object.values(bandwidth.value).reduce(
      (sum, b) => sum + (b.download_Mbps || 0),
      0,
    ),
  );
  const totalUpload = computed(() =>
    Object.values(bandwidth.value).reduce(
      (sum, b) => sum + (b.upload_Mbps || 0),
      0,
    ),
  );

  // ── Retour ──────────────────────────────────────────
  return {
    apiUrl,
    interval,
    connected,
    interfaces,
    bandwidth,
    latency,
    history,
    thresholds,
    pingTargets,
    errors,
    totalDownload,
    totalUpload,
    connections,
    startPolling,
    stopPolling,
    setInterval_,
    addError,
    fetchMetrics,
    applyTheme,
    fetchInterfaces,
    getInterfaceTotal,
    resetSession,
    fetchConnections,
    refreshInterfaces,
    startInterfaceRefresh,
    stopInterfaceRefresh,
  };
});
