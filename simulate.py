"""Run one labelled, offline Scenario B event through NetWatch's normal logic.

Examples:
    py simulate.py NORMAL
    py simulate.py HIGH_LATENCY
    py simulate.py PACKET_LOSS
    py simulate.py HOST_DOWN
    py simulate.py UNKNOWN_DEVICE
    py simulate.py PORT_CHANGE

Simulation records use a separate SQLite database by default and never send
Telegram messages. Point the dashboard at that same database to view results:
    $env:NETWATCH_DB_PATH = "$PWD/netwatch_simulation.db"
    py app.py
"""
import argparse
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent

import config  # noqa: E402
import db  # noqa: E402
import monitor  # noqa: E402


SCENARIOS = ("NORMAL", "HIGH_LATENCY", "PACKET_LOSS", "HOST_DOWN", "UNKNOWN_DEVICE", "PORT_CHANGE")
SIM_TARGET = "192.0.2.1"  # TEST-NET-1: reserved for documentation, not a real endpoint.
SIM_PORT = 443


def run_scenario(name):
    """Persist a deterministic event using the same record and alert paths."""
    name = name.upper()
    if name not in SCENARIOS:
        raise ValueError(f"Unknown scenario: {name}")

    # Keep each default scenario isolated so an earlier synthetic event cannot
    # become the baseline for a later run. An explicit env path can be used
    # when a combined simulation database is desired.
    if "NETWATCH_DB_PATH" not in os.environ:
        config.DB_PATH = str(ROOT / f"netwatch_simulation_{name.lower()}.db")
    else:
        config.DB_PATH = os.environ["NETWATCH_DB_PATH"]

    db.init_db()
    monitor.alert_state.clear()
    if name == "NORMAL":
        monitor.record_ping_result("Simulation target", SIM_TARGET, 24.0, 0.0, source="simulation")
        monitor.record_device_scan([], source="simulation")
        monitor.record_port_result(SIM_TARGET, SIM_PORT, True, source="simulation")
    elif name == "HIGH_LATENCY":
        monitor.record_ping_result("Simulation target", SIM_TARGET, config.LATENCY_THRESHOLD_MS + 50.0, 0.0,
                                   source="simulation")
    elif name == "PACKET_LOSS":
        monitor.record_ping_result("Simulation target", SIM_TARGET, 80.0,
                                   min(99.0, config.LOSS_THRESHOLD_PCT + 25.0), source="simulation")
    elif name == "HOST_DOWN":
        monitor.record_ping_result("Simulation target", SIM_TARGET, None, 100.0, source="simulation")
    elif name == "UNKNOWN_DEVICE":
        monitor.record_device_scan([
            {"ip": "192.0.2.50", "mac": "02:00:5e:10:00:01", "hostname": "simulation-device"}
        ], source="simulation")
    elif name == "PORT_CHANGE":
        # Seed a normal baseline, then submit the changed state via the detector.
        db.save_port_check(SIM_TARGET, SIM_PORT, True, source="simulation")
        monitor.record_port_result(SIM_TARGET, SIM_PORT, False, source="simulation")

    print(f"{name} simulation saved to: {config.DB_PATH}")
    print("All records are labelled SIMULATED; no live network probes or Telegram sends were made.")


def main():
    parser = argparse.ArgumentParser(description="Exercise a labelled NetWatch simulation scenario.")
    parser.add_argument("scenario", choices=SCENARIOS, type=str.upper)
    args = parser.parse_args()
    run_scenario(args.scenario)


if __name__ == "__main__":
    main()
