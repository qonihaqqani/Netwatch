"""NetWatch dashboard. Run: python app.py  then open http://localhost:5000"""
from datetime import datetime

from flask import Flask, jsonify, render_template

import config
import db

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/status")
def api_status():
    targets = db.latest_status()
    for t in targets:
        t["age_sec"] = int((datetime.now() - datetime.fromisoformat(t["ts"])).total_seconds())
        t["history"] = db.history(t["target"], limit=40)

    device_scan = db.latest_device_scan()
    if device_scan["ts"]:
        device_scan["age_sec"] = int((datetime.now() - datetime.fromisoformat(device_scan["ts"])).total_seconds())
    else:
        device_scan["age_sec"] = None

    return jsonify(
        {
            "targets": targets,
            "alerts": db.recent_alerts(),
            "device_scan": device_scan,
            "ports": db.latest_port_checks(),
            "active_profile": config.ACTIVE_PROFILE,
            "thresholds": {
                "latency_ms": config.LATENCY_THRESHOLD_MS,
                "loss_pct": config.LOSS_THRESHOLD_PCT,
                "stale_after_sec": config.CHECK_INTERVAL_SEC * 3,
            },
        }
    )


if __name__ == "__main__":
    db.init_db()
    app.run(host="0.0.0.0", port=5000)
