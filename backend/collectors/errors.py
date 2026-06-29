import psutil
import time
from typing import Dict

def get_errors(interface: str) -> Dict:
    try:
        io_counters = psutil.net_io_counters(pernic=True)
        if interface not in io_counters:
            return {"error": f"Interface {interface} not found"}
        
        counters = io_counters[interface]
        
        total_errors = counters.errin + counters.errout + counters.dropin + counters.dropout
        total_packets = counters.packets_recv + counters.packets_sent + 1  # avoid div0
        error_rate = (total_errors / total_packets * 100)
        
        return {
            "interface": interface,
            "errin": counters.errin,
            "errout": counters.errout,
            "dropin": counters.dropin,
            "dropout": counters.dropout,
            "error_rate_pct": round(error_rate, 4),
            "timestamp": time.time()
        }
    except Exception as e:
        return {"error": str(e)}
