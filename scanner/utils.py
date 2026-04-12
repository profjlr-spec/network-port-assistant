import csv
import json
import os
from datetime import datetime


# ==============================
# Interactive menu
# ==============================
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


# ==============================
# Output path helpers
# ==============================
def get_timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def ensure_output_directory():
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


# ==============================
# Save scan results
# ==============================
def save_results(interface_info, hosts):
    scan_time = datetime.now()
    timestamp = get_timestamp()
    output_dir = ensure_output_directory()

    json_file = os.path.join(output_dir, f"scan_results_{timestamp}.json")
    csv_file = os.path.join(output_dir, f"scan_results_{timestamp}.csv")

    save_json_results(interface_info, hosts, scan_time, json_file)
    save_csv_results(interface_info, hosts, scan_time, csv_file)

    return json_file, csv_file


def save_json_results(interface_info, hosts, scan_time, json_file):
    data = {
        "scan_time": scan_time.strftime("%Y-%m-%d %H:%M:%S"),
        "interface_info": interface_info,
        "hosts": hosts
    }

    with open(json_file, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    print(f"Saved JSON: {json_file}")


def save_csv_results(interface_info, hosts, scan_time, csv_file):
    with open(csv_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "scan_time",
            "interface",
            "network",
            "ip",
            "hostname",
            "mac",
            "vendor",
            "os_guess",
            "open_port_count",
            "open_ports",
            "banners"
        ])

        for host in hosts:
            ports = host.get("ports", [])

            open_ports = "; ".join(
                f"{port_info['port']} {port_info['service']}"
                for port_info in ports
            )

            banners = "; ".join(
                f"{port_info['port']} {port_info['banner']}"
                for port_info in ports
                if port_info.get("banner")
            )

            writer.writerow([
                scan_time.strftime("%Y-%m-%d %H:%M:%S"),
                str(interface_info.get("interface", "")),
                str(interface_info.get("network", "")),
                str(host.get("ip", "")),
                str(host.get("hostname", "")),
                str(host.get("mac", "")),
                str(host.get("vendor", "")),
                str(host.get("os", "")),
                len(ports),
                open_ports,
                banners
            ])

    print(f"Saved CSV : {csv_file}")
