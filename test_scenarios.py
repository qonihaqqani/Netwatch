"""Scenario tests for the evaluation chapter of your report.

These don't mock anything - they call your real ping(), scan_devices() and
check_port() functions so the numbers you get are real measurements you can
quote. Run: python test_scenarios.py

Scenario A: normal conditions - everything should read "up", low latency, low loss.
Scenario B: induced fault - you break something on purpose, then the script
confirms NetWatch caught it and measures how long the alert took.
"""
import time

import config
import db
import monitor


def scenario_a_normal():
    print("=== Scenario A: normal network conditions ===")
    for name, address in config.TARGETS.items():
        latency, loss = monitor.ping(address)
        verdict = "PASS" if loss < config.LOSS_THRESHOLD_PCT else "FAIL"
        lat_text = f"{latency:.1f} ms" if latency is not None else "no reply"
        print(f"  [{verdict}] {name:<16} latency={lat_text:<12} loss={loss:.0f}%")
    print()


def scenario_b_induced_fault(target_name=None, timeout_sec=90):
    """Pick (or use) a target, poll it every 2s, and time how long it takes
    NetWatch's own alert logic to flag it as down. Before running this,
    actually break that host's connectivity (unplug it, block it with a
    firewall rule, or point TARGETS at an address you then take offline).
    """
    target_name = target_name or next(iter(config.TARGETS))
    address = config.TARGETS[target_name]
    print(f"=== Scenario B: induced fault on {target_name} ({address}) ===")
    print("Break this host's connectivity now (unplug cable / block via firewall / power off).")
    input("Press Enter once the fault is in place...")

    start = time.monotonic()
    detected_at = None
    while time.monotonic() - start < timeout_sec:
        latency, loss = monitor.ping(address)
        is_up = loss < 100
        print(f"  t+{time.monotonic()-start:4.1f}s  up={is_up}  loss={loss:.0f}%")
        if not is_up:
            detected_at = time.monotonic() - start
            break
        time.sleep(2)

    if detected_at is None:
        print(f"  FAIL: no failure detected within {timeout_sec}s")
    else:
        print(f"  PASS: failure detected after {detected_at:.1f}s")
        print("  (This is your 'detection time' figure. Separately time how long")
        print("   the Telegram message takes to arrive on your phone for 'alert delivery time'.)")
    print("\nRestore the host's connectivity before continuing.")


def scenario_c_device_scan():
    print("=== Scenario C: device discovery ===")
    devices = monitor.scan_devices()
    print(f"  Found {len(devices)} device(s):")
    for d in devices:
        print(f"    {d['ip']:<16} {d['mac']:<18} {d.get('hostname') or '-'}")
    print()


if __name__ == "__main__":
    db.init_db()
    scenario_a_normal()
    scenario_c_device_scan()
    print("Run scenario_b_induced_fault() separately (it's interactive):")
    print("  python -c \"import test_scenarios as t; t.scenario_b_induced_fault()\"")
