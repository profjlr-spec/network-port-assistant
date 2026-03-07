import ipaddress
import re
import socket
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed


OUI_VENDORS = {
    "F8:79:0A": "Router / Network Device",
    "7C:27:BC": "Apple",
    "7A:7A:12": "Unknown / Private MAC",
}


def ping_host(ip):
    result = subprocess.run(
        ["ping", "-c", "1", "-W", "1", ip],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    if result.returncode == 0:
        return ip

    return None


def discover_hosts(network):
    print(f"\nScanning network: {network}\n")

    net = ipaddress.IPv4Network(network)
    hosts = []

    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(ping_host, str(host)) for host in net.hosts()]

        for future in as_completed(futures):
            result = future.result()
            if result:
                print(f"Host active: {result}")
                hosts.append(result)

    hosts.sort(key=lambda ip: ipaddress.IPv4Address(ip))
    return hosts


def get_hostname(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except Exception:
        return "Unknown"


def get_mac(ip):
    try:
        output = subprocess.check_output(["arp", "-n", ip], text=True)

        for line in output.splitlines():
            if ip in line:
                for part in line.split():
                    if ":" in part and len(part) == 17:
                        return part.upper()
    except Exception:
        pass

    return "Unknown"


def get_vendor(mac, local_mac):
    if mac == "Unknown":
        return "Unknown"

    if mac.upper() == local_mac.upper():
        return "Local Interface"

    prefix = mac.upper()[0:8]
    return OUI_VENDORS.get(prefix, "Unknown Vendor")


def get_ttl(ip):
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "1", ip],
            capture_output=True,
            text=True
        )

        output = result.stdout
        match = re.search(r"ttl[=\s](\d+)", output, re.IGNORECASE)

        if match:
            return int(match.group(1))

    except Exception:
        pass

    return None


def detect_os(ip):
    ttl = get_ttl(ip)

    if ttl is None:
        return "Unknown"

    if ttl <= 64:
        return "Linux / Router"
    elif ttl <= 128:
        return "Windows"
    elif ttl <= 255:
        return "Network Device / Router"

    return "Unknown"
