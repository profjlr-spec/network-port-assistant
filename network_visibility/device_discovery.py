# ==============================
# Network Device Discovery Tool
# ==============================

import subprocess
import json
import os
import csv

from datetime import datetime
from tabulate import tabulate


# ==============================
# Configuration
# ==============================

NETWORK = "192.168.1.0/24"

OUTPUT_FILE = "devices.json"

CSV_FILE = "devices.csv"

LOG_FILE = "network_events.log"


# ==============================
# Run Nmap Scan
# ==============================

def run_nmap_scan():

    command = [
        "sudo",
        "nmap",
        "-sn",
        NETWORK
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    return result.stdout


# ==============================
# Parse Nmap Output
# ==============================

def parse_nmap_output(output):

    devices = []

    current_device = {}

    for line in output.splitlines():

        line = line.strip()

        # --------------------------
        # New device found
        # --------------------------

        if line.startswith("Nmap scan report for"):

            if current_device:
                devices.append(current_device)

            target = line.replace(
                "Nmap scan report for",
                ""
            ).strip()

            current_device = {
                "target": target,
                "ip": None,
                "mac": None,
                "vendor": None,
                "status": "KNOWN",
                "last_seen": datetime.now().isoformat()
            }

            # Extract IP
            if "(" in target and ")" in target:

                current_device["ip"] = (
                    target.split("(")[-1]
                    .replace(")", "")
                )

            else:
                current_device["ip"] = target

        # --------------------------
        # MAC Address
        # --------------------------

        elif line.startswith("MAC Address:"):

            parts = line.replace(
                "MAC Address:",
                ""
            ).strip()

            mac = parts.split(" ")[0]

            if "(" in parts:

                vendor = (
                    parts.split("(", 1)[1]
                    .replace(")", "")
                )

            else:
                vendor = "Unknown"

            current_device["mac"] = mac

            current_device["vendor"] = vendor

    # Add last device
    if current_device:
        devices.append(current_device)

    return devices


# ==============================
# Load Previous Devices
# ==============================

def load_previous_devices():

    if not os.path.exists(OUTPUT_FILE):
        return []

    with open(OUTPUT_FILE, "r") as file:

        return json.load(file)


# ==============================
# Save Devices JSON
# ==============================

def save_devices(devices):

    with open(OUTPUT_FILE, "w") as file:

        json.dump(
            devices,
            file,
            indent=4
        )


# ==============================
# Save CSV Report
# ==============================

def save_csv(devices):

    with open(CSV_FILE, "w", newline="") as file:

        writer = csv.writer(file)

        writer.writerow([
            "IP Address",
            "MAC Address",
            "Vendor",
            "Status",
            "Last Seen"
        ])

        for device in devices:

            writer.writerow([
                device.get("ip"),
                device.get("mac"),
                device.get("vendor"),
                device.get("status"),
                device.get("last_seen")
            ])


# ==============================
# Detect New Devices
# ==============================

def detect_new_devices(
    current_devices,
    previous_devices
):

    previous_macs = {
        device.get("mac")
        for device in previous_devices
        if device.get("mac")
    }

    new_devices = []

    for device in current_devices:

        mac = device.get("mac")

        # --------------------------
        # No MAC detected
        # --------------------------

        if not mac:

            device["status"] = "NO MAC"

            continue

        # --------------------------
        # New Device
        # --------------------------

        if mac not in previous_macs:

            device["status"] = "NEW"

            new_devices.append(device)

        else:

            device["status"] = "KNOWN"

    return new_devices


# ==============================
# Log New Devices
# ==============================

def log_new_devices(new_devices):

    if not new_devices:
        return

    with open(LOG_FILE, "a") as log:

        for device in new_devices:

            timestamp = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            log.write(
                f"[{timestamp}] NEW DEVICE | "
                f"IP: {device['ip']} | "
                f"MAC: {device['mac']} | "
                f"Vendor: {device['vendor']}\n"
            )


# ==============================
# Print Inventory Table
# ==============================

def print_inventory_table(devices):

    table_data = []

    for device in devices:

        table_data.append([
            device.get("ip"),
            device.get("mac"),
            device.get("vendor"),
            device.get("status")
        ])

    print("\n[+] Current Network Inventory:\n")

    print(tabulate(
        table_data,
        headers=[
            "IP Address",
            "MAC Address",
            "Vendor",
            "Status"
        ],
        tablefmt="grid"
    ))


# ==============================
# Main Program
# ==============================

def main():

    print("\n[+] Scanning network...\n")

    output = run_nmap_scan()

    current_devices = parse_nmap_output(output)

    previous_devices = load_previous_devices()

    new_devices = detect_new_devices(
        current_devices,
        previous_devices
    )

    # --------------------------
    # Print total devices
    # --------------------------

    print(
        f"[+] Devices found: "
        f"{len(current_devices)}"
    )

    # --------------------------
    # Print inventory
    # --------------------------

    print_inventory_table(current_devices)

    # --------------------------
    # Print new devices
    # --------------------------

    if new_devices:

        print("\n[!] New devices detected:\n")

        for device in new_devices:

            print(
                f"IP: {device['ip']} | "
                f"MAC: {device['mac']} | "
                f"Vendor: {device['vendor']}"
            )

    else:

        print("\n[+] No new devices detected.")

    # --------------------------
    # Save inventory
    # --------------------------

    save_devices(current_devices)

    # --------------------------
    # Save CSV
    # --------------------------

    save_csv(current_devices)

    # --------------------------
    # Save logs
    # --------------------------

    log_new_devices(new_devices)

    # --------------------------
    # Final status
    # --------------------------

    print(
        f"\n[+] Inventory saved to "
        f"{OUTPUT_FILE}"
    )

    print(
        f"[+] CSV report saved to "
        f"{CSV_FILE}"
    )

    print(
        f"[+] Event log saved to "
        f"{LOG_FILE}"
    )


# ==============================
# Program Entry
# ==============================

if __name__ == "__main__":
    main()
