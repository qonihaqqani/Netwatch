"""Settings for phone mobile-data hotspot (your phone is the router).

Fill in GATEWAY once connected - common defaults:
  Android hotspot: 192.168.43.1
  iPhone hotspot:  172.20.10.1
Confirm with: ip route | grep default  (Linux/Pi) or ipconfig (Windows)
"""
GATEWAY = "192.168.43.1"
LAN_SUBNET = "192.168.43.0/24"

TARGETS = {
    "Phone hotspot": GATEWAY,
    "Google DNS": "8.8.8.8",
    "Cloudflare DNS": "1.1.1.1",
}

# This is your own private network, so device discovery will show exactly
# what's connected (likely just your laptop + Pi) - no client isolation here.
WATCHED_PORTS = {}
