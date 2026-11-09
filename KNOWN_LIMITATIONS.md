# Known Limitations and Risks

## Verified in current source

- ARP-based device listing depends on the local neighbor cache and may omit devices.
- Campus/hotspot/PdaNet profile values may not match a particular current network.
- `WATCHED_PORTS` is empty in all three supplied profiles, so port checks do not run until configured.
- No registered-device comparison exists; unknown devices are not detected.
- Port logic checks whether configured TCP ports are open and alerts if an expected port is closed; it does not detect arbitrary port changes.
- Alert-active state is in memory and resets when the monitor restarts.
- The dashboard binds to all interfaces and has no visible authentication; it must stay on a trusted/private network.
- Telegram delivery is best-effort and not yet verified. API acceptance latency is not phone receipt latency.
- Existing live tests use actual network conditions and can produce results that vary by network and time.

## Not verified / environment-dependent

- Pi 3 Model B+ performance, OS compatibility, wireless conditions, and long-running reliability.
- Campus client isolation and ICMP/ARP policy on the student's target network.
- Exact thresholds appropriate to the final test LAN.
- Current official report format and final supervisor approval of the test scenarios.
