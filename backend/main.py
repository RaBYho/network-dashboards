from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Données simulées modifiables ─────────────────────
# Change ces valeurs pour tester le frontend !
DATA = {
    "eth0": {
        "download_Mbps": 42.3,
        "upload_Mbps":   7.8,
        "latency": {
            "avg_ms":          14.0,
            "min_ms":          10.0,
            "max_ms":          34.0,
            "jitter_ms":        2.1,
            "packet_loss_pct":  0.0,
        }
    },
    "wlan0": {
        "download_Mbps": 8.7,
        "upload_Mbps":   2.6,
        "latency": {
            "avg_ms":          38.0,
            "min_ms":          20.0,
            "max_ms":          72.0,
            "jitter_ms":        9.4,
            "packet_loss_pct":  2.0,
        }
    }
}

# ── Helper : légère variation aléatoire ─────────────
def vary(val, pct=0.05):
    """Ajoute ±5% de variation pour simuler du temps réel."""
    delta = val * pct
    return round(random.uniform(val - delta, val + delta), 3)

# ── Endpoints ────────────────────────────────────────

@app.get("/api/interfaces")
def get_interfaces():
    return [
        { "name": "eth0",  "up": True  },
        { "name": "wlan0", "up": True  },
    ]

@app.get("/api/bandwidth")
def get_bandwidth(interface: str = "eth0"):
    if interface not in DATA:
        return { "error": f"Interface {interface} inconnue" }
    d = DATA[interface]
    return {
        "download_Mbps": vary(d["download_Mbps"]),
        "upload_Mbps":   vary(d["upload_Mbps"]),
        "timestamp":     time.time(),
    }

@app.get("/api/latency")
def get_latency(interface: str = "eth0", host: str = "8.8.8.8"):
    if interface not in DATA:
        return { "error": f"Interface {interface} inconnue" }
    lat = DATA[interface]["latency"]
    return {
        "host":             host,
        "avg_ms":           vary(lat["avg_ms"],          pct=0.1),
        "min_ms":           vary(lat["min_ms"],          pct=0.05),
        "max_ms":           vary(lat["max_ms"],          pct=0.05),
        "jitter_ms":        vary(lat["jitter_ms"],       pct=0.15),
        "packet_loss_pct":  vary(lat["packet_loss_pct"], pct=0.2),
        "timestamp":        time.time(),
    }

@app.get("/api/metrics")
def get_all_metrics():
    """Toutes les métriques en un seul appel."""
    return {
        iface: {
            "bandwidth": {
                "download_Mbps": vary(DATA[iface]["download_Mbps"]),
                "upload_Mbps":   vary(DATA[iface]["upload_Mbps"]),
            },
            "latency": {
                k: vary(v, pct=0.1) if isinstance(v, float) else v
                for k, v in DATA[iface]["latency"].items()
            }
        }
        for iface in DATA
    }