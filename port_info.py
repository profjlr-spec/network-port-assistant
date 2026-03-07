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
    match = re.search(r"link/\w+ ([0-9a-f:]{17})", output)
    return match.group(1) if match else "Unknown"


def get_gateway() -> str:
    output = run_command(["ip", "route"])
    for line in output.splitlines():
        if line.startswith("default"):
            return line.split()[2]
    return "Unknown"


def get_link_info(interface: str) -> tuple[str, str, str]:
    output = run_command(["ethtool", interface])

    speed_match = re.search(r"Speed:\s+(.+)", output)
    duplex_match = re.search(r"Duplex:\s+(.+)", output)
    link_match = re.search(r"Link detected:\s+(.+)", output)

    speed = speed_match.group(1) if speed_match else "Unknown"
    duplex = duplex_match.group(1) if duplex_match else "Unknown"
    link = link_match.group(1) if link_match else "Unknown"

    return speed, duplex, link


def main():
    print("\nNetwork Port Assistant\n")

    interface = get_default_interface()

    if not interface:
        print("Could not detect active network interface.")
        return

    ip = get_ip_address(interface)
    mac = get_mac_address(interface)
    gateway = get_gateway()
    speed, duplex, link = get_link_info(interface)

    print(f"Interface: {interface}")
    print(f"Link Status: {link}")
    print(f"Speed: {speed}")
    print(f"Duplex: {duplex}")
    print(f"IP Address: {ip}")
    print(f"MAC Address: {mac}")
    print(f"Gateway: {gateway}")


if __name__ == "__main__":
    main()
