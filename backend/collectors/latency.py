import subprocess
import re
import time
import asyncio
import platform
from typing import Dict

async def get_latency(interface: str, host: str, count: int = 1) -> Dict:  # ✅ count=2 par défaut
    try:
        system = platform.system().lower()
        if system == "windows":
            cmd = ["ping", "-n", str(count), host]
            # Note: Windows ne supporte pas -I pour l'interface, on ignore
        else:
            # ✅ Utilise l'interface si fournie et si le système le permet (Linux)
            if interface and system == "linux":
                cmd = ["ping", "-c", str(count), "-I", interface, host]
            else:
                cmd = ["ping", "-c", str(count), host]
        
        loop = asyncio.get_running_loop()
        # ✅ timeout réduit à 6 secondes (2 pings * 2s + marge)
        result = await loop.run_in_executor(
            None, 
            lambda: subprocess.run(cmd, capture_output=True, text=True, timeout=3)
        )
        
        output = result.stdout + result.stderr
        
        # Parse RTTs
        rtt_matches = re.findall(r'time[=<](\d+\.?\d*)', output)
        rtts = [float(t) for t in rtt_matches]
        
        # Packet loss
        loss_match = re.search(r'(\d+)%\s*packet loss', output)
        packet_loss = float(loss_match.group(1)) if loss_match else 0.0
        
        if not rtts:
            # Fallback to ping3
            try:
                import ping3
                rtts = []
                for _ in range(count):
                    rtt = ping3.ping(host, timeout=3, unit='ms')
                    if rtt is not None:
                        # ✅ ping3 retourne déjà des millisecondes si unit='ms'
                        rtts.append(rtt)
                    await asyncio.sleep(0.3)
            except:
                pass
        
        if not rtts:
            return {"error": "Could not get latency data"}
        
        avg_ms = sum(rtts) / len(rtts)
        min_ms = min(rtts)
        max_ms = max(rtts)
        jitter = 0
        if len(rtts) > 1:
            diffs = [abs(rtts[i] - rtts[i-1]) for i in range(1, len(rtts))]
            jitter = sum(diffs) / len(diffs)
        
        return {
            "host": host,
            "interface": interface,
            "avg_ms": round(avg_ms, 2),
            "min_ms": round(min_ms, 2),
            "max_ms": round(max_ms, 2),
            "jitter_ms": round(jitter, 2),
            "packet_loss_pct": round(packet_loss, 1),
            "rtts_ms": [round(r, 2) for r in rtts],
            "timestamp": time.time()
        }
    except Exception as e:
        return {"error": str(e)}