"""Field scenarios for the evaluation chapter.

These use real network observations and persist them to SQLite. Record the
actual platform/network; Windows results are not Raspberry Pi results.
Run: python test_scenarios.py
"""
import time

import config
import db
import monitor


def scenario_a_normal():
    """Collect and persist a baseline round for configured targets."""
    print("=== Scenario A: normal network conditions ===")
    for name, address in config.TARGETS.items():
        latency, loss = monitor.ping(address)
        monitor.record_ping_result(name, address, latency, loss)
        verdict = "PASS" if loss < config.LOSS_THRESHOLD_PCT else "FAIL"
        lat_text = f"{latency:.1f} ms" if latency is not None else "no reply"
        print(f"  [{verdict}] {name:<16} latency={lat_text:<12} loss={loss:.0f}%")
    print("Baseline readings and any alerts are saved to SQLite.\n")


def scenario_b_induced_fault(target_name=None, timeout_sec=90, poll_interval_sec=2):
    """Measure detection and recovery for one reachable, authorized host."""
    target_name = target_name or next(iter(config.TARGETS))
    address = config.TARGETS[target_name]
    print(f"=== Scenario B: induced fault on {target_name} ({address}) ===")
    latency, loss = monitor.ping(address)
    if loss >= 100:
        print("FAIL: selected target is already unreachable. Choose a reachable authorized test host.")
        return
    monitor.record_ping_result(target_name, address, latency, loss)
    print("Temporarily disconnect or block this authorized test host. Do not target devices you do not administer.")
    input("Press Enter once the fault is in place...")

    start = time.monotonic()
    detected_at = None
    while time.monotonic() - start < timeout_sec:
        latency, loss = monitor.ping(address)
        is_up = loss < 100
        monitor.record_ping_result(target_name, address, latency, loss)
        print(f"  t+{time.monotonic()-start:4.1f}s  up={is_up}  loss={loss:.0f}%")
        if not is_up:
            detected_at = time.monotonic() - start
            break
        time.sleep(poll_interval_sec)

    if detected_at is None:
        print(f"FAIL: no failure detected within {timeout_sec}s")
        return

    print(f"PASS: failure detected after {detected_at:.1f}s")
    print("Measure phone receipt separately for alert delivery time; the API response time is not phone receipt time.")
    input("Restore the test host now, then press Enter...")
    recovery_start = time.monotonic()
    while time.monotonic() - recovery_start < timeout_sec:
        latency, loss = monitor.ping(address)
        monitor.record_ping_result(target_name, address, latency, loss)
        if loss < 100:
            print(f"Recovery detected after {time.monotonic()-recovery_start:.1f}s")
            break
        time.sleep(poll_interval_sec)
    else:
        print(f"Recovery not detected within {timeout_sec}s")
    print("Scenario readings and alerts are saved to the configured SQLite database.")


def scenario_c_device_scan():
    """Save a real ARP-cache scan and report registered/unregistered devices."""
    print("=== Scenario C: device discovery ===")
    devices = monitor.scan_devices()
    monitor.record_device_scan(devices)
    print(f"  Found {len(devices)} cached neighbor(s):")
    for d in devices:
        label = "registered" if d.get("registered") else "unregistered"
        print(f"    {d['ip']:<16} {d['mac']:<18} {d.get('hostname') or '-':<32} {label}")
    print("The ARP cache may omit devices that have not communicated recently.\n")


if __name__ == "__main__":
    db.init_db()
    scenario_a_normal()
    scenario_c_device_scan()
    print("Run the controlled fault scenario separately against a reachable, authorized host:")
    print('  python -c "import test_scenarios as t; t.scenario_b_induced_fault(\"YOUR_CONFIGURED_TEST_HOST\")"')
