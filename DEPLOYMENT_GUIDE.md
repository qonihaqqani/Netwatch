# NetWatch Deployment Guide

## Current status

Deployment on Raspberry Pi 3 Model B+ is not verified. Use this guide as a preparation checklist; record actual OS and dependency versions during deployment.

## Preparation

1. Confirm the Pi 3 Model B+, power supply, storage, and authorized test LAN are available.
2. Install a supported Python 3 runtime and the dependency in `requirements.txt` (Flask). Record versions.
3. Copy the project to a dedicated directory on the Pi and enter that directory before using the profile switcher or starting processes.
4. Check the actual default gateway/subnet on the Pi and update the appropriate `profiles/*.py` values and targets. Do not assume the example gateway values fit the current network.
5. In that profile, add the known device MAC addresses to `KNOWN_DEVICE_MACS` and configure authorized `WATCHED_PORTS` targets. Until the trusted list is populated, discovered devices are treated as unregistered.
6. If using Telegram, configure `NETWATCH_BOT_TOKEN` and `NETWATCH_CHAT_ID` through the Pi's protected environment. Never store the token in source or report screenshots.

## Start and verify

- Start the monitor with `python monitor.py`; use `python monitor.py --once` for one collection round.
- Start the dashboard with `python app.py` in a second terminal.
- Open `http://<pi-address>:5000` from an authorized device on the same private network.
- Confirm the API returns current readings, then restart the application and confirm persisted history remains.
- Keep access on the local/private network. The dashboard has no visible login/authentication layer; do not publish it through public port forwarding.
- For laptop-to-Pi access, connect both devices to the same local Wi-Fi/hotspot, check the Pi's current IP, then open the dashboard using `http://<pi-address>:5000`. A hotspot that blocks connections between its clients will need another available local network.
- For offline software scenarios, run `python simulate.py HIGH_LATENCY` (or another mode) on the laptop. Each scenario is stored in its own `netwatch_simulation_<scenario>.db`, separate from the live database. To view it, set `NETWATCH_DB_PATH` to that file before starting `app.py`. Do not report simulation rows as field measurements.

## Record for the report

Capture the actual Pi model/OS, Python and Flask versions, network topology, selected profile/targets, database location, startup steps, access method, test date, dashboard screenshot, and logs. Do not fill in values until observed on the device.
