# NetWatch System Architecture

## Implemented source structure

- `monitor.py`: polling loop for ping measurements, configured TCP connect checks, ARP-cache parsing, and threshold alert decisions.
- `simulate.py`: offline controlled scenarios that use the monitor's persistence and alert functions; synthetic records use a dedicated database by default.
- `config.py` and `profiles/*.py`: global intervals/thresholds plus selected network target and port settings.
- `db.py`: SQLite schema and access functions.
- `app.py`: Flask page and JSON status endpoint.
- `templates/index.html`: single-page dashboard refreshed by browser JavaScript.
- `switch_network.py`: selects the active profile via a text file.

## Data flow

```text
Configured targets ──> monitor.py ──> ping / TCP connect / local ARP cache
                                  ├──> SQLite readings, device_scans, port_checks
                                  └──> threshold decision ──> SQLite alerts ──> optional Telegram API

Browser ──> Flask `/` and `/api/status` ──> SQLite latest values/history ──> dashboard tables and latency sparkline
```

The monitor and Flask app are separate processes. SQLite stores observations in `readings`, `alerts`, `device_scans`, and `port_checks`, including a `source` value to distinguish live and simulated records. No `monitoring_cycles` table is present in the current schema. Simulations use a separate SQLite file unless `NETWATCH_DB_PATH` is overridden.

## Important boundaries

ARP parsing reads entries already known to the operating system; it is not a complete active subnet scan. Unknown-device alerts compare observed MAC addresses to the active profile's trusted list. Port-change alerts compare the latest state with the prior saved state. The code has no login/authentication route. Keep the dashboard on a trusted/private network.
