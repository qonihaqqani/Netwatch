"""Switch which network profile NetWatch uses.

Usage:
    python switch_network.py campus
    python switch_network.py hotspot
    python switch_network.py pdanet
    python switch_network.py           (shows the current profile)

Run this once each time you change networks, before starting monitor.py
and app.py. It just writes a text file; it doesn't touch anything else.
"""
import sys

ACTIVE_FILE = "active_profile.txt"
VALID = {"campus", "hotspot", "pdanet"}


def current():
    try:
        with open(ACTIVE_FILE) as f:
            return f.read().strip()
    except FileNotFoundError:
        return "campus"  # default


def main():
    if len(sys.argv) < 2:
        print(f"Current profile: {current()}")
        print(f"Valid profiles: {', '.join(sorted(VALID))}")
        return
    name = sys.argv[1].strip().lower()
    if name not in VALID:
        print(f"Unknown profile '{name}'. Valid: {', '.join(sorted(VALID))}")
        sys.exit(1)
    with open(ACTIVE_FILE, "w") as f:
        f.write(name)
    print(f"Switched to profile: {name}")
    print("Now (re)start monitor.py and app.py for it to take effect.")


if __name__ == "__main__":
    main()
