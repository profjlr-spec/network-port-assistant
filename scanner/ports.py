import socket
from concurrent.futures import ThreadPoolExecutor, as_completed


TOP_PORTS = [22, 53, 80, 139, 443, 445, 3389]


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


def scan_ports(ip, ports_to_scan):
    open_ports = []

    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(scan_port, ip, port) for port in ports_to_scan]

        total_ports = len(futures)
        checked = 0

        for future in as_completed(futures):
            checked += 1
            print(f"  Port scan progress: {checked}/{total_ports}", end="\r")

            result = future.result()
            if result:
                open_ports.append(result)

    print(" " * 50, end="\r")
    open_ports.sort()
    return open_ports


def get_service(port):
    try:
        return socket.getservbyport(port)
    except Exception:
        return "unknown"


def parse_port_range(port_range_text):
    try:
        start_port, end_port = port_range_text.split("-")
        start_port = int(start_port)
        end_port = int(end_port)

        if start_port < 1 or end_port > 65535 or start_port > end_port:
            raise ValueError

        return list(range(start_port, end_port + 1))
    except Exception:
        raise ValueError("Port range must be in format START-END, for example 1-1024.")


def get_ports_to_scan(use_top_ports=False, port_range=None):
    if port_range:
        return parse_port_range(port_range)

    if use_top_ports:
        return TOP_PORTS

    return TOP_PORTS
