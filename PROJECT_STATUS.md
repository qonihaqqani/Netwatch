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
- Pi validation of the new unknown-device and port-change features.
- Telegram notification delivery.
- Scenario B controlled abnormal condition, dashboard update timing, detection success rate, false alerts, or usability.
- Current official report format.

See `TEST_RESULTS.md`, `TEST_PLAN.md`, and `KNOWN_LIMITATIONS.md` for details. The consolidated initial audit is in the task outputs folder.

## Development update: controlled scenarios

- Added profile-specific trusted MAC lists and registration status in device snapshots; newly observed unregistered devices generate an alert.
- Added edge detection for changes to a monitored TCP port.
- Added offline `NORMAL`, `HIGH_LATENCY`, `PACKET_LOSS`, `HOST_DOWN`, `UNKNOWN_DEVICE`, and `PORT_CHANGE` scenarios. They use the application's recording/alert pathways, save to separate per-scenario databases by default, display a SIMULATED label, and suppress Telegram sends.
- Added an additive SQLite migration for a `source` column so pre-existing databases remain readable and records identify live or simulated origin.
- Added an offline test suite. Eleven checks passed, including migration, alert transitions, all six scenarios, simulation labeling, and `/api/status`.

These changes have not been deployed to the Raspberry Pi. Genuine Scenario A/B results, Telegram delivery, network-specific trusted MAC baselines, and usability evaluation remain outstanding.

## Priority next steps

1. Deploy this version to the approved Pi 3 Model B+ and verify dashboard access from the laptop.
2. Set trusted MAC addresses and watched ports for an authorized local network.
3. Execute and record Scenario A and Scenario B real-world runs, clearly separating simulation results.
4. Test Telegram delivery and collect usability feedback if required by the confirmed supervisor methodology.
5. Update Chapters 3–5 using actual test evidence and the current official template.

Additional audit check: a one-shot monitor cycle ran successfully on the Windows development host and persisted measurements plus a host-down alert. Raspberry Pi deployment and Telegram delivery remain unverified.
