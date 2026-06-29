import psutil
from collections import defaultdict
from typing import Dict, Optional

def get_connections(interface: Optional[str] = None) -> Dict:
    try:
        connections = psutil.net_connections(kind='tcp')
        states = defaultdict(int)
        total = len(connections)
        
        for conn in connections:
            states[conn.status] += 1
        
        return {
            "total": total,
            "states": dict(states)
        }
    except Exception as e:
        return {"error": str(e)}
