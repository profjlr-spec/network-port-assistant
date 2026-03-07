import ipaddress
import netifaces


def list_interfaces():
    interfaces = netifaces.interfaces()
    excluded = {"lo", "docker0"}
    filtered = [i for i in interfaces if i not in excluded]
    return filtered


def choose_interface():
    interfaces = list_interfaces()

    print("\nAvailable Network Interfaces:\n")
    for i, iface in enumerate(interfaces, start=1):
        print(f"{i}. {iface}")

    while True:
        try:
            choice = int(input("\nSelect an interface: "))
            if 1 <= choice <= len(interfaces):
                selected = interfaces[choice - 1]
                print(f"\nSelected Interface: {selected}")
                return selected
            print("Number out of range.")
        except ValueError:
            print("Please enter a valid number.")


def get_interface_info(interface):
    addresses = netifaces.ifaddresses(interface)

    if netifaces.AF_INET not in addresses:
        print("No IPv4 address found for this interface.")
        return None

    ipv4 = addresses[netifaces.AF_INET][0]
    ip = ipv4.get("addr")
    netmask = ipv4.get("netmask")

    if not ip or not netmask:
        print("Could not determine IP address or netmask.")
        return None

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
