"""Settings for PdaNet tethering at the rental house.

PdaNet's gateway is usually the phone's USB/Bluetooth tether IP - check with
ip route | grep default (Linux/Pi) or ipconfig (Windows) once connected,
since it varies by PdaNet version and connection type (USB/wifi/Bluetooth).
"""
GATEWAY = "192.168.49.1"
LAN_SUBNET = "192.168.49.0/24"

TARGETS = {
    "PdaNet gateway": GATEWAY,
    "Google DNS": "8.8.8.8",
    "Cloudflare DNS": "1.1.1.1",
}

WATCHED_PORTS = {}
