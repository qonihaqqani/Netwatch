"""NetWatch settings.

Network-specific settings (gateway IP, subnet, targets) live in profiles/
and switch_network.py picks which one is active. Everything else that
doesn't change between networks (thresholds, Telegram, intervals) lives
here.

To switch networks:  python switch_network.py campus|hotspot|pdanet
"""
import importlib
import os

import switch_network

_profile_name = switch_network.current()
_profile = importlib.import_module(f"profiles.{_profile_name}")

TARGETS = _profile.TARGETS
WATCHED_PORTS = _profile.WATCHED_PORTS
LAN_SUBNET = _profile.LAN_SUBNET
ACTIVE_PROFILE = _profile_name

CHECK_INTERVAL_SEC = 30
PING_COUNT = 4

LATENCY_THRESHOLD_MS = 100
LOSS_THRESHOLD_PCT = 20

TELEGRAM_BOT_TOKEN = os.environ.get("NETWATCH_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("NETWATCH_CHAT_ID", "")

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "netwatch.db")

DEVICE_SCAN_INTERVAL_SEC = 120
PORT_TIMEOUT_SEC = 2
