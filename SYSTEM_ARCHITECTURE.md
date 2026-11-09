# NetWatch System Architecture

## Implemented source structure

- `monitor.py`: polling loop for ping measurements, configured TCP connect checks, ARP-cache parsing, and threshold alert decisions.
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

The monitor and Flask app are separate processes. SQLite stores observations in `readings`, `alerts`, `device_scans`, and `port_checks`. No `monitoring_cycles` table is present in the current schema.

## Important boundaries

ARP parsing reads entries already known to the operating system; it is not a complete active subnet scan. The code has no login/authentication route. The diagram describes the current source snapshot and must be revised if implementation changes.
