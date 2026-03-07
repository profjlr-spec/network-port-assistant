import socket
from concurrent.futures import ThreadPoolExecutor, as_completed


COMMON_PORTS = [22, 53, 80, 139, 443, 445, 3389]


def scan_port(ip, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            result = sock.connect_ex((ip, port))
            if result == 0:
                return port
    except Exception:
        return None

    return None


def scan_ports(ip):
    open_ports = []

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(scan_port, ip, p) for p in COMMON_PORTS]

        for future in as_completed(futures):
            result = future.result()
            if result:
                open_ports.append(result)

    open_ports.sort()
    return open_ports


def get_service(port):
    try:
        return socket.getservbyport(port)
    except Exception:
        return "unknown"
