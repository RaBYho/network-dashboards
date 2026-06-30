from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import psutil
from typing import Dict, List
import time
import socket
# netifaces n'est plus importé au niveau global

from collectors.bandwidth import get_bandwidth
from collectors.latency import get_latency
from collectors.errors import get_errors
from collectors.connections import get_connections

app = FastAPI(title="Network Monitoring API")

# CORS plus permissif en développement (à restreindre en production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # ← accepter toutes les origines pour le développement
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_default_gateway():
    """Récupère la passerelle par défaut (bloquant, à appeler via asyncio.to_thread)."""
    try:
        # Méthode 1 : netifaces (nécessite pip install netifaces)
        import netifaces
        gws = netifaces.gateways()
        default = gws.get('default', {})
        if netifaces.AF_INET in default:
            return default[netifaces.AF_INET][0]
    except ImportError:
        # Méthode 2 : fallback avec ip route (Linux)
        import subprocess
        import re
        try:
            output = subprocess.check_output(
                "ip route show default", shell=True, text=True, timeout=3
            )
            match = re.search(r'default via (\S+)', output)
            if match:
                return match.group(1)
        except Exception:
            pass
    return None

@app.get("/api/interfaces")
async def get_interfaces() -> List[Dict]:
    """Return list of network interfaces with full details."""
    try:
        # Exécute la fonction bloquante dans un thread
        gateway = await asyncio.to_thread(get_default_gateway)

        stats = psutil.net_if_stats()
        addrs = psutil.net_if_addrs()
        result = []

        for name, stat in stats.items():
            iface = {
                "name": name,
                "up": stat.isup,
                "mtu": stat.mtu,
                "mac": "",
                "ipv4": "",
                "netmask": "",
                "ipv6": "",
                "gateway": gateway or ""
            }

            if name in addrs:
                for addr in addrs[name]:
                    if addr.family == socket.AF_INET:
                        iface["ipv4"] = addr.address
                        iface["netmask"] = addr.netmask
                    elif addr.family == socket.AF_INET6:
                        iface["ipv6"] = addr.address
                    elif hasattr(psutil, "AF_LINK") and addr.family == psutil.AF_LINK:
                        # Sécurisé : vérifie que la constante existe
                        iface["mac"] = addr.address

            result.append(iface)
        return result
    except Exception as e:
        return [{"error": str(e)}]

@app.get("/api/bandwidth")
async def api_bandwidth(
    interface: str = Query(..., description="Network interface name")
) -> Dict:
    """Get bandwidth for interface."""
    # get_bandwidth est bloquant => exécution dans un thread
    return await asyncio.to_thread(get_bandwidth, interface, interval=0.5)

@app.get("/api/latency")
async def api_latency(
    interface: str = Query(..., description="Network interface name"),
    host: str = Query("8.8.8.8", description="Target host")
) -> Dict:
    """Get latency to host."""
    # get_latency est déjà async, pas besoin de to_thread
    return await get_latency(interface, host, count=2)

@app.get("/api/metrics")
async def get_all_metrics() -> Dict:
    """Get all metrics for all interfaces."""
    try:
        interfaces = psutil.net_if_stats()
        result = {}

        for iface_name in interfaces:
            # Exécute la partie bande passante (bloquante) dans un thread
            bw = await asyncio.to_thread(get_bandwidth, iface_name, interval=0.5)
            # get_latency est async
            latency = await get_latency(iface_name, "8.8.8.8", count=2)

            # Vérification plus propre de la présence d'erreur
            bw_ok = isinstance(bw, dict) and "error" not in bw
            lat_ok = isinstance(latency, dict) and "error" not in latency

            result[iface_name] = {
                "bandwidth": bw if bw_ok else {"download_Mbps": 0.0, "upload_Mbps": 0.0},
                "latency": latency if lat_ok else {
                    "avg_ms": 0, "min_ms": 0, "max_ms": 0,
                    "jitter_ms": 0, "packet_loss_pct": 0
                }
            }

        return result
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/errors")
async def api_errors(
    interface: str = Query(..., description="Network interface name")
) -> Dict:
    """Get error counters."""
    # get_errors est bloquant (psutil) → à exécuter dans un thread
    return await asyncio.to_thread(get_errors, interface)

@app.get("/api/connections")
async def api_connections(
    interface: str = Query(None, description="Optional interface filter")
) -> Dict:
    """Get TCP connections stats."""
    # get_connections est bloquant → à exécuter dans un thread
    return await asyncio.to_thread(get_connections, interface)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)