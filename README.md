# Network Port Assistant

Network Port Assistant is a Python-based network reconnaissance tool designed to discover devices on a local network and identify basic service information.

The tool performs host discovery, MAC address detection, vendor identification, and scans common open ports on active hosts.

This project is intended as a learning tool for networking, cybersecurity, and Python scripting.

---

## Features

- Automatic network interface detection
- IPv4 network calculation
- Multithreaded host discovery
- Hostname resolution
- MAC address detection
- Vendor identification (based on MAC OUI)
- Common port scanning
- JSON export of results
- Interactive CLI menu
- Command line argument support

---

## Technologies Used

- Python 3
- `netifaces`
- `socket`
- `ipaddress`
- `argparse`
- `ThreadPoolExecutor`

---

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/network-port-assistant.git
cd network-port-assistant
