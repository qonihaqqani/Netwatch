# NetWatch Test Results

Updated: 10 November 2026

## Offline regression run — 10 November 2026

Command: `py -m unittest discover -s tests -v`

Result: **11 tests passed.** Checks cover SQLite history, device/port snapshots, legacy database migration, host and port alert edges, port transitions, unregistered device detection, all six simulation modes, simulation origin and Telegram suppression, `/api/status` output, and the controlled-fault script's persistence/recovery path with mocked inputs.

Command: `py -m compileall -q .`

Result: completed with no syntax errors.

These are offline Windows development-host checks. They do not establish Raspberry Pi compatibility, field detection accuracy, network access, Telegram delivery, or user usability.

## Preliminary development-host run

Existing `test_scenarios.py` was run from an isolated copy of the source on the Windows development host using the `campus` profile.

| Check | Actual result | Interpretation |
|---|---|---|
| Campus gateway `10.0.0.1` | No reply; 100% loss | Failed this run. Profile may not match the active network; repeat after checking the actual gateway. |
| Google DNS `8.8.8.8` | 61.0 ms; 0% loss | Passed the script's loss threshold for this sample. |
| Cloudflare DNS `1.1.1.1` | 93.0 ms; 0% loss | Passed the script's loss threshold for this sample. |
| ARP neighbor listing | One IP/MAC entry, no hostname | Confirms one cached neighbor was parsed; it does not establish complete device discovery. |

These are observations from one Windows-host run. They are not Pi deployment results, do not establish a network baseline, and should not be used as project-wide performance claims.

## Isolated checks

| Check | Result | Notes |
|---|---|---|
| Python AST syntax parsing | Passed | All Python modules in the project snapshot parsed. |
| Flask `/` route | Passed | HTTP 200 and dashboard HTML contained the NetWatch title using Flask's test client. |
| Flask `/api/status` | Passed | Returned seeded targets, device scan, port result, alert, and threshold data. |
| SQLite persistence/history | Passed | Test rows remained readable after writes; target history returned the expected row. |
| Host-down/recovery alert transition | Passed | Mocked ping inputs produced one host-down row and one resolution row; Telegram disabled. |

## Outstanding

No Raspberry Pi run, Telegram receipt, unknown-device test, port-change test, full restart test, normal-condition observation window, Scenario B field run, or usability study has been completed.

## Monitor one-shot integration run

`python monitor.py --once` was run from the isolated source copy with Telegram environment variables cleared. This exercised the monitor against the same Windows-host `campus` profile.

- Campus gateway: down, 100% loss; a `host_down` alert was written to SQLite.
- Google DNS: up, 62 ms, 0% loss.
- Cloudflare DNS: up, 37 ms, 0% loss.
- Device scan: one neighbor parsed; hostname unavailable.
- Port checks: none, because `WATCHED_PORTS` is empty in the active profile.
- Telegram: not configured; alert delivery was not tested.

The run confirms one collection cycle and alert persistence on the development host. It does not verify Pi deployment or complete device discovery.
