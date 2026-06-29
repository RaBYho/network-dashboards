from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import psutil
from typing import Dict, List
import time
import socket
from collectors.bandwidth import get_bandwidth
from collectors.latency import get_latency
from collectors.errors import get_errors
from collectors.connections import get_connections

app = FastAPI(title="Network Monitoring API")

# ✅ CORS élargi pour développement (accepte localhost avec n'importe quel port)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://localhost:3000",   # ports alternatifs fréquents
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/interfaces")
async def get_interfaces() -> List[Dict]:
    """Return list of network interfaces with full details."""
    try:
        stats = psutil.net_if_stats()
        addrs = psutil.net_if_addrs()
        result = []
        for name, stat in stats.items():
            iface = {
                "name": name,
                "up": stat.isup,
                "mac": "",
                "ipv4": "",
                "netmask": "",
                "ipv6": "",
            }
            # Récupération des adresses
            if name in addrs:
                for addr in addrs[name]:
                    if addr.family == socket.AF_INET:
                        iface["ipv4"] = addr.address
                        iface["netmask"] = addr.netmask
                    elif addr.family == socket.AF_INET6:
                        iface["ipv6"] = addr.address
                    elif addr.family == psutil.AF_LINK:  # MAC
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
    return get_bandwidth(interface, interval=0.5)  # ✅ réduit à 0.5s

@app.get("/api/latency")
async def api_latency(
    interface: str = Query(..., description="Network interface name"),
    host: str = Query("8.8.8.8", description="Target host")
) -> Dict:
    """Get latency to host."""
    return await get_latency(interface, host, count=2)  # ✅ 2 pings suffisent

@app.get("/api/metrics")
async def get_all_metrics() -> Dict:
    """Get all metrics for all interfaces."""
    try:
        interfaces = psutil.net_if_stats()
        result = {}
        
        for iface_name, _ in interfaces.items():
            bw = get_bandwidth(iface_name, interval=0.5)
            latency = await get_latency(iface_name, "8.8.8.8", count=2)
            
            result[iface_name] = {
                "bandwidth": bw if "error" not in str(bw) else {"download_Mbps": 0.0, "upload_Mbps": 0.0},
                "latency": latency if "error" not in str(latency) else {
                    "avg_ms": 0, "min_ms": 0, "max_ms": 0, "jitter_ms": 0, "packet_loss_pct": 0
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
    return get_errors(interface)

@app.get("/api/connections")
async def api_connections(
    interface: str = Query(None, description="Optional interface filter")
) -> Dict:
    """Get TCP connections stats."""
    return get_connections(interface)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)