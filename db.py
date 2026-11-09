"""All SQLite access lives here so every other module shares one schema."""
import sqlite3
from contextlib import closing
from datetime import datetime

import config


def now():
    return datetime.now().isoformat(timespec="seconds")


def connect():
    conn = sqlite3.connect(config.DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    with closing(connect()) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                target TEXT NOT NULL,
                address TEXT NOT NULL,
                latency_ms REAL,
                loss_pct REAL NOT NULL,
                is_up INTEGER NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_readings_target ON readings(target, id);

            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                target TEXT NOT NULL,
                kind TEXT NOT NULL,
                message TEXT NOT NULL,
                telegram_sent INTEGER NOT NULL DEFAULT 0,
                telegram_delay_ms INTEGER
            );

            CREATE TABLE IF NOT EXISTS device_scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                device_count INTEGER NOT NULL,
                devices_json TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS port_checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                address TEXT NOT NULL,
                port INTEGER NOT NULL,
                is_open INTEGER NOT NULL
            );
            """
        )
        conn.commit()


def save_reading(target, address, latency_ms, loss_pct, is_up):
    with closing(connect()) as conn:
        conn.execute(
            "INSERT INTO readings (ts, target, address, latency_ms, loss_pct, is_up) VALUES (?,?,?,?,?,?)",
            (now(), target, address, latency_ms, loss_pct, int(is_up)),
        )
        conn.commit()


def save_alert(target, kind, message, telegram_sent, telegram_delay_ms):
    with closing(connect()) as conn:
        conn.execute(
            "INSERT INTO alerts (ts, target, kind, message, telegram_sent, telegram_delay_ms) VALUES (?,?,?,?,?,?)",
            (now(), target, kind, message, int(telegram_sent), telegram_delay_ms),
        )
        conn.commit()


def save_device_scan(devices):
    import json
    with closing(connect()) as conn:
        conn.execute(
            "INSERT INTO device_scans (ts, device_count, devices_json) VALUES (?,?,?)",
            (now(), len(devices), json.dumps(devices)),
        )
        conn.commit()


def save_port_check(address, port, is_open):
    with closing(connect()) as conn:
        conn.execute(
            "INSERT INTO port_checks (ts, address, port, is_open) VALUES (?,?,?,?)",
            (now(), address, port, int(is_open)),
        )
        conn.commit()


def latest_status():
    with closing(connect()) as conn:
        rows = conn.execute(
            """
            SELECT r.* FROM readings r
            JOIN (SELECT target, MAX(id) AS max_id FROM readings GROUP BY target) m
              ON r.id = m.max_id
            ORDER BY r.target
            """
        ).fetchall()
    return [dict(r) for r in rows]


def recent_alerts(limit=20):
    with closing(connect()) as conn:
        rows = conn.execute("SELECT * FROM alerts ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return [dict(r) for r in rows]


def latest_device_scan():
    import json
    with closing(connect()) as conn:
        row = conn.execute("SELECT * FROM device_scans ORDER BY id DESC LIMIT 1").fetchone()
    if not row:
        return {"ts": None, "device_count": 0, "devices": []}
    d = dict(row)
    d["devices"] = json.loads(d.pop("devices_json"))
    return d


def latest_port_checks():
    """Most recent open/closed result for every (address, port) pair we've checked."""
    with closing(connect()) as conn:
        rows = conn.execute(
            """
            SELECT p.* FROM port_checks p
            JOIN (SELECT address, port, MAX(id) AS max_id FROM port_checks GROUP BY address, port) m
              ON p.id = m.max_id
            ORDER BY p.address, p.port
            """
        ).fetchall()
    return [dict(r) for r in rows]


def history(target, limit=50):
    """Latency history for one target, oldest first, for graphing."""
    with closing(connect()) as conn:
        rows = conn.execute(
            "SELECT ts, latency_ms, loss_pct FROM readings WHERE target = ? ORDER BY id DESC LIMIT ?",
            (target, limit),
        ).fetchall()
    return [dict(r) for r in reversed(rows)]
