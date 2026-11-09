"""NetWatch monitoring agent: ping, device discovery, port checks, alerts.

Run:  python monitor.py          (loops forever)
      python monitor.py --once   (one round of everything, for testing)
"""
import platform
import re
import socket
import subprocess
import sys
import time
import urllib.parse
import urllib.request

import config
import db

IS_WINDOWS = platform.system() == "Windows"
alert_state = {}  # (target, kind) -> True while that problem is active


# ---------- ping ----------

def ping(address):
    """Return (avg_latency_ms or None, loss_pct)."""
    if IS_WINDOWS:
        cmd = ["ping", "-n", str(config.PING_COUNT), "-w", "1000", address]
    else:
        cmd = ["ping", "-c", str(config.PING_COUNT), "-W", "1", address]
    try:
        out = subprocess.run(
            cmd, capture_output=True, text=True, timeout=config.PING_COUNT * 3 + 5
        ).stdout
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None, 100.0

    if IS_WINDOWS and "TTL=" not in out:
        return None, 100.0

    loss_match = re.search(r"(\d+(?:\.\d+)?)%\s*(?:packet\s+)?loss", out)
    loss = float(loss_match.group(1)) if loss_match else 100.0

    latency = None
    m = re.search(r"=\s*[\d.]+/([\d.]+)/[\d.]+", out)
    if m:
        latency = float(m.group(1))
    else:
        m = re.search(r"Average = (\d+)ms", out)
        if m:
            latency = float(m.group(1))
    return latency, loss


# ---------- device discovery ----------

def scan_devices():
    """ARP-scan the LAN. Prefers `arp -a` (no special privileges, works on Pi/Win/Mac)
    over nmap, since nmap -sn needs sudo for a full ping sweep on most systems."""
    devices = []
    try:
        if IS_WINDOWS:
            out = subprocess.run(["arp", "-a"], capture_output=True, text=True, timeout=10).stdout
            for line in out.splitlines():
                m = re.match(r"\s*([\d.]+)\s+([0-9a-fA-F-]{17})\s+(\w+)", line)
                if m and m.group(3).lower() == "dynamic":
                    devices.append({"ip": m.group(1), "mac": m.group(2)})
        else:
            out = subprocess.run(["arp", "-an"], capture_output=True, text=True, timeout=10).stdout
            for line in out.splitlines():
                m = re.search(r"\(([\d.]+)\) at ([0-9a-fA-F:]{17})", line)
                if m:
                    devices.append({"ip": m.group(1), "mac": m.group(2)})
    except FileNotFoundError:
        print("    'arp' command not found; device discovery skipped.")
        return []

    for d in devices:
        try:
            d["hostname"] = socket.gethostbyaddr(d["ip"])[0]
        except (socket.herror, socket.gaierror, OSError):
            d["hostname"] = None
    return devices


# ---------- port checks ----------

def check_port(address, port):
    try:
        with socket.create_connection((address, port), timeout=config.PORT_TIMEOUT_SEC):
            return True
    except OSError:
        return False


# ---------- telegram + alerts ----------

def send_telegram(text):
    if not (config.TELEGRAM_BOT_TOKEN and config.TELEGRAM_CHAT_ID):
        return False, None
    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": config.TELEGRAM_CHAT_ID, "text": text}).encode()
    start = time.monotonic()
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=10) as resp:
            ok = resp.status == 200
    except Exception as e:
        print(f"    Telegram send failed: {e}")
        return False, None
    return ok, int((time.monotonic() - start) * 1000)


def raise_alert(target, kind, message):
    print(f"    >> {message}")
    sent, delay = send_telegram(f"NetWatch: {message}")
    db.save_alert(target, kind, message, sent, delay)


def set_alert(name, kind, active, active_message, resolved_message):
    was_active = alert_state.get((name, kind), False)
    if active and not was_active:
        raise_alert(name, kind, f"ALERT: {active_message}")
    elif was_active and not active:
        raise_alert(name, kind + "_resolved", f"RESOLVED: {resolved_message}")
    alert_state[(name, kind)] = active


def check_ping_alerts(name, latency, loss, is_up):
    set_alert(name, "host_down", not is_up,
              f"{name} is unreachable", f"{name} is back online")
    set_alert(name, "high_latency", is_up and latency is not None and latency > config.LATENCY_THRESHOLD_MS,
              f"{name} latency is {latency:.0f} ms (limit {config.LATENCY_THRESHOLD_MS} ms)" if latency else "",
              f"{name} latency is back under {config.LATENCY_THRESHOLD_MS} ms")
    set_alert(name, "packet_loss", is_up and loss > config.LOSS_THRESHOLD_PCT,
              f"{name} packet loss is {loss:.0f}% (limit {config.LOSS_THRESHOLD_PCT}%)",
              f"{name} packet loss is back under {config.LOSS_THRESHOLD_PCT}%")


def check_port_alerts(address, port, is_open):
    label = f"{address}:{port}"
    set_alert(label, "port_closed", not is_open,
              f"port {port} on {address} is closed (expected open)",
              f"port {port} on {address} is open again")


# ---------- rounds ----------

def run_ping_round():
    for name, address in config.TARGETS.items():
        latency, loss = ping(address)
        is_up = loss < 100
        db.save_reading(name, address, latency, loss, is_up)
        lat_text = f"{latency:.1f} ms" if latency is not None else "-"
        print(f"{db.now()}  {name:<16} {address:<15} up={is_up!s:<5} latency={lat_text:<10} loss={loss:.0f}%")
        check_ping_alerts(name, latency, loss, is_up)


def run_port_round():
    for address, ports in config.WATCHED_PORTS.items():
        for port in ports:
            is_open = check_port(address, port)
            db.save_port_check(address, port, is_open)
            print(f"{db.now()}  port {address}:{port:<6} open={is_open}")
            check_port_alerts(address, port, is_open)


def run_device_scan():
    devices = scan_devices()
    db.save_device_scan(devices)
    print(f"{db.now()}  device scan: {len(devices)} device(s) on the LAN")


def run_once():
    run_ping_round()
    run_port_round()
    run_device_scan()


def main():
    db.init_db()
    if "--once" in sys.argv:
        run_once()
        return
    print("NetWatch monitor running. Press Ctrl+C to stop.")
    if not (config.TELEGRAM_BOT_TOKEN and config.TELEGRAM_CHAT_ID):
        print("(Telegram not configured: alerts will only be printed and saved.)")
    last_device_scan = 0.0
    while True:
        started = time.monotonic()
        run_ping_round()
        run_port_round()
        if started - last_device_scan >= config.DEVICE_SCAN_INTERVAL_SEC:
            run_device_scan()
            last_device_scan = started
        time.sleep(max(1, config.CHECK_INTERVAL_SEC - (time.monotonic() - started)))


if __name__ == "__main__":
    main()
