import subprocess
import re


def run_command(cmd: list[str]) -> str:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Error running command: {e}"


def get_default_interface() -> str | None:
    output = run_command(["ip", "route"])
    for line in output.splitlines():
        if line.startswith("default"):
            parts = line.split()
            if "dev" in parts:
                return parts[parts.index("dev") + 1]
    return None


def get_ip_address(interface: str) -> str:
    output = run_command(["ip", "-4", "addr", "show", interface])
    match = re.search(r"inet (\d+\.\d+\.\d+\.\d+)", output)
    return match.group(1) if match else "Unknown"


def get_mac_address(interface: str) -> str:
    output = run_command(["ip", "link", "show", interface])
    match = re.search(r"link/\w+ ([0-9a-f:]{17})", output, re.IGNORECASE)
    return match.group(1) if match else "Unknown"


def get_gateway() -> str:
    output = run_command(["ip", "route"])
    for line in output.splitlines():
        if line.startswith("default"):
            parts = line.split()
            if len(parts) >= 3:
                return parts[2]
    return "Unknown"


def get_dns_servers() -> list[str]:
    dns_servers = []
    try:
        with open("/etc/resolv.conf", "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("nameserver"):
                    parts = line.split()
                    if len(parts) == 2:
                        dns_servers.append(parts[1])
    except Exception:
        pass
    return dns_servers


def get_link_info(interface: str) -> tuple[str, str, str]:
    output = run_command(["ethtool", interface])

    speed_match = re.search(r"Speed:\s+(.+)", output)
    duplex_match = re.search(r"Duplex:\s+(.+)", output)
    link_match = re.search(r"Link detected:\s+(.+)", output)

    speed = speed_match.group(1).strip() if speed_match else "Unknown"
    duplex = duplex_match.group(1).strip() if duplex_match else "Unknown"
    link = link_match.group(1).strip() if link_match else "Unknown"

    return speed, duplex, link


def main() -> None:
    print("\nNetwork Port Assistant")
    print("=" * 30)

    interface = get_default_interface()

    if not interface:
        print("Could not detect active network interface.")
        return

    ip = get_ip_address(interface)
    mac = get_mac_address(interface)
    gateway = get_gateway()
    dns_servers = get_dns_servers()
    speed, duplex, link = get_link_info(interface)

    print(f"Interface   : {interface}")
    print(f"Link Status : {link}")
    print(f"Speed       : {speed}")
    print(f"Duplex      : {duplex}")
    print(f"IP Address  : {ip}")
    print(f"MAC Address : {mac}")
    print(f"Gateway     : {gateway}")

    if dns_servers:
        print(f"DNS Server(s): {', '.join(dns_servers)}")
    else:
        print("DNS Server(s): Unknown")


if __name__ == "__main__":
    main()
