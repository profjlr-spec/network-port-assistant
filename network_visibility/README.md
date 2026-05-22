# Network Visibility Tool

A Python-based network discovery and monitoring tool designed for learning:

- Linux
- Networking
- Python
- Automation
- Blue Team fundamentals

The tool performs network discovery using Nmap and generates:

- Network inventory
- Device status tracking
- CSV reports
- Event logging
- New device detection

---

# Features

## Network Discovery

Scans the local network using:

```bash
nmap -sn
```

Detects:

- IP addresses
- MAC addresses
- Vendors
- Active devices

---

# Device Status

The tool identifies:

| Status | Meaning |
|---|---|
| KNOWN | Previously detected device |
| NEW | New device detected |
| NO MAC | Device responded without MAC info |

---

# Output Files

## devices.json

Stores full inventory in JSON format.

## devices.csv

CSV export for reports and spreadsheets.

## network_events.log

Logs newly detected devices with timestamps.

Example:

```text
[2026-05-21 20:08:05] NEW DEVICE | IP: 192.168.1.252 | MAC: A0:92:08:E9:69:89 | Vendor: Tuya Smart
```

---

# Requirements

Install Nmap:

```bash
sudo apt install nmap
```

Activate virtual environment:

```bash
source ../venv/bin/activate
```

Install dependencies:

```bash
pip install tabulate
```

---

# Run the Tool

```bash
python3 device_discovery.py
```

---

# Example Output

```text
+---------------+-------------------+-------------------+----------+
| IP Address    | MAC Address       | Vendor            | Status   |
+---------------+-------------------+-------------------+----------+
| 192.168.1.66  | 44:61:32:38:51:28 | ecobee           | KNOWN    |
+---------------+-------------------+-------------------+----------+
```

---

# Learning Objectives

This project helps develop skills in:

- Python scripting
- Network discovery
- Linux administration
- Packet analysis
- Automation
- Cybersecurity fundamentals

---

# Future Improvements

- Flask dashboard
- Real-time monitoring
- Suricata integration
- Email alerts
- Device fingerprinting
- Traffic analysis
- SQLite database
- Web UI

---

# Project Structure

```text
network_visibility/
├── device_discovery.py
├── devices.json
├── devices.csv
├── network_events.log
└── README.md
```

---

# Author

Juan Ramos
