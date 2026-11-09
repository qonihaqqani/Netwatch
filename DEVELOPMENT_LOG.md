# NetWatch Development Log

## 10 November 2026 — Controlled scenario implementation

- Added profile-specific trusted MAC lists, unregistered-device labels/alerts, and alerts when a saved TCP-port state changes.
- Added six offline modes: `NORMAL`, `HIGH_LATENCY`, `PACKET_LOSS`, `HOST_DOWN`, `UNKNOWN_DEVICE`, and `PORT_CHANGE`.
- Simulated events use the same persistence and detection functions, a separate per-scenario database by default, explicit simulation labels, and never send Telegram messages.
- Added additive SQLite `source`-column migrations to preserve existing data.
- Added eleven offline regression checks. `py -m unittest discover -s tests -v` passed all 11; `py -m compileall -q .` completed successfully.
- Pi deployment, field tests, Telegram delivery, and usability evaluation remain pending.

## 10 November 2026 — Initial audit

- Read the project source, corrected proposal, FYP1 Chapters 1–3 report, old UiTM format guide, completed example report, and 2025 anchor paper.
- Confirmed the source snapshot is smaller than the handover's historical description: one Flask dashboard, one monitor, SQLite, three profiles, and a live-network scenario script.
- Parsed all Python files successfully.
- Ran the existing `test_scenarios.py` from an isolated copy. Campus gateway (`10.0.0.1`) did not reply; Google DNS reported 61 ms / 0% loss; Cloudflare DNS reported 93 ms / 0% loss; ARP returned one neighbor. This run was on the Windows development host, not the Pi.
- Ran temporary isolated checks: dashboard route/API, SQLite persistence/history, and mocked down/recovery alerts passed. No Telegram credentials or network calls were used in the mocked test.
- No production code was changed during this audit. No live Pi tests or Telegram delivery tests were performed.
- Ran `python monitor.py --once` on the Windows-host campus profile from an isolated copy with Telegram disabled: the configured gateway was down, both DNS targets were up, one ARP neighbor was listed, and the down alert persisted in SQLite. No ports were checked because the profile has no watched ports.
