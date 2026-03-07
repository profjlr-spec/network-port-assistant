import csv
import json
from datetime import datetime


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
        raise SystemExit


def save_results(interface_info, hosts):
    save_json_results(interface_info, hosts)
    save_csv_results(hosts)


def save_json_results(interface_info, hosts):
    data = {
        "scan_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "interface_info": interface_info,
        "hosts": hosts
    }

    with open("scan_results.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    print("Saved: scan_results.json")


def save_csv_results(hosts):
    with open("scan_results.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "ip",
            "hostname",
            "mac",
            "vendor",
            "os",
            "open_ports",
            "banners"
        ])

        for host in hosts:
            open_ports = "; ".join(
                f"{port_info['port']} {port_info['service']}"
                for port_info in host["ports"]
            )

            banners = "; ".join(
                f"{port_info['port']} {port_info['banner']}"
                for port_info in host["ports"]
                if port_info.get("banner")
            )

            writer.writerow([
                str(host.get("ip", "")),
                str(host.get("hostname", "")),
                str(host.get("mac", "")),
                str(host.get("vendor", "")),
                str(host.get("os", "")),
                open_ports,
                banners
            ])

    print("Saved: scan_results.csv")
