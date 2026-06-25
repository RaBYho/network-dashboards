import subprocess
import re
import time
import platform

def ping(host="8.8.8.8", count=4):
    """
    Envoie 'count' pings vers 'host' et retourne les RTT en ms.
    Fonctionne sur Windows, Linux et macOS.
    """
    system = platform.system()

    if system == "Windows":
        cmd = ["ping", "-n", str(count), host]
    else:
        cmd = ["ping", "-c", str(count), host]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        output = result.stdout
    except subprocess.TimeoutExpired:
        return None

    return parse_ping(output, system)


def parse_ping(output, system):
    """
    Extrait les RTT individuels + statistiques depuis la sortie du ping.
    """
    # Extraire chaque RTT individuel (ex: time=12.3 ms)
    rtts = re.findall(r"time[=<]([\d.]+)\s*ms", output)
    rtts = [float(r) for r in rtts]

    if not rtts:
        return None

    # Calcul du jitter = écart moyen entre RTTs consécutifs
    jitter = 0
    if len(rtts) > 1:
        diffs = [abs(rtts[i] - rtts[i-1]) for i in range(1, len(rtts))]
        jitter = round(sum(diffs) / len(diffs), 3)

    # Perte de paquets
    loss_match = re.search(r"(\d+)%\s*(?:packet\s*)?loss", output)
    packet_loss = float(loss_match.group(1)) if loss_match else 0.0

    return {
        "host": None,           # sera rempli par l'appelant
        "rtts_ms": rtts,
        "min_ms":  round(min(rtts), 3),
        "max_ms":  round(max(rtts), 3),
        "avg_ms":  round(sum(rtts) / len(rtts), 3),  # latence moyenne
        "jitter_ms": jitter,
        "packet_loss_pct": packet_loss,
        "timestamp": time.time()
    }


def get_latency(host="8.8.8.8", count=4):
    """Point d'entrée principal."""
    stats = ping(host, count)
    if stats:
        stats["host"] = host
    return stats


# Test
if __name__ == "__main__":
    result = get_latency("8.8.8.8", count=4)
    if result:
        print(f"RTT min/avg/max : {result['min_ms']}/{result['avg_ms']}/{result['max_ms']} ms")
        print(f"Jitter : {result['jitter_ms']} ms")
        print(f"Perte de paquets : {result['packet_loss_pct']} %")
    else:
        print("Hôte inaccessible.")