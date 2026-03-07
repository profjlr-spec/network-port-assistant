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
    data = {
        "scan_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "interface_info": interface_info,
        "hosts": hosts
    }

    with open("scan_results.json", "w") as f:
        json.dump(data, f, indent=4)

    print("\nResults saved to scan_results.json")
