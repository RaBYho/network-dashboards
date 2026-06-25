import psutil
import time

def get_network_stats(interface=None, interval=1.0):
    """
    Retourne le débit montant/descendant en Mo/s et la bande passante en Mbps.
    interface : nom de l'interface (ex: 'eth0', 'Wi-Fi'). None = toutes interfaces.
    """
    # Premier snapshot
    if interface:
        s1 = psutil.net_io_counters(pernic=True)[interface]
    else:
        s1 = psutil.net_io_counters()

    time.sleep(interval)

    # Deuxième snapshot
    if interface:
        s2 = psutil.net_io_counters(pernic=True)[interface]
    else:
        s2 = psutil.net_io_counters()

    # Calcul des deltas
    bytes_sent = s2.bytes_sent - s1.bytes_sent
    bytes_recv = s2.bytes_recv - s1.bytes_recv

    return {
        "debit_montant_MBps": round(bytes_sent / interval / 1_000_000, 3),   # Mo/s upload
        "debit_descendant_MBps": round(bytes_recv / interval / 1_000_000, 3), # Mo/s download
        "bande_passante_montant_Mbps": round(bytes_sent * 8 / interval / 1_000_000, 3),  # Mbps upload
        "bande_passante_descendant_Mbps": round(bytes_recv * 8 / interval / 1_000_000, 3), # Mbps download
        "timestamp": time.time()
    }

# Test rapide
if __name__ == "__main__":
    while True:
        stats = get_network_stats(interval=1.0)
        print(f"↑ {stats['bande_passante_montant_Mbps']} Mbps  "
              f"↓ {stats['bande_passante_descendant_Mbps']} Mbps")