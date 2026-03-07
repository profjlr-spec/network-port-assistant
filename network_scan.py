import argparse

from scanner.discovery import (
    detect_os,
    discover_hosts,
    get_hostname,
    get_mac,
    get_vendor,
)
from scanner.interfaces import choose_interface, get_interface_info
from scanner.ports import get_ports_to_scan, get_service, scan_ports
from scanner.utils import interactive_menu, save_results


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--scan", action="store_true")
    parser.add_argument("--ports", action="store_true")
    parser.add_argument("--save", action="store_true")
    parser.add_argument(
        "--top-ports",
        action="store_true",
        help="Scan a predefined list of common ports"
    )
    parser.add_argument(
        "--port-range",
        type=str,
        help="Scan a custom port range, for example 1-1024"
    )

    return parser.parse_args()


def print_host_separator():
    print("=" * 40)


def print_summary(total_hosts, hosts_with_open_ports, save_enabled):
    print("\nScan Summary")
    print("-" * 20)
    print(f"Active hosts found      : {total_hosts}")
    print(f"Hosts with open ports   : {hosts_with_open_ports}")

    if save_enabled:
        print("Results saved           : scan_results.json, scan_results.csv")


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
    print(f"Interface   : {interface_info['interface']}")
    print(f"IP Address  : {interface_info['ip_address']}")
    print(f"Netmask     : {interface_info['netmask']}")
    print(f"Network     : {interface_info['network']}")
    print(f"Local MAC   : {interface_info['mac_address']}")

    hosts = discover_hosts(interface_info["network"])

    if not hosts:
        print("\nNo active hosts were found.")
        return

    results = []
    hosts_with_open_ports = 0

    print("\nDiscovered Hosts:\n")

    ports_to_scan = []
    if ports:
        try:
            ports_to_scan = get_ports_to_scan(
                use_top_ports=args.top_ports,
                port_range=args.port_range
            )
        except ValueError as error:
            print(f"Error: {error}")
            return

        print(f"Ports selected for scanning: {len(ports_to_scan)} ports\n")

    for host in hosts:
        hostname = get_hostname(host)

        if host == interface_info["ip_address"]:
            mac = interface_info["mac_address"].upper()
        else:
            mac = get_mac(host)

        vendor = get_vendor(mac, interface_info["mac_address"])
        os_guess = detect_os(host)

        print_host_separator()
        print(f"Host     : {host}")
        print(f"Hostname : {hostname}")
        print(f"MAC      : {mac}")
        print(f"Vendor   : {vendor}")
        print(f"OS       : {os_guess}")

        port_data = []

        if ports:
            open_ports = scan_ports(host, ports_to_scan)

            print("Open Ports:")
            if open_ports:
                hosts_with_open_ports += 1
                for port in open_ports:
                    service = get_service(port)
                    print(f"  - {port:<5} {service}")
                    port_data.append({
                        "port": port,
                        "service": service
                    })
            else:
                print("  - None found")

        print_host_separator()
        print()

        results.append({
            "ip": host,
            "hostname": hostname,
            "mac": mac,
            "vendor": vendor,
            "os": os_guess,
            "ports": port_data
        })

    if save:
        print("Saving results...\n")
        save_results(interface_info, results)

    print_summary(
        total_hosts=len(hosts),
        hosts_with_open_ports=hosts_with_open_ports,
        save_enabled=save
    )


if __name__ == "__main__":
    main()
