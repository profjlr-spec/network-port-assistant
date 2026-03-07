import argparse
import ipaddress
import json
import netifaces
import socket
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime


COMMON_PORTS = [22, 53, 80, 139, 443, 445, 3389]

OUI_VENDORS = {
    "F8:79:0A": "Router / Network Device",
    "7C:27:BC": "Apple",
    "7A:7A:12": "Unknown / Private MAC",
}


def interactive_menu():
    print("\nNetwork Port Assistant")
    print("----------------------")
    print("1) Discover hosts")
    print("2) Discover hosts + scan ports")
    print("3) Full scan + save results")
    print("4) Exit")

    choice = input("\nSelect option: ")

    if choice == "1":
        return True, False, False
    elif choice == "2":
        return True, True, False
    elif choice == "3":
        return True, True, True
    else:
        exit()


def list_interfaces():
    interfaces = netifaces.interfaces()
    excluded = {"lo", "docker0"}
    filtered = [i for i in interfaces if i not in excluded]

    print("\nAvailable Network Interfaces:\n")
    for i, iface in enumerate(filtered, start=1):
        print(f"{i}. {iface}")

    return filtered


def choose_interface():
    interfaces = list_interfaces()

    while True:
        try:
            choice = int(input("\nSelect an interface: "))
            if 1 <= choice <= len(interfaces):
                return interfaces[choice - 1]
        except:
            pass


def get_interface_info(interface):
    addresses = netifaces.ifaddresses(interface)

    ipv4 = addresses[netifaces.AF_INET][0]
    ip = ipv4.get("addr")
    netmask = ipv4.get("netmask")

    network = ipaddress.IPv4Network(f"{ip}/{netmask}", strict=False)

    mac = "Unknown"
    if netifaces.AF_LINK in addresses:
        mac = addresses[netifaces.AF_LINK][0].get("addr", "Unknown")

    return {
        "interface": interface,
        "ip_address": ip,
        "netmask": netmask,
        "network": str(network),
        "mac_address": mac
    }


def ping_host(ip):
    result = subprocess.run(
        ["ping", "-c", "1", "-W", "1", ip],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    if result.returncode == 0:
        return ip


def discover_hosts(network):

    print(f"\nScanning network: {network}\n")

    net = ipaddress.IPv4Network(network)
    hosts = []

    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(ping_host, str(host)) for host in net.hosts()]

        for future in as_completed(futures):
            result = future.result()
            if result:
                print("Host active:", result)
                hosts.append(result)

    hosts.sort(key=lambda ip: ipaddress.IPv4Address(ip))
    return hosts


def scan_port(ip, port):

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        result = sock.connect_ex((ip, port))

        if result == 0:
            return port


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
    except:
        return "unknown"


def get_hostname(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except:
        return "Unknown"


def get_mac(ip):
    try:
        output = subprocess.check_output(["arp", "-n", ip], text=True)

        for line in output.splitlines():
            if ip in line:
                for part in line.split():
                    if ":" in part and len(part) == 17:
                        return part.upper()
    except:
        pass

    return "Unknown"


def get_vendor(mac, local_mac):

    if mac == "Unknown":
        return "Unknown"

    if mac.upper() == local_mac.upper():
        return "Local Interface"

    prefix = mac.upper()[0:8]
    return OUI_VENDORS.get(prefix, "Unknown Vendor")


def save_results(interface_info, hosts):

    data = {
        "scan_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "interface_info": interface_info,
        "hosts": hosts
    }

    with open("scan_results.json", "w") as f:
        json.dump(data, f, indent=4)

    print("\nResults saved to scan_results.json")


def parse_args():

    parser = argparse.ArgumentParser()

    parser.add_argument("--scan", action="store_true")
    parser.add_argument("--ports", action="store_true")
    parser.add_argument("--save", action="store_true")

    return parser.parse_args()


def main():

    args = parse_args()

    if not args.scan and not args.ports and not args.save:
        scan, ports, save = interactive_menu()
    else:
        scan = args.scan
        ports = args.ports
        save = args.save

    interface = choose_interface()
    interface_info = get_interface_info(interface)

    print("\nInterface Information:")
    print("Interface   :", interface_info["interface"])
    print("IP Address  :", interface_info["ip_address"])
    print("Netmask     :", interface_info["netmask"])
    print("Network     :", interface_info["network"])
    print("Local MAC   :", interface_info["mac_address"])

    hosts = discover_hosts(interface_info["network"])

    results = []

    print("\nDiscovered Hosts:\n")

    for host in hosts:

        hostname = get_hostname(host)

        if host == interface_info["ip_address"]:
            mac = interface_info["mac_address"]
        else:
            mac = get_mac(host)

        vendor = get_vendor(mac, interface_info["mac_address"])

        print("Host:", host)
        print("  Hostname:", hostname)
        print("  MAC Address:", mac)
        print("  Vendor:", vendor)

        port_data = []

        if ports:

            open_ports = scan_ports(host)

            if open_ports:
                print("  Open Ports:")
                for p in open_ports:
                    service = get_service(p)
                    print("   ", p, service)
                    port_data.append({"port": p, "service": service})
            else:
                print("  No common open ports found.")

        print()

        results.append({
            "ip": host,
            "hostname": hostname,
            "mac": mac,
            "vendor": vendor,
            "ports": port_data
        })

    if save:
        save_results(interface_info, results)


if __name__ == "__main__":
    main()
