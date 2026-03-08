from setuptools import setup, find_packages

setup(
    name="network-port-assistant",
    version="1.0.0",
    description="Python network reconnaissance tool for host discovery, MAC detection, vendor lookup, port scanning, and banner grabbing",
    author="profjlr-spec",
    packages=find_packages(),
    py_modules=["network_scan"],
    install_requires=[
        "netifaces",
    ],
    entry_points={
        "console_scripts": [
            "network-scan=network_scan:main",
        ],
    },
)
