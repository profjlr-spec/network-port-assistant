from scapy.all import ARP, Ether, srp
from mac_vendor_lookup import MacLookup
import socket
import ipaddress
import subprocess
import re
import nmap
import json
from datetime import datetime


def get_active_interface_and_ip():
    result = subprocess.run(["ip", "-4", "addr", "show"], capture_output=True, text=True)
    output = result.stdout

    current_interface = None

    for line in output.splitlines():
        iface_match = re.match(r"^\d+:\s+([^:]+):", line)
        if iface_match:
            current_interface = iface_match.group(1)

        inet_match = re.search(r"inet\s+(\d+\.\d+\.\d+\.\d+)/(\d+)", line)
        if inet_match and current_interface != "lo":
            ip = inet_match.group(1)
            cidr = inet_match.group(2)
            return current_interface, ip, cidr

    return None, None, None


def get_mac_address(interface):
    try:
        with open(f"/sys/class/net/{interface}/address", "r") as f:
            return f.read().strip()
    except Exception:
        return "Unknown"


def get_network_range(ip, cidr):
    network = ipaddress.ip_network(f"{ip}/{cidr}", strict=False)
    return str(network)


def get_hostname(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except Exception:
        return "Unknown"


def scan_open_ports(ip):
    open_ports = []
    try:
        nm = nmap.PortScanner()
        nm.scan(ip, arguments="-F")

        if ip in nm.all_hosts():
            for proto in nm[ip].all_protocols():
                ports = nm[ip][proto].keys()
                for port in sorted(ports):
                    if nm[ip][proto][port]["state"] == "open":
                        service = nm[ip][proto][port]["name"]
                        open_ports.append({
                            "port": port,
                            "protocol": proto,
                            "service": service
                        })
    except Exception:
        pass

    return open_ports


def scan_network(ip_range):
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp

    result = srp(packet, timeout=2, verbose=0)[0]

    devices = []
    lookup = MacLookup()

    for _, received in result:
        try:
            vendor = lookup.lookup(received.hwsrc)
        except Exception:
            vendor = "Unknown"

        hostname = get_hostname(received.psrc)
        open_ports = scan_open_ports(received.psrc)

        devices.append({
            "ip": received.psrc,
            "mac": received.hwsrc,
            "vendor": vendor,
            "hostname": hostname,
            "open_ports": open_ports
        })

    return devices


def save_to_json(scan_data, filename="scan_results.json"):
    with open(filename, "w") as f:
        json.dump(scan_data, f, indent=4)
    print(f"\nResultados guardados en {filename}")


def main():
    interface, local_ip, cidr = get_active_interface_and_ip()

    if not interface or not local_ip:
        print("No se pudo detectar una interfaz activa.")
        return

    local_mac = get_mac_address(interface)
    network_range = get_network_range(local_ip, cidr)

    print("\nNetwork Port Assistant")
    print("=" * 40)
    print(f"Active Interface : {interface}")
    print(f"Local IP         : {local_ip}/{cidr}")
    print(f"Local MAC        : {local_mac}")
    print(f"Detected Network : {network_range}")

    print("\nEscaneando red, espera...\n")
    devices = scan_network(network_range)

    if not devices:
        print("No se encontraron dispositivos.")
        return

    print("Devices Found")
    print("=" * 40)

    for device in devices:
        print(f"IP       : {device['ip']}")
        print(f"MAC      : {device['mac']}")
        print(f"Vendor   : {device['vendor']}")
        print(f"Hostname : {device['hostname']}")

        if device["open_ports"]:
            print("Ports    :")
            for port in device["open_ports"]:
                print(f"  - {port['port']}/{port['protocol']} ({port['service']})")
        else:
            print("Ports    : No open common ports found")

        print("-" * 40)

    scan_data = {
        "scan_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "interface": interface,
        "local_ip": f"{local_ip}/{cidr}",
        "local_mac": local_mac,
        "network_range": network_range,
        "devices": devices
    }

    save_to_json(scan_data)


if __name__ == "__main__":
    main()
