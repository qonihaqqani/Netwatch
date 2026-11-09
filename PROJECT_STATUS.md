# NetWatch Project Status

Updated: 10 November 2026

## Project baseline

**Title:** End User Network Monitoring System for Small Scale Network
**Target platform:** Raspberry Pi 3 Model B+ (deployment not yet verified)
**Current implementation:** Python monitor, Flask dashboard, SQLite, ping checks, ARP-cache device listing, TCP port checks, threshold alerts, optional Telegram path.

## Verified in this audit

- All project Python files passed AST syntax parsing.
- Flask page and `/api/status` worked with a temporary test database.
- SQLite readings, device scan, port status, alert history, and latency history were readable after writes/reopen.
- Mocked host-down and recovery transition recorded alert and resolution rows without network calls.
- Existing scenario script ran on the Windows development host: Google DNS and Cloudflare DNS replied; configured campus gateway did not; ARP returned one local neighbor. These are not Raspberry Pi results.

## Not verified yet

- Runtime on Raspberry Pi 3 Model B+.
- End-to-end monitoring on the intended small LAN.
- Unknown-device detection and port-change detection.
- Telegram notification delivery.
- Scenario B controlled abnormal condition, dashboard update timing, detection success rate, false alerts, or usability.
- Current official report format.

See `TEST_RESULTS.md`, `TEST_PLAN.md`, and `KNOWN_LIMITATIONS.md` for details. The consolidated initial audit is in the task outputs folder.

## Priority next steps

1. Confirm final report template and scenario definitions with the current UiTM/supervisor requirements.
2. Implement or narrow the proposal requirements for device baseline/unknown-device and port-status change detection.
3. Add repeatable automated tests for monitoring decisions, API output, and database behavior.
4. Run the system on the Pi in a controlled LAN and collect genuine evidence.

Additional audit check: a one-shot monitor cycle ran successfully on the Windows development host and persisted measurements plus a host-down alert. Raspberry Pi deployment and Telegram delivery remain unverified.
