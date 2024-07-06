import os
import time
import socket
import psutil
from ping3 import ping, verbose_ping

def get_ip_address():
    try:
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)
    except Exception as e:
        return f"Tidak dapat mendapatkan IP address: {e}"

def get_network_info():
    try:
        interfaces = psutil.net_if_addrs()
        ip_address = None
        gateway = None
        dns_servers = []

        for interface in interfaces:
            for snic in interfaces[interface]:
                if snic.family == socket.AF_INET and not snic.address.startswith("127."):
                    ip_address = snic.address
                    break

        net_if_stats = psutil.net_if_stats()
        for interface, stats in net_if_stats.items():
            if stats.isup and ip_address:
                gateway = psutil.net_if_addrs()[interface][0].address
                break

        resolv_conf_path = '/etc/resolv.conf'
        if os.path.exists(resolv_conf_path):
            with open(resolv_conf_path, 'r') as file:
                for line in file:
                    if line.startswith('nameserver'):
                        dns_servers.append(line.split()[1])
        
        return {
            "ip": ip_address or "Tidak ditemukan",
            "gateway": gateway or "Tidak ditemukan",
            "dns": ", ".join(dns_servers) if dns_servers else "Tidak ditemukan",
        }
    except Exception as e:
        return {
            "ip": f"Tidak dapat mendapatkan IP address: {e}",
            "gateway": f"Tidak dapat mendapatkan Gateway: {e}",
            "dns": f"Tidak dapat mendapatkan DNS: {e}"
        }

def check_local_network():
    response = ping("8.8.8.8")
    return response is not None

def monitor_connection(host, interval=1, log_file="connection_log.txt"):
    while True:
        network_info = get_network_info()
        response = ping(host)
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        if response is None:
            local_network_status = check_local_network()
            log_message = f"{current_time} - Connection to {host} lost\n"
            if not local_network_status:
                log_message += f"{current_time} - Local network issue detected\n"
            else:
                log_message += f"{current_time} - Issue likely with remote host or network\n"
            log_message += f"IP: {network_info['ip']}, Gateway: {network_info['gateway']}, DNS: {network_info['dns']}\n"
        else:
            log_message = f"{current_time} - Connection to {host} is up, latency: {response*1000:.2f} ms\n"
        
        # Cetak ke layar (console)
        print(log_message.strip())

        # Tulis ke file log
        with open(log_file, "a") as log:
            log.write(log_message)

        time.sleep(interval)

if __name__ == "__main__":
    target_host = "192.168.0.1"  # Ganti dengan IP perangkat yang ingin dimonitor
    monitor_connection(target_host, interval=5)  # Memantau setiap 5 detik