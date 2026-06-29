import time
import psutil
from typing import Dict

def get_bandwidth(interface: str, interval: float = 0.5) -> Dict:
    try:
        io1 = psutil.net_io_counters(pernic=True)
        if interface not in io1:
            return {"error": f"Interface {interface} not found"}
        
        bytes_recv1 = io1[interface].bytes_recv
        bytes_sent1 = io1[interface].bytes_sent
        
        time.sleep(interval)
        
        io2 = psutil.net_io_counters(pernic=True)
        bytes_recv2 = io2[interface].bytes_recv
        bytes_sent2 = io2[interface].bytes_sent
        
        download_mbps = (bytes_recv2 - bytes_recv1) * 8 / interval / 1_000_000
        upload_mbps = (bytes_sent2 - bytes_sent1) * 8 / interval / 1_000_000
        
        return {
            "download_Mbps": round(download_mbps, 2),
            "upload_Mbps": round(upload_mbps, 2),
            "bytes_recv": bytes_recv2,      # ✅ octets reçus depuis le démarrage
            "bytes_sent": bytes_sent2,      # ✅ octets envoyés depuis le démarrage
            "timestamp": time.time()
        }
    except Exception as e:
        return {"error": str(e)}