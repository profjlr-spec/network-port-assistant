# Network Port Assistant

![Python](https://img.shields.io/badge/Python-3.x-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

Network Port Assistant is a Python-based network visibility and validation tool designed to help IT professionals identify active devices on a local network, review basic service exposure, and export results for troubleshooting and operational documentation.

This project is intended for practical IT operations use cases such as local subnet discovery, deployment validation, quick port checks, and small network inventory collection.

---

## What It Does

Network Port Assistant helps you:

- Discover active hosts on a local IPv4 subnet
- Detect hostnames when available
- Retrieve MAC addresses from the local ARP table
- Provide basic vendor hints from MAC OUI prefixes
- Estimate operating system family using TTL-based heuristics
- Scan common ports or a custom port range
- Perform basic service banner grabbing
- Export results to JSON and CSV

---

## Typical Use Cases

This tool is useful for:

- Validating network connectivity after workstation deployment
- Identifying active devices during troubleshooting
- Performing quick local network visibility checks
- Creating a lightweight inventory of devices on a subnet
- Supporting field IT work, tech refresh, and operational documentation
- Practicing Python, networking, and automation with a real-world tool

---

## Features

- Automatic network interface selection
- IPv4 network calculation
- Multithreaded host discovery
- Hostname resolution
- MAC address detection
- Basic vendor identification
- Basic OS guessing from TTL behavior
- Common port scanning
- Custom port range scanning
- Basic service banner grabbing
- JSON and CSV export
- Interactive CLI menu
- Command-line argument support
- Scan progress indicators
- End-of-scan summary

---

## Project Scope

This tool is focused on **authorized local network assessment** and **basic operational visibility**.

It is **not** intended to replace enterprise scanners or advanced network security tools. Its value is in being simple, readable, practical, and useful for day-to-day IT troubleshooting and validation workflows.

---

## Limitations

To keep expectations realistic, this project currently has some important limitations:

- Operating system detection is only a **heuristic guess** based on TTL values
- Vendor identification depends on a **small local OUI mapping**
- MAC address discovery relies on the local ARP table
- Banner grabbing is basic and may not work on all services
- Performance is best on small to medium local subnets
- The tool should only be used on networks you are authorized to assess

---

## Installation

Clone the repository:

```bash
git clone https://github.com/profjlr-spec/network-port-assistant.git
cd network-port-assistant
