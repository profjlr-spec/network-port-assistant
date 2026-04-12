import ipaddress
import re
import socket
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed


# ==============================
# Local OUI vendor hints
# ==============================
# This is a lightweight local mapping for common vendors.
# It is not a complete OUI database.
OUI_VENDORS = {
    "00:1A:2B": "Cisco",
    "00:1B:63": "Apple",
    "00:1C:B3": "Apple",
    "00:1D:4F": "Apple",
    "00:1E:C2": "Apple",
    "00:21:E9": "Apple",
    "00:23:12": "Apple",
    "00:25:00": "Apple",
    "00:26:08": "Apple",
    "04:52:C7": "Apple",
    "14:10:9F": "Apple",
    "28:CF:E9": "Apple",
    "3C:07:54": "Apple",
    "40:A6:D9": "Apple",
    "58:55:CA": "Apple",
    "5C:59:48": "Apple",
    "68:5B:35": "Apple",
    "7C:27:BC": "Apple",
    "88:66:A5": "Apple",
    "A4:5E:60": "Apple",
    "B8:17:C2": "Apple",
    "DC:A6:32": "Raspberry Pi / Sony UK",
    "B8:27:EB": "Raspberry Pi",
    "D8:3A:DD": "Raspberry Pi",
    "E4:5F:01": "Raspberry Pi",
    "2C:CF:67": "Espressif / IoT Device",
    "24:0A:C4": "Espressif / IoT Device",
    "84:F3:EB": "Espressif / IoT Device",
    "18:FE:34": "Espressif / IoT Device",
    "00:50:56": "VMware",
    "00:0C:29": "VMware",
    "00:05:69": "VMware",
    "08:00:27": "VirtualBox",
    "52:54:00": "QEMU / KVM",
    "F8:79:0A": "Router / Network Device",
    "70:03:7E": "Router / Network Device",
    "18:7F:88": "Consumer / Smart Device",
    "14:EA:63": "Private / Consumer Device",
}


# ==============================
# Host discovery
# ==============================
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

    net = ipaddress.IPv4Network(network, strict=False)
    all_hosts = list(net.hosts())
    total_hosts = len(all_hosts)
    hosts = []
    checked = 0

    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(ping_host, str(host)) for host in all_hosts]

        for future in as_completed(futures):
            checked += 1
            print(f"Progress: {checked}/{total_hosts} hosts checked", end="\r")

            result = future.result()
            if result:
                print(f"\nHost active: {result}")
                hosts.append(result)

    print()
    hosts.sort(key=lambda ip: ipaddress.IPv4Address(ip))
    return hosts


# ==============================
# Host detail helpers
# ==============================
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


def is_locally_administered_mac(mac):
    try:
        first_octet = int(mac.split(":")[0], 16)
        return bool(first_octet & 2)
    except Exception:
        return False


def get_vendor(mac, local_mac):
    if not mac or mac == "Unknown":
        return "Unknown"

    mac = mac.upper()
    local_mac = local_mac.upper()

    if mac == local_mac:
        return "Local Interface"

    if is_locally_administered_mac(mac):
        return "Private / Randomized MAC (Vendor Hidden)"

    prefix = mac[0:8]
    return OUI_VENDORS.get(prefix, "Unknown Vendor")

# ==============================
# OS guess helpers
# ==============================
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
        return "Linux / Unix / Router"
    elif ttl <= 128:
        return "Windows"
    elif ttl <= 255:
        return "Network Device / Router"

    return "Unknown"
