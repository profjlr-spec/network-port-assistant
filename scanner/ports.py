import socket
import ssl
from concurrent.futures import ThreadPoolExecutor, as_completed


TOP_PORTS = [
    21, 22, 23, 25, 53, 80, 110, 123, 135, 139,
    143, 161, 389, 443, 445, 587, 636, 3306, 3389,
    5432, 5900, 8080, 8443
]

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
            print(f"\r  Port scan progress: {checked}/{total_ports}", end="")

            result = future.result()
            if result:
                open_ports.append(result)

    # limpia la línea de progreso completamente
    print("\r" + " " * 80 + "\r", end="")

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


def grab_banner(ip, port):
    try:
        if port == 80:
            with socket.create_connection((ip, port), timeout=2) as sock:
                request = f"HEAD / HTTP/1.1\r\nHost: {ip}\r\nConnection: close\r\n\r\n"
                sock.sendall(request.encode())
                response = sock.recv(1024).decode(errors="ignore").strip()

                if response:
                    return response.splitlines()[0]

        elif port == 443:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            with socket.create_connection((ip, port), timeout=2) as sock:
                with context.wrap_socket(sock, server_hostname=ip) as ssock:
                    request = f"HEAD / HTTP/1.1\r\nHost: {ip}\r\nConnection: close\r\n\r\n"
                    ssock.sendall(request.encode())
                    response = ssock.recv(1024).decode(errors="ignore").strip()

                    if response:
                        return response.splitlines()[0]

                    return "TLS service detected"

        elif port == 22:
            with socket.create_connection((ip, port), timeout=2) as sock:
                banner = sock.recv(1024).decode(errors="ignore").strip()
                if banner:
                    return banner

        else:
            with socket.create_connection((ip, port), timeout=2) as sock:
                try:
                    banner = sock.recv(1024).decode(errors="ignore").strip()
                    if banner:
                        return banner.splitlines()[0]
                except Exception:
                    pass

    except Exception:
        return None

    return None
