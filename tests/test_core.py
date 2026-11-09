"""Offline regression checks for NetWatch's core monitoring paths."""
import tempfile
import unittest
import os
from pathlib import Path
from unittest.mock import patch

import db
import monitor
import simulate
import app as web_app
import test_scenarios


class NetWatchCoreTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.old_db_path = db.config.DB_PATH
        db.config.DB_PATH = str(Path(self.temp_dir.name) / "test.db")
        db.init_db()
        monitor.alert_state.clear()

    def tearDown(self):
        db.config.DB_PATH = self.old_db_path
        monitor.alert_state.clear()
        self.temp_dir.cleanup()

    def test_readings_persist_and_history_is_oldest_first(self):
        db.save_reading("test-host", "192.0.2.10", 20.0, 0.0, True)
        db.save_reading("test-host", "192.0.2.10", 30.0, 5.0, True)

        history = db.history("test-host")
        self.assertEqual([row["latency_ms"] for row in history], [20.0, 30.0])
        self.assertEqual(db.latest_status()[0]["loss_pct"], 5.0)

    @patch("monitor.send_telegram", return_value=(False, None))
    def test_host_down_and_recovery_create_edge_alerts(self, _send):
        monitor.check_ping_alerts("test-host", None, 100.0, False)
        monitor.check_ping_alerts("test-host", 25.0, 0.0, True)

        alerts = db.recent_alerts()
        self.assertEqual([row["kind"] for row in reversed(alerts)], ["host_down", "host_down_resolved"])

    @patch("monitor.send_telegram", return_value=(False, None))
    def test_expected_port_closure_and_recovery_are_recorded(self, _send):
        monitor.check_port_alerts("192.0.2.10", 443, False)
        monitor.check_port_alerts("192.0.2.10", 443, False)
        monitor.check_port_alerts("192.0.2.10", 443, True)

        alerts = db.recent_alerts()
        self.assertEqual([row["kind"] for row in reversed(alerts)], ["port_closed", "port_closed_resolved"])

    def test_device_and_port_snapshots_are_persisted(self):
        db.save_device_scan([{"ip": "192.0.2.10", "mac": "00:11:22:33:44:55", "hostname": None}])
        db.save_port_check("192.0.2.10", 443, True)

        self.assertEqual(db.latest_device_scan()["device_count"], 1)
        self.assertTrue(db.latest_port_checks()[0]["is_open"])

    @patch("monitor.send_telegram", side_effect=AssertionError("simulation must not send Telegram"))
    def test_simulation_uses_detection_path_and_is_labelled(self, _send):
        with patch.dict(os.environ, {"NETWATCH_DB_PATH": str(Path(self.temp_dir.name) / "high_latency.db")}):
            simulate.run_scenario("HIGH_LATENCY")

        with db.closing(db.connect()) as conn:
            reading = conn.execute("SELECT * FROM readings ORDER BY id DESC LIMIT 1").fetchone()
        self.assertEqual(reading["source"], "simulation")
        self.assertEqual(db.recent_alerts()[0]["source"], "simulation")

    @patch("monitor.send_telegram", return_value=(False, None))
    def test_new_port_state_creates_change_alert(self, _send):
        db.save_port_check("192.0.2.10", 443, True)
        monitor.record_port_result("192.0.2.10", 443, False)

        kinds = [row["kind"] for row in reversed(db.recent_alerts())]
        self.assertIn("port_change", kinds)
        self.assertIn("port_closed", kinds)

    @patch("monitor.send_telegram", return_value=(False, None))
    def test_unregistered_device_is_marked_and_alerted(self, _send):
        monitor.record_device_scan([{"ip": "192.0.2.10", "mac": "00:11:22:33:44:55"}])

        self.assertFalse(db.latest_device_scan()["devices"][0]["registered"])
        self.assertEqual(db.recent_alerts()[0]["kind"], "unknown_device")

    def test_existing_database_gets_source_column_migration(self):
        old_db_path = db.config.DB_PATH
        legacy_path = str(Path(self.temp_dir.name) / "legacy.db")
        try:
            db.config.DB_PATH = legacy_path
            with db.closing(db.connect()) as conn:
                conn.execute("CREATE TABLE readings (id INTEGER PRIMARY KEY, ts TEXT, target TEXT, address TEXT, latency_ms REAL, loss_pct REAL, is_up INTEGER)")
                conn.commit()
            db.init_db()
            with db.closing(db.connect()) as conn:
                columns = {row["name"] for row in conn.execute("PRAGMA table_info(readings)")}
            self.assertIn("source", columns)
        finally:
            db.config.DB_PATH = old_db_path

    def test_status_api_exposes_monitoring_and_data_origin(self):
        db.save_reading("test-host", "192.0.2.10", 12.5, 0.0, True, source="simulation")
        response = web_app.app.test_client().get("/api/status")

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["targets"][0]["source"], "simulation")
        self.assertEqual(payload["targets"][0]["target"], "test-host")

    @patch("monitor.send_telegram", side_effect=AssertionError("simulation must not send Telegram"))
    def test_all_six_simulation_modes(self, _send):
        expected_alerts = {
            "NORMAL": None,
            "HIGH_LATENCY": "high_latency",
            "PACKET_LOSS": "packet_loss",
            "HOST_DOWN": "host_down",
            "UNKNOWN_DEVICE": "unknown_device",
            "PORT_CHANGE": "port_change",
        }
        for mode, expected_kind in expected_alerts.items():
            with self.subTest(mode=mode):
                path = Path(self.temp_dir.name) / f"{mode}.db"
                with patch.dict(os.environ, {"NETWATCH_DB_PATH": str(path)}):
                    simulate.run_scenario(mode)
                    alerts = db.recent_alerts(limit=50)
                    kinds = [row["kind"] for row in alerts]
                    if expected_kind:
                        self.assertIn(expected_kind, kinds)
                        self.assertTrue(all(row["source"] == "simulation" for row in alerts))
                    else:
                        self.assertEqual(alerts, [])

    @patch("test_scenarios.input", side_effect=["", ""])
    @patch("test_scenarios.time.sleep", return_value=None)
    @patch("monitor.send_telegram", return_value=(False, None))
    @patch("monitor.ping", side_effect=[(20.0, 0.0), (25.0, 0.0), (None, 100.0), (None, 100.0), (22.0, 0.0)])
    def test_controlled_fault_scenario_persists_down_and_recovery(self, _ping, _send, _sleep, _input):
        with patch.object(test_scenarios.config, "TARGETS", {"test-host": "192.0.2.10"}):
            test_scenarios.scenario_b_induced_fault("test-host", timeout_sec=5, poll_interval_sec=0)

        kinds = [row["kind"] for row in reversed(db.recent_alerts())]
        self.assertEqual(kinds, ["host_down", "host_down_resolved"])
        with db.closing(db.connect()) as conn:
            reading_count = conn.execute("SELECT COUNT(*) FROM readings").fetchone()[0]
        self.assertEqual(reading_count, 5)


if __name__ == "__main__":
    unittest.main()
