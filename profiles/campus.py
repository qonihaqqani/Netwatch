"""Settings for campus/student wifi (e.g. eduroam).

Fill in GATEWAY once you're connected on campus:
  Linux/Pi/Mac: ip route | grep default
  Windows:      ipconfig  (look for 'Default Gateway')
"""
GATEWAY = "10.0.0.1"          # <-- replace with campus gateway IP
LAN_SUBNET = "10.0.0.0/24"    # <-- replace with campus subnet if known; device scan still works without this being exact

TARGETS = {
    "Campus gateway": GATEWAY,
    "Google DNS": "8.8.8.8",
    "Cloudflare DNS": "1.1.1.1",
}

# Most campus wifi isolates clients from each other for security, so expect
# the device scan to show very few devices here - that's the network's
# policy, not a bug. Worth a line in your report's limitations section.
WATCHED_PORTS = {}

# Add the MAC addresses of devices you trust on this network. Any discovered
# MAC not listed here is reported as unregistered. Keep this list network-specific.
KNOWN_DEVICE_MACS = set()
