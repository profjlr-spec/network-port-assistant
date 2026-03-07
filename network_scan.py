import argparse

from scanner.discovery import discover_hosts, get_hostname, get_mac, get_vendor
from scanner.interfaces import choose_interface, get_interface_info
from scanner.ports import get_service, scan_ports
from scanner.utils import interactive_menu, save_results


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

    if interface_info is None:
        return

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
            mac = interface_info["mac_address"].upper()
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
