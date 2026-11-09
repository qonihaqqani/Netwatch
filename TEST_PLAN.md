# NetWatch Test Plan

Tests must distinguish real measurements from mocked/unit inputs. Record platform, network/profile, time, targets, configuration, expected result, actual result, and evidence file for each run. Do not represent Windows-host results as Raspberry Pi results.

| ID | Test | Type | Current status |
|---|---|---|---|
| TP01 | Python syntax check | Static | Passed 10 Nov 2026 |
| TP02 | Scenario A ping checks for configured targets | Live network | Preliminary Windows-host run; gateway failed, public DNS targets replied. Repeat on Pi and correct profile first. |
| TP03 | ARP neighbor parsing | Live local network | One neighbor listed on Windows host; not a subnet-wide discovery test. |
| TP04 | Dashboard page and `/api/status` response | Isolated integration | Passed with temporary test database. |
| TP05 | SQLite readings, scans, ports, alerts, and history persistence | Isolated integration | Passed with temporary test database. |
| TP06 | Host-down alert and recovery | Mocked unit check | Passed; no network/Telegram activity. |
| TP07 | High latency and packet-loss threshold transitions | Automated/simulated | Passed offline through `tests/test_core.py`; field validation pending. |
| TP08 | Unknown-device detection from a registered baseline | Automated/simulated | Detection implemented; automated check passed. Populate trusted MAC list and validate on Pi. |
| TP09 | Selected port-status change detection | Automated/simulated | Implemented using previous saved status; automated check passed. Validate against a real authorized service. |
| TP10 | Telegram end-to-end message receipt | Integration | Pending; no credentials configured for audit. |
| TP11 | Scenario A on Raspberry Pi in intended LAN | Field | Pending. |
| TP12 | Scenario B controlled fault on Raspberry Pi | Field | Pending; do not use attack traffic outside an isolated, authorized lab. |
| TP13 | Restart persistence and recovery behavior | Integration | Database reads after close/reopen passed in temporary check; full application restart test pending. |
| TP14 | Dashboard usability feedback | User evaluation | Pending; requires approved participants/questionnaire process. |
| TP15 | Six controlled modes (`NORMAL`, `HIGH_LATENCY`, `PACKET_LOSS`, `HOST_DOWN`, `UNKNOWN_DEVICE`, `PORT_CHANGE`) | Offline simulation | Implemented; exercised on Windows. Results are labelled and use a separate database by default. |

## Metric definitions to finalize

- Monitoring accuracy: compare each observed status/result against a stated reference measurement and report sample counts.
- Dashboard update time: timestamp difference from stored measurement to visible API/dashboard update; define sampling and repetitions.
- Detection time: time from controlled fault activation to recorded/detected state.
- Telegram delivery time: detection to actual receipt on the device; API acceptance time is a separate metric.
- False-alert observation: count inappropriate alerts during the stated normal-condition window.
- Usability: report the approved questionnaire method and participant count, if retained in final scope.
